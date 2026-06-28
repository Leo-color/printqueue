# 📚 Documentazione Completa — Print Queue

Indice di **tutti i documenti** per usare il sistema.

---

## 🎯 Scegli la Tua Guida

### 👤 **Sono nuovo — voglio capire**
→ Leggi: **[README.md](README.md)**
- Cos'è il sistema
- Funzionalità principali
- Workflow completo
- API endpoints

---

### 🔧 **Voglio installarlo da zero**
→ Leggi: **[SETUP.md](SETUP.md)**
- Prerequisites
- Ottieni token Bambu
- Configura .env
- Deploy su Render
- Prima stampa

---

### 🆘 **Qualcosa non funziona**
→ Leggi: **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**
- Errori comuni
- Soluzioni rapide
- Debug avanzato
- FAQ

---

## 📖 Tutti i Documenti

| Documento | Descrizione | Quando leggere |
|-----------|------------|-----------------|
| **[README.md](README.md)** | Guida generale completa | Sempre (reference) |
| **[SETUP.md](SETUP.md)** | Setup passo-passo | Prima di usare |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | Problemi e soluzioni | Quando c'è un errore |
| **[DOCS.md](DOCS.md)** | Questo file (indice) | Orientamento |

---

## 🚀 Quick Start (5 minuti)

```bash
# 1. Clona
git clone https://github.com/Leo-color/printqueue.git
cd printqueue

# 2. Token Bambu
python get_token.py
# → Salva BAMBU_TOKEN e BAMBU_UID

# 3. Configura .env
echo "BAMBU_TOKEN=xyz" > .env
echo "BAMBU_UID=999" >> .env
echo "BAMBU_SERIAL=Mxxxxxxx" >> .env
echo "BASE_URL=https://printqueue-yjfk.onrender.com" >> .env

# 4. Deploy
git push origin main
# Attendi 3 minuti, poi accedi a:
# https://printqueue-yjfk.onrender.com
```

---

## 🎮 Workflow Tipico

```
1. Slicing Locale (PrusaSlicer)
   ↓
2. Carica .gcode sul sito
   ↓
3. Scegli colore
   ↓
4. Clicca "▶ Stampa"
   ↓
5. Sistema stampa automaticamente
   ↓
6. Pezzo cade (eiezione automatica)
   ↓
7. Continua prossimo file
```

Per dettagli: vedi [README.md#come-usare](README.md#come-usare)

---

## 🔑 Configurazione Essenziale

```bash
# File: .env
BAMBU_TOKEN=xxxxx           # Da python get_token.py
BAMBU_UID=99999             # Da python get_token.py
BAMBU_SERIAL=Mxxxxxxx       # Dal retro A1
BASE_URL=https://printqueue-yjfk.onrender.com
SECRET_KEY=Leonardo Carlo Manzone
```

---

## 🐛 Problemi Rapidi

| Problema | Soluzione | Dove leggere |
|----------|-----------|--------------|
| **Stampante non connessa** | Nuovo token con `python get_token.py` | [TROUBLESHOOTING](TROUBLESHOOTING.md#stampante-non-connessa) |
| **Upload fallisce** | File deve essere `.gcode` | [TROUBLESHOOTING](TROUBLESHOOTING.md#upload-file-fallisce) |
| **Stampa non parte** | Verifica stampante online | [TROUBLESHOOTING](TROUBLESHOOTING.md#stampa-non-parte) |
| **Pezzo non cade** | Aumenta cooldown a 600s | [TROUBLESHOOTING](TROUBLESHOOTING.md#pezzo-non-cade) |
| **Deploy fallisce su Render** | Vedi log Render | [TROUBLESHOOTING](TROUBLESHOOTING.md#problemi-render) |

---

## 📁 Struttura Repo

```
printqueue/
├── README.md                 # ← Leggi prima
├── SETUP.md                  # ← Poi questo
├── TROUBLESHOOTING.md        # ← Se problemi
├── DOCS.md                   # ← Questo (indice)
├── .env                      # ⚠️ Secrets (gitignored)
├── app.py                    # Flask backend
├── bambu.py                  # MQTT cloud
├── get_token.py              # Token Bambu 2FA
├── upload_gcode.py           # Slicing locale
├── requirements.txt
├── build.sh
├── render.yaml
└── uploads/                  # Gcode files (auto)
```

---

## 💬 Contatti & Support

### Prima di contattare:

1. ✅ Leggi [README.md](README.md)
2. ✅ Leggi [SETUP.md](SETUP.md)
3. ✅ Leggi [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. ✅ Guarda il **Log** nel sito

### Se ancora non funziona:

- GitHub Issues: https://github.com/Leo-color/printqueue/issues
- Descrivi il problema e il Log esatto

---

## 🔄 Versioni Docs

| Versione | Data | Nota |
|----------|------|------|
| 1.0 | Giugno 2026 | Release iniziale |

---

## ✅ Checklist Primo Setup

- [ ] Ho clonato il repo
- [ ] Ho creato token con `python get_token.py`
- [ ] Ho configurato `.env` con token, serial, URL
- [ ] Ho fatto `git push origin main`
- [ ] Render ha finito il deploy
- [ ] Accedo a sito e vedo "Connesso" ✅
- [ ] Carico un file `.gcode`
- [ ] Clicco "▶ Stampa"
- [ ] Stampante inizia a stampare
- [ ] Pezzo cade dopo print ✨

Se ✅ tutto: **Sistema pronto!** 🚀

---

**Buona stampa! 🖨️✨**

---

*Ultima modifica: Giugno 2026*
*Print Queue v1.0 — Bambu Lab A1 Automation*
