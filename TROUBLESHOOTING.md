# 🆘 TROUBLESHOOTING — Print Queue

Soluzioni rapide ai problemi comuni.

---

## 🔴 Stampante Non Connessa

### Sintomo:
```
[❌] Non connesso
```

### Cause & Soluzioni:

**1. Token scaduto**
```bash
python get_token.py        # Ottieni nuovo token
# Aggiorna .env
# Se su Render: aggiorna environment variables
# git push origin main     # Rideploy
```

**2. Serial stampante sbagliato**
```
Stampante A1 → Menu Impostazioni → Info Sistema → Serial
# Copia esattamente (con M iniziale)
# Aggiorna .env: BAMBU_SERIAL=Mxxxxxxxx
```

**3. Render environment variables non salvate**
```
Render dashboard → Service → Environment
Verifica che BAMBU_TOKEN, BAMBU_UID, BAMBU_SERIAL siano salvati
Se modificati: click "Redeploy latest commit"
```

**4. WiFi A1 disconnessa**
```
Stampante A1 → Menu WiFi → Verifica connessione
Riavvia A1 se necessario
```

---

## 📤 Upload File Fallisce

### Sintomo:
```
ERROR: Upload fallito
```

### Cause & Soluzioni:

**1. File non è .gcode**
```
Nome file deve finire con: .gcode
Non: .gcode.bak, .txt, .stl
```

**2. File troppo grande**
```
Max size: 100MB
Se > 100MB: dividi stampa in più file
```

**3. Server Render down**
```
Visita: https://status.render.com
Se down: attendi ripristino
Altrimenti: git push origin main (rideploy)
```

**4. Password login sbagliata**
```
Password corretta: Leonardo Carlo Manzone
Se "Password errata": controlla SECRET_KEY in .env
Su Render: controlla environment variable SECRET_KEY
```

---

## ▶️ Stampa Non Parte

### Sintomo:
```
[Status] printing: 0%
[Log] Avvio stampa... (bloccato)
```

### Cause & Soluzioni:

**1. Stampante offline**
```
Sezione "Stampante" nel sito:
- Verde 🟢 = Online (OK)
- Rosso 🔴 = Offline (Problema)

Soluzione:
- Riavvia A1
- Controlla WiFi A1
- Controlla token Bambu (vedi "Stampante Non Connessa")
```

**2. Nessun file in coda**
```
Sezione "Aggiungi alla Coda":
Se "Nessun file in coda":
→ Carica un file .gcode prima di cliccare "▶ Stampa"
```

**3. File corrotto**
```
Nel Log vedi: ERROR: File not found / corrupted
Soluzione:
- Ricarica il file .gcode
- Rigenera il file con PrusaSlicer
- Controlla che file non sia vuoto
```

**4. API non risponde**
```
Refresh il sito: F5 oppure Ctrl+R
Se ancora bloccato:
- Clicca "■ Stop"
- Attendi 5 secondi
- Riprova "▶ Stampa"
```

---

## 🎯 Pezzo Non Cade

### Sintomo:
```
[Log] Espulsione completata.
[Reality] Pezzo ancora sul piatto 😢
```

### Cause & Soluzioni:

**1. Cooldown insufficiente**
```
Pezzo non si ritrae abbastanza dal piatto.
Soluzione:
- Aumenta "Raffreddamento (secondi)" a 600 o più
- Clicca "Salva"
- Stampa di nuovo
```

**2. Pezzo incollato al PEI**
```
Il piatto PEI è invecchiato/sporco.
Soluzione:
- Pulisci PEI con alcol isopropilico
- Inspira aria calda (60°C piatto)
- Riprova eiezione manuale
```

**3. Altezza pezzo non rilevata**
```
Sistema non riesce a capire quanto è alto il pezzo.
Nel Log vedi: "Piece height: 5.0mm" (default)
Soluzione:
- Se pezzo è molto grande: aggiungi manualmente nel gcode
- G-code deve avere linee Z per rilevare altezza
```

