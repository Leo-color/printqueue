# 🔧 SETUP COMPLETO — Print Queue Bambu Lab A1

Guida passo-passo per configurare tutto da zero.

---

## 📌 Prerequisiti

- ✅ Bambu Lab A1 (stampante)
- ✅ Account Bambu Lab (email + password)
- ✅ Git installato
- ✅ Python 3.8+
- ✅ PrusaSlicer o Bambu Studio (locale)

---

## 🚀 Fase 1: Clona il Repo

```bash
git clone https://github.com/Leo-color/printqueue.git
cd printqueue
```

---

## 🔑 Fase 2: Ottieni Token Bambu

Questo script esegue il login Bambu con 2FA:

```bash
python get_token.py
```

**Inserisci:**
1. Email Bambu Lab
2. Password Bambu Lab
3. Attendi email con codice 2FA
4. Inserisci il codice

**Output:**
```
BAMBU_TOKEN: xyz123...
BAMBU_UID: 9999
```

✅ **Salva questi valori!** Servono per `.env`

---

## 🔐 Fase 3: Crea `.env`

Nella cartella `printqueue`, crea il file `.env`:

```bash
# File: printqueue/.env

BAMBU_TOKEN=xyz123...      # Da get_token.py
BAMBU_UID=9999             # Da get_token.py
BAMBU_SERIAL=M1234567      # Leggi sulla A1 dietro (sticker)
BASE_URL=https://printqueue-yjfk.onrender.com
SECRET_KEY=Leonardo Carlo Manzone
COOLDOWN_SECONDS=300
PLATE_X=256.0
PLATE_Y=256.0
```

### Dove trovare BAMBU_SERIAL:

```
Bambu Lab A1 → Menù Impostazioni → Informazioni Sistema → Serial Number
```

---

## 🖥️ Fase 4: Setup Locale (Test)

### Installa dipendenze:

```bash
pip install -r requirements.txt
```

### Avvia il server locale:

```bash
python app.py
```

Output:
```
  Print Queue → http://localhost:5000
```

### Accedi:

```
http://localhost:5000
Password: Leonardo Carlo Manzone
```

Vedi la UI? ✅ Perfetto!

---

## ☁️ Fase 5: Deploy su Render

### Crea account Render:

```
https://render.com → Sign up (free)
```

### Connetti il repo GitHub:

1. Dashboard Render
2. **"New +"** → **"Web Service"**
3. Seleziona repo `printqueue`
4. Configura:
   - **Name:** `printqueue`
   - **Runtime:** Python
   - **Build Command:** `bash build.sh`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`

### Aggiungi variabili ambiente:

In Render dashboard, sezione **Environment**:

```
BAMBU_TOKEN=xyz123...
BAMBU_UID=9999
BAMBU_SERIAL=M1234567
BASE_URL=https://printqueue-yjfk.onrender.com
SECRET_KEY=Leonardo Carlo Manzone
```

### Deploy:

```bash
git push origin main
```

Render farà il deploy automaticamente. Attendi ~3 minuti.

---

## ✅ Fase 6: Verifica Connessione

Accedi a: `https://printqueue-yjfk.onrender.com`

Nella sezione **Stampante**, vedi:

```
🟢 Connesso
```

Se vedi **🔴 Non connesso**, controlla:
1. Token Bambu valido (`python get_token.py` nuovo)
2. Serial stampante corretto (con `M` iniziale)
3. Render environment variables salvate
4. Render redeploy: **"Redeploy latest commit"**

---

## 🎯 Fase 7: Prima Stampa

### Step 1: Genera G-code

Usando **Bambu Studio** o **PrusaSlicer**:

```
File → Export → Salva come: pezzo.gcode
```

Oppure script locale:

```bash
python upload_gcode.py pezzo.stl 0.2 15 none
```

### Step 2: Carica su sito

```
https://printqueue-yjfk.onrender.com
→ Trascina pezzo.gcode
```

Nel Log vedi:
```
[hh:mm:ss] Upload ricevuto: pezzo.gcode
[hh:mm:ss] Altezza pezzo: 5.2mm
[hh:mm:ss] Eject gcode generato
[hh:mm:ss] Aggiunto in coda: pezzo.gcode
```

### Step 3: Seleziona colore

Clicca **"▶ Stampa"** → Scegli cerchio colorato → Clicca **"✓ Stampa"**

### Step 4: Monitora

Nel Log vedi:
```
[hh:mm:ss] Avvio stampa: pezzo.gcode
[hh:mm:ss] Stampa... 5% | ~42 min
[hh:mm:ss] Stampa... 15% | ~38 min
...
[hh:mm:ss] Stampa completata
[hh:mm:ss] Attendo fine espulsione (360s)...
[hh:mm:ss] Espulsione completata
```

### Step 5: Pezzo cade! ✨

Una volta il cooldown è finito, il pezzo cade dal piatto automaticamente.

---

## 🔄 Stampe Continue

Una volta finita la prima stampa:

1. Carica il **prossimo file** (sempre via drag-drop)
2. Clicca **"▶ Stampa"** di nuovo
3. Sistema stampa automaticamente uno per uno 🤖

---

## 📁 Cartelle Importanti

```
printqueue/
├── .env                    # ⚠️ Secrets (NEVER commit!)
├── uploads/                # Gcode files (auto-generati)
├── app.py                  # Main server
├── bambu.py               # MQTT cloud
├── requirements.txt        # Dependencies
└── README.md              # Documentazione
```

**.env non deve mai andare in Git!** (è in `.gitignore`)

---

## 🐛 Debug

### Abilita logging verbose:

```bash
export FLASK_DEBUG=1
python app.py
```

### Vedi log Render live:

```bash
# In Render dashboard → Logs
# Vedi tutto quello che succede sul server
```

### Test token Bambu:

```bash
python get_token.py
# Se fallisce, il token è scaduto → riscarica nuovo
```

---

## 🆘 Problemi Comuni

### "Stampante non connessa"

**Causa:** Token scaduto o serial sbagliato

**Soluzione:**
```bash
python get_token.py     # Nuovo token
# Aggiorna BAMBU_TOKEN e BAMBU_UID in .env e Render
git push origin main    # Render rideploy
```

### "Upload fallisce con ERROR 403"

**Causa:** Password login sito sbagliata

**Soluzione:**
```bash
# Password corretta: Leonardo Carlo Manzone
# Controlla che SECRET_KEY in .env sia identico
```

### "Pezzo non cade dopo stampa"

**Causa:** Cooldown troppo breve, o pezzo incollato

**Soluzione:**
1. Aumenta `COOLDOWN_SECONDS` a 600 (10 min)
2. Prova manualmente: **"Test espulsione manuale"** nel sito
3. Se ancora no: togli a mano, verifica PEI plate

### "Render shows: Build failed"

**Causa:** Dipendenze mancanti o gcode corrupted

**Soluzione:**
```bash
pip install -r requirements.txt
git push origin main     # Retry build
# Vedi logs Render per dettagli
```

---

## 📞 Support

- **Local testing:** `python app.py` → `http://localhost:5000`
- **Cloud logs:** Render dashboard → Logs
- **Printer status:** Sezione "Stampante" nel sito
- **Real-time debug:** Guarda il Log nel sito in tempo reale

---

**Ready to automate! 🚀**

Domande? Controlla `README.md` per dettagli pieni.
