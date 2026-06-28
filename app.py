"""
Print Queue Automation - Bambu Lab Cloud
Web UI to queue .gcode files with automatic ejection + next print.
Runs on Railway — accessible from anywhere.
"""

import os
import time
import threading
import hashlib
from pathlib import Path
from functools import wraps
from flask import Flask, request, jsonify, render_template_string, send_from_directory, session, redirect, url_for
from dotenv import load_dotenv
from bambu import BambuCloud

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "pq_secret_x9z2k")
UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

SITE_PASSWORD = "Leonardo Carlo Manzone"

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated

# ── Global state ──────────────────────────────────────────────────────────────

printer: BambuCloud | None = None
queue: list[dict] = []
current_job: dict | None = None
automation_thread: threading.Thread | None = None
log_messages: list[str] = []
running = False

COOLDOWN_SECONDS = 300
PLATE_X = 256.0   # Bambu A1

def auto_connect():
    """Connect to Bambu cloud. Uses BAMBU_TOKEN+BAMBU_UID if set, else email/password."""
    global printer
    serial = os.getenv("BAMBU_SERIAL", "")
    if not serial:
        log("BAMBU_SERIAL mancante nelle variabili d'ambiente")
        return
    try:
        token = os.getenv("BAMBU_TOKEN", "")
        uid = os.getenv("BAMBU_UID", "")
        if token and uid:
            # Direct token — no login needed (avoids 403 from cloud IP)
            p = BambuCloud("", "", serial, token=token, uid=uid)
            p.connect_mqtt()
            printer = p
            log("Connesso al cloud Bambu (token diretto)")
            return

        # Fallback: email/password login
        email = os.getenv("BAMBU_EMAIL", "")
        password = os.getenv("BAMBU_PASSWORD", "")
        if not (email and password):
            log("Mancano credenziali — imposta BAMBU_TOKEN+BAMBU_UID oppure BAMBU_EMAIL+BAMBU_PASSWORD")
            return
        p = BambuCloud(email, password, serial)
        ok, err = p.login()
        if ok:
            p.connect_mqtt()
            printer = p
            log("Connesso al cloud Bambu (email/password)")
        else:
            log(f"Auto-connessione fallita: {err}")
    except Exception as e:
        log(f"Auto-connessione errore: {e}")
PLATE_Y = 256.0
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")  # set this on Railway


def log(msg: str):
    ts = time.strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    log_messages.append(entry)
    if len(log_messages) > 200:
        log_messages.pop(0)
    print(entry)


# ── Automation loop ───────────────────────────────────────────────────────────

def automation_loop():
    global current_job, running
    log("Automazione avviata")
    while running:
        if not printer or not queue:
            time.sleep(3)
            continue

        job = next((j for j in queue if j["status"] == "queued"), None)
        if not job:
            time.sleep(3)
            continue

        # Step 1: inject eject G-code
        job["status"] = "preparing"
        log(f"Preparazione: {job['name']}")
        piece_h = BambuCloud.extract_piece_height(job["path"])
        modified_path = BambuCloud.inject_eject_gcode(
            job["path"],
            plate_x_mm=PLATE_X,
            plate_y_mm=PLATE_Y,
            cooldown_seconds=COOLDOWN_SECONDS,
            piece_height_mm=piece_h,
        )
        log(f"Altezza pezzo: {piece_h:.1f}mm | G-code modificato")

        # Step 2: build URL — printer will download the file from our server
        filename = Path(modified_path).name
        gcode_url = f"{BASE_URL}/files/{filename}"
        job["status"] = "printing"
        current_job = job
        log(f"Avvio stampa: {job['name']} → {gcode_url}")
        printer.start_print_from_url(gcode_url)

        # Step 3: wait for finish
        while running:
            st = printer.get_status()
            state = st.get("gcode_state", "").lower()
            if state in ("finish", "failed", "idle"):
                break
            prog = st.get("mc_percent", 0)
            rem = st.get("mc_remaining_time", 0)
            log(f"Stampa... {prog}% | ~{rem} min | stato={state}")
            time.sleep(15)

        st = printer.get_status()
        final = st.get("gcode_state", "").lower()
        if final == "failed":
            job["status"] = "error"
            log(f"Stampa FALLITA: {job['name']}")
        else:
            job["status"] = "done"
            log(f"Stampa completata: {job['name']} — sequenza espulsione in corso")
            log(f"Attendo fine espulsione ({COOLDOWN_SECONDS + 60}s)...")
            time.sleep(COOLDOWN_SECONDS + 60)
            log("Espulsione completata. Prossimo pezzo.")

        current_job = None
        time.sleep(2)

    log("Automazione fermata")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET"])
