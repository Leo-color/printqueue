# 🖨️ Print Queue Automation — Bambu Lab A1

Sistema automatico di stampa continua con **eiezione automatica** per Bambu Lab A1. Accedi da **qualsiasi luogo** tramite cloud Bambu.

---

## 🚀 Funzionalità

✅ **Coda stampa automatica** — Carica file `.gcode`, il sistema stampa uno per uno  
✅ **Eiezione automatica** — Il pezzo cade dal piatto dopo il print (nessun intervento manuale)  
✅ **Selezione colore** — Scegli il filamento prima di stampare  
✅ **Stampa continua** — Loop automatico finché non finiscono i file  
✅ **Controllo da web** — Accedi da qualsiasi dispositivo, in qualsiasi luogo  
✅ **Monitoraggio real-time** — Stato stampante, temperature, tempo restante  
✅ **Pulsanti di emergenza** — Stop e Annulla stampa con eiezione forzata  

---

## 📋 Requisiti

- **Stampante:** Bambu Lab A1 (256×256mm bed)
- **Token Bambu:** Email/password account Bambu Lab
- **PrusaSlicer:** Locale (Bambu Studio o PrusaSlicer standalone)
- **Render.com account:** Hosting cloud (free tier)

---

## 🔧 Setup Iniziale

### 1️⃣ **Ottieni il Token Bambu**

```bash
python get_token.py
```

Inserisci:
- Email Bambu Lab
- Password Bambu Lab
- Codice 2FA (riceverai email)

Output: `BAMBU_TOKEN` e `BAMBU_UID`

### 2️⃣ **Configura `.env`**

```bash
BAMBU_TOKEN=xxx
BAMBU_UID=xxx
BAMBU_SERIAL=xxxxx  # Serial stampante (vedi etichetta A1)
BASE_URL=https://printqueue-yjfk.onrender.com
SECRET_KEY=Leonardo Carlo Manzone
```

### 3️⃣ **Deploy su Render**

```bash
git push origin main
```

Render farà il deploy automaticamente. Guarda lo stato su https://render.com

---

## 📖 Come Usare

### **Workflow Completo:**

```
1. Slicing Locale (PrusaSlicer)
   ↓
2. Carica .gcode sul sito
   ↓
3. Scegli colore filamento
   ↓
4. Clicca "▶ Stampa"
   ↓
5. Sistema stampa automaticamente
   ↓
6. Dopo print → Eiezione automatica
   ↓
7. Pezzo cade dal piatto
   ↓
8. Continua con prossimo file
```

### **Step 1: Genera G-code Localmente**

Usa **Bambu Studio** o **PrusaSlicer**:

```bash
# Oppure via script (local):
python upload_gcode.py Vortex_Ball.stl 0.2 15 none
```

Parametri:
- `0.2` = layer height (mm)
- `15` = infill (%)
- `none` = supports (none|tree|linear)

Output: `Vortex_Ball_printqueue.gcode` → Carica questo!

### **Step 2: Accedi al Sito**

```
https://printqueue-yjfk.onrender.com
Password: Leonardo Carlo Manzone
```

### **Step 3: Carica File**

- **Trascina** `.gcode` nella zona grigia, oppure
- **Clicca** per scegliere il file

Il sito automaticamente:
- Estrae altezza pezzo dal gcode
- Inietta sequenza eiezione
- Aggiunge al file in coda

### **Step 4: Seleziona Colore**

Clicca **"▶ Stampa"** → Scegli cerchio colorato → Clicca **"✓ Stampa"**

I colori vengono dai **slot AMS** della tua stampante (se configurati).

### **Step 5: Monitora**

Nel Log vedi:
```
[18:15:59] Connesso al cloud Bambu
[18:16:05] Upload ricevuto: test.gcode
[18:16:06] Altezza pezzo: 5.2mm
[18:16:07] Eject gcode generato
[18:16:08] Avvio stampa: test.gcode
[18:16:09] Stampa... 0% | Temp nozzle: 220°C | ~45 min
```

### **Step 6: Emergenza**

**"■ Stop"** = Ferma stampa, continua con prossimo file  
**"✕ Annulla"** = Ferma tutto, esegui eiezione forzata, rimuovi file dalla coda  

---

## 🔄 Sequenza di Eiezione Automatica

Dopo ogni print, il gcode iniettato esegue:

