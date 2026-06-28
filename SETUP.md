# Setup Guide — Print Queue Automation

Complete setup instructions from scratch.

---

## Prerequisites

- Bambu Lab A1 printer
- Bambu Lab account (email + password)
- Git installed
- Python 3.8 or later
- PrusaSlicer or Bambu Studio (local)

---

## Step 1: Clone Repository

```bash
git clone https://github.com/Leo-color/printqueue.git
cd printqueue
```

---

## Step 2: Obtain Bambu Token

Run the token acquisition script:

```bash
python get_token.py
```

When prompted:
1. Enter your Bambu Lab email
2. Enter your Bambu Lab password
3. Check your email for 2FA code
4. Enter the verification code

**Output:**
```
BAMBU_TOKEN: xyz123...
BAMBU_UID: 9999
```

Save these values for the next step.

---

## Step 3: Create .env File

In the `printqueue` directory, create `.env`:

```bash
BAMBU_TOKEN=xyz123...
BAMBU_UID=9999
BAMBU_SERIAL=M1234567
BASE_URL=https://printqueue-yjfk.onrender.com
SECRET_KEY=Leonardo Carlo Manzone
COOLDOWN_SECONDS=300
PLATE_X=256.0
PLATE_Y=256.0
```

**Finding BAMBU_SERIAL:**
```
Bambu Lab A1 → Menu → Settings → System Information → Serial Number
(Usually starts with "M")
```

---

## Step 4: Test Locally

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start Local Server

```bash
python app.py
```

Output:
```
  Print Queue → http://localhost:5000
```

### Access Web Interface

```
http://localhost:5000
Password: Leonardo Carlo Manzone
```

Verify the Printer section shows "Connected".

### Stop Server

Press `Ctrl+C`

---

## Step 5: Deploy to Render

### Create Render Account

Visit https://render.com and sign up (free tier available).

### Connect GitHub Repository

1. Login to Render dashboard
2. Click "New +" → "Web Service"
3. Select your `printqueue` repository
4. Configure:
   - **Name:** printqueue
   - **Runtime:** Python
   - **Build Command:** `bash build.sh`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`

### Add Environment Variables

In Render dashboard, Environment section, add:

```
BAMBU_TOKEN=xyz123...
BAMBU_UID=9999
BAMBU_SERIAL=M1234567
BASE_URL=https://printqueue-yjfk.onrender.com
SECRET_KEY=Leonardo Carlo Manzone
```

### Deploy

```bash
git push origin main
```

Render automatically builds and deploys. Wait 2-3 minutes.

---

## Step 6: Verify Connection

Visit: `https://printqueue-yjfk.onrender.com`

Check Printer section:
- Green indicator = Connected
- Red indicator = Not connected

If not connected:
1. Run `python get_token.py` for fresh token
2. Update `BAMBU_TOKEN` and `BAMBU_UID` in Render environment
3. Click "Redeploy latest commit" in Render dashboard

---

## Step 7: First Print

### Generate G-code

Using Bambu Studio or PrusaSlicer:
```
File → Export → Save as: part.gcode
```

Or using the local script:
```bash
python upload_gcode.py part.stl 0.2 15 none
```

### Upload to Queue

1. Go to `https://printqueue-yjfk.onrender.com`
2. Drag and drop `part.gcode` into the upload area
3. System extracts piece height and injects ejection sequence

### Start Printing

1. Click the "Play" button
2. Choose filament color from available slots
3. Click "Print"

Monitor the Log section for progress.

---

## Troubleshooting Setup

### "Printer not connected" on first access

```bash
# Get fresh token
python get_token.py

# Update .env with new BAMBU_TOKEN and BAMBU_UID
# Update Render environment variables
# Push changes
git push origin main
```

### "Upload fails with ERROR 403"

**Cause:** Wrong password

**Solution:**
```
Password: Leonardo Carlo Manzone
Check SECRET_KEY matches in .env and Render
```

### "Render build fails"

Check Render dashboard logs for detailed error.

Common causes:
- Missing dependencies in requirements.txt
- Invalid environment variables
- Python version mismatch

Re-run `git push origin main` after fixing the issue.

---

## File Structure

```
printqueue/
├── .env                      (secrets — never commit)
├── app.py                    (Flask backend)
├── bambu.py                  (MQTT cloud)
├── get_token.py              (Token acquisition)
├── upload_gcode.py           (Local slicing)
├── requirements.txt
├── build.sh
├── render.yaml
└── uploads/                  (G-code storage)
```

---

## Next Steps

- Read [README.md](README.md) for how to use the system
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if you encounter issues
- Monitor the Log section for real-time debugging

---

*Setup Guide v1.0 — June 2026*