def login_page():
    return render_template_string(LOGIN_TEMPLATE)

@app.route("/login", methods=["POST"])
def do_login():
    pw = request.form.get("password", "")
    if pw == SITE_PASSWORD:
        session["logged_in"] = True
        return redirect(url_for("index"))
    return render_template_string(LOGIN_TEMPLATE, error="Password errata")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))

@app.route("/")
@login_required
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/files/<filename>")
@login_required
def serve_gcode(filename):
    """Printer downloads the gcode file from here."""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/api/connect", methods=["POST"])
@login_required
def connect():
    global printer
    data = request.json
    email = data.get("email") or os.getenv("BAMBU_EMAIL", "")
    password = data.get("password") or os.getenv("BAMBU_PASSWORD", "")
    serial = data.get("serial") or os.getenv("BAMBU_SERIAL", "")
    if not (email and password and serial):
        return jsonify({"ok": False, "error": "Email, password e serial richiesti"}), 400
    try:
        p = BambuCloud(email, password, serial)
        ok, err = p.login()
        if not ok:
            return jsonify({"ok": False, "error": f"Login fallito: {err}"})
        p.connect_mqtt()
        printer = p
        log(f"Connesso al cloud Bambu — serial: {serial}")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/status")
@login_required
def status():
    st = printer.get_status() if printer else {}
    return jsonify({
        "connected": printer is not None and printer.connected,
        "running": running,
        "printer": st,
        "queue": queue,
        "current": current_job,
        "logs": log_messages[-50:],
        "cooldown": COOLDOWN_SECONDS,
    })

@app.route("/api/upload", methods=["POST"])
@login_required
def upload():
    log(f"Upload request: files={list(request.files.keys())}")

    # Accetta sia 'file' che 'files' per compatibilità
    files = request.files.getlist("file") or request.files.getlist("files")
    log(f"Parsed files: {len(files)} file(s)")

    if not files:
        return jsonify({"ok": False, "error": "Nessun file"}), 400

    added = []
    cooldown = int(request.form.get("cooldown", 300))

    for f in files:
        log(f"Processing: {f.filename}")
        if not f.filename.endswith(".gcode"):
            log(f"Skipped (not .gcode): {f.filename}")
            continue

        dest = UPLOAD_FOLDER / f.filename
        try:
            f.save(str(dest))
            log(f"Saved to: {dest}")

            # Estrai altezza pezzo e inietta sequenza eiezione
            piece_h = BambuCloud.extract_piece_height(str(dest))
            log(f"Piece height detected: {piece_h}mm")

            eject_gcode_path = BambuCloud.inject_eject_gcode(
                str(dest),
                plate_x_mm=256.0,
                plate_y_mm=256.0,
                cooldown_seconds=cooldown,
                piece_height_mm=piece_h
            )
            log(f"Eject gcode generated: {eject_gcode_path}")

            # Usa il file con eiezione come file principale
            queue.append({"name": f.filename, "path": eject_gcode_path, "status": "queued"})
            added.append(f.filename)
            log(f"Aggiunto in coda (con eiezione): {f.filename}")
        except Exception as e:
            log(f"ERROR processing {f.filename}: {e}")
            return jsonify({"ok": False, "error": f"Processing error: {e}"}), 500

    return jsonify({"ok": True, "added": added})

@app.route("/api/remove", methods=["POST"])
@login_required
def remove():
    name = request.json.get("name")
    for j in queue:
        if j["name"] == name and j["status"] == "queued":
            queue.remove(j)
            log(f"Rimosso: {name}")
            return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Job non trovato o in corso"})

@app.route("/api/start", methods=["POST"])
@login_required
def start_auto():
    global automation_thread, running
    if running:
        return jsonify({"ok": False, "error": "Già in esecuzione"})
    if not printer:
        return jsonify({"ok": False, "error": "Stampante non connessa"})
    running = True
    automation_thread = threading.Thread(target=automation_loop, daemon=True)
    automation_thread.start()
    return jsonify({"ok": True})

@app.route("/api/stop", methods=["POST"])
@login_required
def stop_auto():
    global running
    running = False
    log("Stop richiesto")
    return jsonify({"ok": True})

@app.route("/api/cooldown", methods=["POST"])
@login_required
def set_cooldown():
    global COOLDOWN_SECONDS
    COOLDOWN_SECONDS = max(30, min(int(request.json.get("seconds", 300)), 3600))
    log(f"Raffreddamento: {COOLDOWN_SECONDS}s")
    return jsonify({"ok": True, "seconds": COOLDOWN_SECONDS})