**4. Nozzle ostruito**
```
L'ugello non scende/sale bene.
Soluzione:
- Clicca "Test espulsione manuale" nel sito
- Se stesso problema: pulisci nozzle
- Controlla no gunk on hotend
```

---

## 🔊 Errori nel Log

### `ERROR: Save error: Permission denied`

**Causa:** Cartella `uploads/` non ha permessi di scrittura

**Soluzione (locale):**
```bash
chmod -R 755 uploads/
```

**Soluzione (Render):** Già configurato, rideploy:
```bash
git push origin main
```

---

### `ERROR: Eject gcode: File not found`

**Causa:** File gcode non salvato correttamente

**Soluzione:**
```bash
# Verifica che file esista:
ls uploads/         # Deve elencare i tuoi file
# Se vuoto: carica di nuovo il file
```

---

### `ERROR: MQTT connection failed`

**Causa:** Token scaduto o cloud Bambu down

**Soluzione:**
```bash
python get_token.py     # Nuovo token
# Aggiorna in .env e Render
git push origin main
```

---

### `ERROR: Cooldown not in range 30-3600`

**Causa:** Hai inserito un valore fuori range

**Soluzione:**
```
Nel sito, sezione "Impostazioni":
Raffreddamento: deve essere tra 30 e 3600 secondi
Esempi validi:
- 30 (mezzo minuto)
- 300 (5 minuti — default)
- 600 (10 minuti)
- 3600 (1 ora max)
```

---

## 🌐 Problemi Render

### Deploy fails: `Build command failed`

```bash
# Verifica dipendenze:
pip install -r requirements.txt

# Controlla build.sh sintassi:
cat build.sh     # Deve essere valido bash

# Ripush:
git push origin main
```

---

### Deploy succeeds pero sito non risponde

```
Render dashboard → Logs
Vedi errore Python?
Se sì: correggi app.py e ripush

Se no errore visibile:
- Riavvia servizio: Render dashboard → "Restart"
- Attendi 2 minuti
- Riprova https://printqueue-yjfk.onrender.com
```

---

### "Port already in use" (locale)

```bash
# Se app.py dice: Port 5000 already in use

# Uccidi il processo:
lsof -ti:5000 | xargs kill -9

# Oppure usa porta diversa:
python app.py --port 5001
# Accedi: http://localhost:5001
```

---

## 🖥️ Test Locale vs Cloud

### Test Locale (offline, no cloud):

```bash
cd printqueue
python app.py
# Accedi: http://localhost:5000
# Funziona senza internet? ❌ (serve cloud Bambu)
```

### Test Cloud (su Render):

```
https://printqueue-yjfk.onrender.com
Funziona da celluare su 4G? ✅ (connessione cloud OK)
```

---

## 📊 Debug Avanzato

### Abilita Flask debug mode:

```bash
export FLASK_DEBUG=1
python app.py
```

Vedi errori dettagliati e hot-reload.

---

### Vedi request/response HTTP:

```bash
# Nel browser, premi F12 → Network
# Carica file
# Guarda le richieste:
POST /api/upload → Status 200 OK? ✅
```

---

### Controlla log Render live:

```bash
# Render dashboard → Service → Logs
# Vedi tutto quello che succede sul server
# Cercaparte: grep "ERROR" per errori
```

---

## ☎️ Quando Contattare Support

Se ancora non funziona:

1. ✅ Leggi questo documento
2. ✅ Controlla [README.md](README.md)
3. ✅ Leggi [SETUP.md](SETUP.md)
4. ✅ Guarda il Log nel sito per indizi
5. ✅ Prova "Test espulsione manuale"

Se ancora bloccato, puoi:
- Aprire una issue su GitHub
- Descrivere il Log esatto che vedi
- Includere screenshot

---

**Buona stampa! 🖨️✨**
