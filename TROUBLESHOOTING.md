# Troubleshooting — Print Queue Automation

Common issues and solutions.

---

## Printer Not Connected

**Symptom:**
```
Status: Not Connected
```

**Causes and Solutions:**

### Token Expired

```bash
python get_token.py        # Obtain new token
```

Update in `.env` and Render environment variables, then redeploy:
```bash
git push origin main
```

### Serial Number Incorrect

Verify printer serial:
```
Bambu Lab A1 → Menu → Settings → System Information
```

Update `BAMBU_SERIAL=M...` in both `.env` and Render environment.

Redeploy:
```bash
git push origin main
```

### Environment Variables Not Saved

In Render dashboard:
- Check that all environment variables are present
- Click "Redeploy latest commit"
- Wait 2-3 minutes

### Printer Offline

```
Bambu Lab A1 → Check WiFi connection
Restart printer if needed
```

---

## Upload File Fails

**Symptom:**
```
ERROR: Upload failed
```

**Causes and Solutions:**

### Wrong File Format

File must end with `.gcode`

Acceptable:
- `part.gcode` ✓
- `part_printqueue.gcode` ✓

Not acceptable:
- `part.gcode.bak` ✗
- `part.stl` ✗

### File Too Large

Maximum size: 100 MB

**Solution:** Split print into multiple files using PrusaSlicer.

### Password Incorrect

Password: `Leonardo Carlo Manzone`

Verify `SECRET_KEY` matches in `.env` and Render environment.

### Server Unavailable

Check Render dashboard. If showing errors, redeploy:
```bash
git push origin main
```

---

## Print Won't Start

**Symptom:**
```
Status: printing (0%)
Log: "Starting print..." (stuck)
```

**Causes and Solutions:**

### Printer Offline

In web interface:
- Check Printer section indicator
- If red: see "Printer Not Connected" section above

### No File in Queue

Before clicking Print:
- Upload a `.gcode` file
- Verify it appears in the queue

### Corrupted File

**Symptoms:** File doesn't show in queue, or shows error in Log

**Solution:** Re-upload or regenerate the file with PrusaSlicer

### API Not Responding

1. Refresh page (F5 or Ctrl+R)
2. Click "Stop"
3. Wait 5 seconds
4. Try again

---

## Piece Won't Fall

**Symptom:**
```
Log: "Ejection complete"
Reality: Piece still on plate
```

**Causes and Solutions:**

### Insufficient Cooldown

The piece may not have cooled enough.

**Solution:**
1. In web interface, Settings section, increase "Cooldown (seconds)"
2. Try 600 seconds (10 minutes) for larger pieces
3. Click Save
4. Try again with next print

### PEI Plate Issues

PEI surface may be dirty or aged.

**Solution:**
1. Clean PEI plate with isopropyl alcohol
2. Warm plate to 60°C to release piece
3. Click "Test Manual Ejection" in Settings
4. If still stuck: remove piece manually

### Piece Too Large or Complex

Large pieces may not fall completely.

**Solution:**
1. Click "Test Manual Ejection" to retry
2. If piece still stuck: increase cooldown time
3. Remove manually if necessary

### Nozzle Issue

Nozzle may not be moving correctly.

**Solution:**
1. Check hotend for debris
2. Click "Test Manual Ejection"
3. If issue persists: check printer mechanics

---

## Errors in Log

### "ERROR: Save error: Permission denied"

**Cause:** Upload directory permissions issue

**Solution (Local):**
```bash
chmod -R 755 uploads/
```

**Solution (Render):** Already configured. Redeploy:
```bash
git push origin main
```

### "ERROR: Eject gcode: File not found"

**Cause:** File not saved correctly

**Solution:**
```bash
# Local testing
ls uploads/     # Should list your files

# If empty: re-upload the file
```

### "ERROR: MQTT connection failed"

**Cause:** Token expired or Bambu Cloud unreachable

**Solution:**
```bash
python get_token.py     # Get new token
# Update .env and Render environment
git push origin main
```

### "ERROR: Cooldown out of range"

**Cause:** Invalid cooldown value

**Solution:**
```
Valid range: 30 to 3600 seconds
30 = 30 seconds (minimum)
300 = 5 minutes (default)
3600 = 1 hour (maximum)
```

---

## Render Deployment Issues

### Build Fails

Check Render dashboard Logs for specific error.

**Common causes:**
- Missing Python dependencies
- Syntax error in code
- Invalid environment variable

**Solution:**
```bash
# Fix the issue locally
git push origin main    # Retry build
```

### Service Runs but Doesn't Respond

1. Visit Render dashboard → Logs
2. Check for Python errors
3. Click "Restart Service"
4. Wait 2 minutes
5. Try again

### Port Already in Use (Local)

```bash
# If running locally and get "port 5000 in use"
lsof -ti:5000 | xargs kill -9

# Or use different port
python app.py --port 5001
# Access: http://localhost:5001
```

---

## Testing

### Test Locally (Offline)

```bash
python app.py
# Access: http://localhost:5000
# Works without internet? No (requires Bambu Cloud)
```

### Test on Cloud (via Render)

```
https://printqueue-yjfk.onrender.com
# Works on mobile 4G? Yes (Bambu Cloud connection)
```

### Manual Ejection Test

In Settings section:
- Click "Test Manual Ejection"
- Runs ejection sequence without printing
- Useful for debugging

---

## Debug Mode

### Enable Flask Debug

```bash
export FLASK_DEBUG=1
python app.py
# More detailed errors and hot-reload
```

### View HTTP Requests

In browser:
1. Press F12 (Developer Tools)
2. Click Network tab
3. Upload file
4. Check requests for errors

### View Render Logs Live

```
Render dashboard → Service → Logs
Shows everything happening on server
Search for "ERROR" to find issues
```

---

## When to Contact Support

Before reaching out:
1. Read [README.md](README.md)
2. Read [SETUP.md](SETUP.md)
3. Check this document
4. Look at Log in web interface
5. Try "Test Manual Ejection"

If still stuck:
- Check Render logs for specific error message
- Include the exact error from the Log
- Include screenshot if helpful

---

*Troubleshooting Guide v1.0 — June 2026*