@app.route("/api/eject", methods=["POST"])
@login_required
def manual_eject():
    if not printer:
        return jsonify({"ok": False, "error": "Non connesso"})
    # Auto-detect height from last done/printing job, fallback to 10mm
    h = 10.0
    for j in reversed(queue):
        if j["status"] in ("done", "printing", "preparing"):
            h = BambuCloud.extract_piece_height(j["path"])
            break
    cx = PLATE_X / 2
    by = PLATE_Y - 2
    pz = max(h - 2, 1)
    printer.send_gcode([
        "G28 Z", "G1 Z15 F600",
        f"G1 X{cx} Y{by} F6000",
        f"G1 Z{pz} F300",
        f"G1 Y2 F300",
        f"G1 Y{by} F6000",
        "G28 X Y",
    ])
    log(f"Espulsione manuale inviata (altezza rilevata: {h:.1f}mm)")
    return jsonify({"ok": True})


@app.route("/api/ams")
@login_required
def get_ams():
    """Return AMS filament slots from printer status."""
    if not printer:
        return jsonify({"ok": False, "slots": []})
    st = printer.get_status()
    slots = []
    ams_data = st.get("ams", {})
    ams_list = ams_data.get("ams", []) if isinstance(ams_data, dict) else []
    for ams_unit in ams_list:
        for tray in ams_unit.get("tray", []):
            slots.append({
                "id": tray.get("id", ""),
                "color": "#" + tray.get("tray_color", "FFFFFF")[:6],
                "material": tray.get("tray_type", "PLA"),
                "name": tray.get("tray_sub_brands", tray.get("tray_type", "PLA")),
            })
    # Also check single-color (no AMS)
    if not slots:
        slots.append({"id": "0", "color": "#FF8000", "material": "PLA", "name": "Filamento caricato"})
    return jsonify({"ok": True, "slots": slots})




# ── HTML ──────────────────────────────────────────────────────────────────────