```gcode
; === AUTO EJECT SEQUENCE ===
M400                    ; aspetta finché finisce
M104 S0                 ; estrusore OFF
M140 S0                 ; piatto OFF
G4 P300000              ; cooldown 300 secondi
G28 Z                   ; home Z (sicuro)
G1 Z25 F600             ; alza 25mm (sopra tutto)
G1 X128 Y254 F6000      ; posiziona dietro
G1 Z3 F300              ; abbassa a contatto (delicato)
G1 Y2 F200              ; spingi in avanti (lento)
G1 Z20 F600             ; alza subito (pezzo non tocca)
G28 X Y                 ; home finale
; === END EJECT ===
```

**Protezioni:**
- ✅ Z25 all'inizio (no contatto estrusore)
- ✅ Spinta F200 (lentissima)
- ✅ Alza subito dopo (pezzo cade libero)
- ✅ Cooldown configurable (300s default)

---

## ⚙️ Configurazione

### **Raffr Colddown**

Nel sito, sezione **Impostazioni**:
```
Raffreddamento (secondi): 300
[Salva]
```

Min: 30s | Max: 3600s

### **Test Eiezione Manuale**

```
[Impostazioni] → [Test espulsione manuale]
```

Esegue l'eiezione senza stampa (utile per debug).

### **Variabili Ambiente**

```bash
BAMBU_TOKEN          # Token authentication
BAMBU_UID            # User ID
BAMBU_SERIAL         # Printer serial (A1 back panel)
BASE_URL             # Cloud server URL (Render)
SECRET_KEY           # Sito password
COOLDOWN_SECONDS     # Cooldown time (default 300)
PLATE_X              # Bed width (256 for A1)
PLATE_Y              # Bed depth (256 for A1)
```

---

## 📁 Struttura Files

```
printqueue/
├── app.py                 # Flask backend (API, web UI)
├── bambu.py              # Cloud MQTT communication
├── upload_gcode.py       # Local slicing tool
├── get_token.py          # Token acquisition (2FA)
├── requirements.txt      # Python dependencies
├── build.sh              # Render build script
├── render.yaml           # Render deployment config
├── .env                  # Secrets (NEVER commit!)
├── uploads/              # Gcode files storage
└── README.md             # This file
```

---

## 🐛 Troubleshooting

### **Stampante non connessa**

```
[❌] Non connesso
```

**Soluzione:**
1. Verifica token Bambu: `python get_token.py`
2. Verifica serial stampante in `.env`
3. Riavvia sito: `git push` (Render redeploy)

### **Upload fallisce**

```
ERROR uploading: Upload fallito
```

**Soluzione:**
1. File deve finire con `.gcode`
2. Check file size (max 100MB)
3. Guarda il Log nel sito

### **Stampa non parte**

```
[Status] printing: 0%
[Log] Avvio stampa... (resta bloccato)
```

**Soluzione:**
1. Controlla che stampante sia online (sezione Stampante)
2. Clicca "■ Stop", poi riprova
3. Se ancora bloccato, clicca "✕ Annulla" → Eiezione forzata

### **Pezzo non cade**

```
[Log] Eiezione completata. (Ma pezzo resta sul piatto)
```

**Soluzione:**
1. Pezzo potrebbe essere incollato al piatto
2. Aumenta `Raffreddamento` a 600 secondi (più tempo per ritrarre)
3. Clicca "Test espulsione manuale" per riprovare
4. Se ancora no: togli manualmente, verifica PEI plate

---

## 📊 API Endpoints (interno)

```bash
POST /login                      # Login sito
POST /api/upload                 # Upload gcode
GET  /api/status                 # Stato stampante + coda
POST /api/start                  # Avvia automazione
POST /api/stop                   # Ferma (continua prossimo)
POST /api/cancel                 # Annulla (eiezione forzata)
POST /api/cooldown               # Cambia cooldown
POST /api/eject                  # Test eiezione manuale
POST /api/remove                 # Rimuovi file dalla coda
GET  /api/ams                    # Slot filamento disponibili
GET  /files/<filename>           # Scarica gcode (per stampante)
```

---

## 🔐 Sicurezza

⚠️ **IMPORTANTE:**
- `.env` non è mai committato (`.gitignore`)
- Sito ha password (vedi `.env: SECRET_KEY`)
- Token Bambu è privato — non condividere!

---

## 📝 Licenza

Progetto personale per Bambu Lab A1 automation.

---

## 💬 Support

Controlla il **Log** nel sito per debug in tempo reale. Mostra ogni step dell'automazione.

**Ultimo aggiornamento:** Giugno 2026