LOGIN_TEMPLATE = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Print Queue — Accesso</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',system-ui,sans-serif;background:#0f0f0f;color:#e0e0e0;min-height:100vh;display:flex;align-items:center;justify-content:center}
.box{background:#1a1a1a;border:1px solid #272727;border-radius:14px;padding:36px 32px;width:100%;max-width:340px}
h1{font-size:1rem;font-weight:600;color:#fff;margin-bottom:6px}
p{font-size:.78rem;color:#555;margin-bottom:24px}
label{display:block;font-size:.75rem;color:#777;margin-bottom:5px}
input[type=password]{width:100%;background:#111;border:1px solid #2e2e2e;border-radius:7px;padding:10px 12px;color:#ddd;font-size:.9rem;outline:none;margin-bottom:14px}
input:focus{border-color:#4f8ef7}
button{width:100%;padding:10px;background:#4f8ef7;color:#fff;border:none;border-radius:7px;font-size:.88rem;font-weight:500;cursor:pointer}
button:hover{background:#3a7ae0}
.err{background:#450a0a;color:#f87171;border-radius:6px;padding:8px 12px;font-size:.78rem;margin-bottom:14px}
</style>
</head>
<body>
<div class="box">
  <h1>Print Queue</h1>
  <p>Inserisci la password per accedere</p>
  {% if error %}<div class="err">{{ error }}</div>{% endif %}
  <form method="POST" action="/login">
    <label>Password</label>
    <input type="password" name="password" placeholder="••••••••••••••••" autofocus>
    <button type="submit">Entra</button>
  </form>
</div>
</body>
</html>"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Print Queue</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',system-ui,sans-serif;background:#0f0f0f;color:#e0e0e0;padding:20px;min-height:100vh}
h1{font-size:1.2rem;font-weight:600;color:#fff;margin-bottom:20px}
.grid{display:grid;grid-template-columns:290px 1fr;gap:14px;max-width:1060px}
@media(max-width:700px){.grid{grid-template-columns:1fr}}
.card{background:#1a1a1a;border:1px solid #272727;border-radius:11px;padding:16px;margin-bottom:14px}
.card h2{font-size:.7rem;text-transform:uppercase;letter-spacing:1px;color:#555;margin-bottom:12px}
label{display:block;font-size:.75rem;color:#777;margin:10px 0 3px}
input[type=text],input[type=password],input[type=number],input[type=email]{width:100%;background:#111;border:1px solid #2e2e2e;border-radius:6px;padding:7px 9px;color:#ddd;font-size:.82rem;outline:none}
input:focus{border-color:#4f8ef7}
button{width:100%;margin-top:8px;padding:8px;border:none;border-radius:7px;font-size:.82rem;font-weight:500;cursor:pointer;transition:.15s}
.p{background:#4f8ef7;color:#fff}.p:hover{background:#3a7ae0}
.g{background:#22c55e;color:#fff}.g:hover{background:#16a34a}
.r{background:#ef4444;color:#fff}.r:hover{background:#dc2626}
.q{background:#232323;color:#aaa}.q:hover{background:#2a2a2a}
.badge{display:inline-block;padding:2px 7px;border-radius:20px;font-size:.67rem;font-weight:600}
.bq{background:#1e3a5f;color:#60a5fa}.bp{background:#14532d;color:#4ade80}
.bd{background:#1a1a1a;color:#444;border:1px solid #2a2a2a}.be{background:#450a0a;color:#f87171}
.bpr{background:#292303;color:#fbbf24}.bu{background:#1c1c38;color:#818cf8}
.qi{display:flex;align-items:center;justify-content:space-between;padding:7px 9px;border-radius:6px;margin-bottom:5px;background:#111;border:1px solid #1e1e1e}
.qi span{font-size:.78rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:155px}
.dz{border:2px dashed #2a2a2a;border-radius:9px;padding:22px;text-align:center;cursor:pointer;transition:.15s;margin-bottom:10px}
.dz:hover,.dz.ov{border-color:#4f8ef7;background:#131c2e}
.dz p{font-size:.75rem;color:#444}
.dz input{display:none}
.log{background:#090909;border:1px solid #1e1e1e;border-radius:7px;height:240px;overflow-y:auto;padding:9px;font-size:.7rem;font-family:monospace;color:#666}
.log p{margin-bottom:2px;line-height:1.5}
.log p:last-child{color:#bbb}
.bar{height:3px;background:#1e1e1e;border-radius:2px;margin-top:7px;overflow:hidden}
.fill{height:100%;background:#4f8ef7;border-radius:2px;transition:width .5s}
.row{display:flex;gap:8px;margin-top:8px}
.row button{margin:0}
.dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:5px}
.dg{background:#22c55e}.dr{background:#ef4444}
</style>
</head>
<body>
<h1>Print Queue — Bambu Lab</h1>
<div class="grid">
<div>
  <div class="card">
    <h2>Stampante</h2>
    <div id="cs" style="font-size:.82rem;color:#555;padding:4px 0">Controllo connessione...</div>
  </div>
  <div class="card">
    <h2>Impostazioni</h2>
    <label>Raffreddamento (secondi)</label>
    <input id="cool" type="number" value="300" min="30" max="3600">
    <button class="q" onclick="saveCool()">Salva</button>
    <button class="q" onclick="eject()" style="margin-top:10px">Test espulsione manuale</button>
  </div>
  <div class="card">
    <h2>Stato Stampante</h2>
    <div id="pi" style="font-size:.75rem;color:#555">—</div>
    <div class="bar"><div class="fill" id="prog" style="width:0%"></div></div>
  </div>
</div>
<div>
  <!-- Upload gcode -->
  <div class="card">
    <h2>Aggiungi alla Coda</h2>
    <p style="font-size:.78rem;color:#aaa;margin-bottom:12px">
      📄 <strong>Carica file .gcode</strong> generati con <code>upload_gcode.py</code> sul tuo PC<br>
      STL/OBJ/3MF si sliciano localmente, poi si uploadano qui.
    </p>
    <div class="dz" id="dz" onclick="document.getElementById('fi').click()">
      <p>Trascina file .gcode qui<br>oppure clicca per scegliere</p>
      <input id="fi" type="file" accept=".gcode" multiple onchange="uploadGcode(this.files)">
    </div>

    <div id="ql" style="margin-top:10px"></div>
    <div class="row" style="margin-top:10px">
      <button class="g" onclick="startAuto()">▶ Avvia</button>
      <button class="r" onclick="stopAuto()">■ Stop</button>
    </div>
  </div>
  <div class="card">
    <h2>Log</h2>
    <div class="log" id="lb"></div>
  </div>
</div>
</div>
<script>
const dz=document.getElementById('dz');
dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('ov')});
dz.addEventListener('dragleave',()=>dz.classList.remove('ov'));
dz.addEventListener('drop',e=>{e.preventDefault();dz.classList.remove('ov');uploadGcode(e.dataTransfer.files)});

async function post(url,body){return fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json())}

async function uploadGcode(files){
  const fd=new FormData();
  for(const f of files)if(f.name.endsWith('.gcode'))fd.append('file',f);
  const r=await fetch('/api/upload',{method:'POST',body:fd});
  const d=await r.json();
  if(!d.ok)alert(d.error);
  refresh();
}
async function startAuto(){const d=await post('/api/start',{});if(!d.ok)alert(d.error);else refresh()}
async function stopAuto(){await post('/api/stop',{});refresh()}
async function saveCool(){await post('/api/cooldown',{seconds:parseInt(document.getElementById('cool').value)})}
async function eject(){
  const d=await post('/api/eject',{});
  if(!d.ok)alert(d.error);
}

// ── STL / Slicing ──
let selectedStlFile = null;
let selectedColor = '#FF8000';


async function loadAmsSlots(){
  const r = await fetch('/api/ams');
  const d = await r.json();
  const box = document.getElementById('ams-slots');
  box.innerHTML = '';
  for(const s of d.slots){
    const btn = document.createElement('div');
    btn.title = s.material + ' — ' + s.name;
    btn.style.cssText = `width:32px;height:32px;border-radius:50%;background:${s.color};cursor:pointer;border:3px solid transparent;transition:.15s`;
    btn.onclick = () => {
      document.querySelectorAll('#ams-slots div').forEach(b=>b.style.borderColor='transparent');
      btn.style.borderColor='#fff';
      selectedColor = s.color;
    };
    // Select first by default
    if(!box.children.length){ btn.style.borderColor='#fff'; selectedColor=s.color; }
    box.appendChild(btn);
  }
}

function selectStl(file){
  if(!file) return;
  selectedStlFile = file;
  document.getElementById('stl-settings').style.display='';
  document.getElementById('stl-name').textContent = '📄 ' + file.name;
  loadAmsSlots();
}

async function sliceAndQueue(){
  if(!selectedStlFile){ alert('Seleziona prima un file STL'); return; }
  const fd = new FormData();
  fd.append('file', selectedStlFile);
  fd.append('layer_height', document.getElementById('sl-layer').value);
  fd.append('infill', document.getElementById('sl-infill').value);
  fd.append('supports', document.getElementById('sl-supports').value);
  fd.append('color', selectedColor);
  document.getElementById('slice-btn').disabled = true;
  document.getElementById('slice-msg').style.display = '';
  const r = await fetch('/api/slice', {method:'POST', body:fd});
  const d = await r.json();
  if(!d.ok){ alert(d.error); }
  document.getElementById('slice-btn').disabled = false;
  refresh();
}
async function removeJob(n){await post('/api/remove',{name:n});refresh()}

async function refresh(){
  const d=await fetch('/api/status').then(r=>r.json());
  document.getElementById('cs').innerHTML=d.connected
    ?'<span class="dot dg"></span>Connesso'
    :'<span class="dot dr"></span>Non connesso';
  const p=d.printer;
  let info='—';
  if(d.connected&&Object.keys(p).length){
    const prog=p.mc_percent||0;
    document.getElementById('prog').style.width=prog+'%';
    info=`<b>${p.gcode_state||'—'}</b> | Estrusore: ${(p.nozzle_temper||0).toFixed(0)}°C | Piatto: ${(p.bed_temper||0).toFixed(0)}°C | ${prog}% | ~${p.mc_remaining_time||0} min`;
  }
  document.getElementById('pi').innerHTML=info;
  const ql=document.getElementById('ql');
  ql.innerHTML=d.queue.length
    ?d.queue.map(j=>`<div class="qi"><span title="${j.name}">${j.name}</span><div style="display:flex;gap:5px;align-items:center"><span class="badge b${j.status[0]}">${j.status}</span>${j.status==='queued'?`<button onclick="removeJob('${j.name}')" style="background:none;border:none;color:#444;cursor:pointer;font-size:.8rem;margin:0;width:auto;padding:0 2px">✕</button>`:''}</div></div>`).join('')
    :'<p style="font-size:.75rem;color:#333;text-align:center;padding:10px">Nessun file in coda</p>';
  const lb=document.getElementById('lb');
  lb.innerHTML=d.logs.map(l=>`<p>${l}</p>`).join('');
  lb.scrollTop=lb.scrollHeight;
  document.getElementById('cool').value=d.cooldown;
}
setInterval(refresh,5000);
refresh();
</script>
</body>
</html>"""

auto_connect()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"\n  Print Queue → http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
