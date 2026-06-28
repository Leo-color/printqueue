# Documentation Index

Find the documentation you need.

---

## Documentation Overview

| Document | Purpose | Read When |
|----------|---------|-----------|
| **[README.md](README.md)** | Complete feature overview and usage guide | First-time users and reference |
| **[SETUP.md](SETUP.md)** | Step-by-step installation instructions | Setting up the system |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | Problem diagnosis and solutions | Experiencing issues |
| **[DOCS.md](DOCS.md)** | This documentation index | Finding what you need |

---

## Quick Start

### New User

Start here → [README.md](README.md)

Key sections:
- Getting Started (5 minutes)
- How to Use (complete workflow)
- Automatic Ejection Sequence

### Setting Up

Follow → [SETUP.md](SETUP.md)

Seven-step journey:
1. Clone Repository
2. Obtain Bambu Token
3. Create .env File
4. Test Locally
5. Deploy to Render
6. Verify Connection
7. First Print

### Experiencing Issues

Check → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

Common issues:
- Printer Not Connected
- Upload File Fails
- Print Won't Start
- Piece Won't Fall
- Render Deployment Issues

---

## Feature Overview

### Automatic Print Queue

Upload multiple `.gcode` files and the system prints them sequentially without intervention.

[Learn more →](README.md#key-features)

### Automatic Ejection

After each print completes, the piece automatically falls from the build plate.

[Learn more →](README.md#automatic-ejection-sequence)

### Filament Selection

Choose from available filament colors in your Bambu Lab AMS before each print.

[Learn more →](README.md#start-printing)

### Real-time Monitoring

Monitor printer status, temperatures, and progress through the web interface.

[Learn more →](README.md#monitor-in-real-time)

---

## Setup Checklist

Use this when setting up:

- [ ] Cloned repository
- [ ] Ran `python get_token.py`
- [ ] Created `.env` file with credentials
- [ ] Tested locally with `python app.py`
- [ ] Created Render account
- [ ] Connected GitHub repository to Render
- [ ] Set environment variables in Render
- [ ] Pushed with `git push origin main`
- [ ] Verified printer shows "Connected"
- [ ] Generated first `.gcode` file
- [ ] Uploaded file and started print
- [ ] Piece fell after print completed

If all checked: System is ready!

---

## Configuration Reference

### Environment Variables (.env)

```
BAMBU_TOKEN          # From python get_token.py
BAMBU_UID            # From python get_token.py
BAMBU_SERIAL         # Printer serial number (from label)
BASE_URL             # https://printqueue-yjfk.onrender.com
SECRET_KEY           # Web interface password
COOLDOWN_SECONDS     # Cooldown time (default 300)
PLATE_X              # Build plate width (256 for A1)
PLATE_Y              # Build plate depth (256 for A1)
```

### Web Interface Settings

**Cooldown (seconds):** 30 to 3600 seconds

Increase for:
- Larger pieces
- Sticky PEI plates
- Complex geometries

---

## API Reference

### Upload G-code

```
POST /api/upload
```

Accepts `.gcode` files and injects ejection sequence.

### Get Status

```
GET /api/status
```

Returns:
- Printer connection status
- Print queue
- Current job status
- Temperature data
- Log entries

### Start/Stop Automation

```
POST /api/start     # Start printing automation
POST /api/stop      # Stop (continue next file)
POST /api/cancel    # Cancel (forced ejection, remove file)
```

### Get Filament Colors

```
GET /api/ams
```

Returns available filament slots from printer.

[See full API reference →](README.md#api-endpoints-internal)

---

## File Structure

```
printqueue/
├── README.md                 # Main documentation
├── SETUP.md                  # Setup instructions
├── TROUBLESHOOTING.md        # Troubleshooting guide
├── DOCS.md                   # This file
├── app.py                    # Flask web server
├── bambu.py                  # Bambu Cloud MQTT
├── get_token.py              # Token acquisition
├── upload_gcode.py           # Local slicing
├── requirements.txt          # Python dependencies
├── build.sh                  # Render build script
├── render.yaml               # Render configuration
├── .env                      # Configuration (secrets)
└── uploads/                  # Uploaded G-code files
```

---

## System Requirements

### Hardware

- Bambu Lab A1 printer
- Computer for local slicing
- Internet connection (for cloud access)

### Software

- Python 3.8+
- Git
- PrusaSlicer or Bambu Studio

### Accounts

- Bambu Lab account (for token authentication)
- Render account (for cloud hosting, free tier available)

---

## Key Concepts

### Automatic Ejection

The system automatically injects a G-code sequence at the end of each print that:
1. Cools the hotend and bed
2. Waits configurable cooldown period
3. Positions nozzle at print center-back
4. Lowers nozzle to piece surface
5. Pushes piece toward front
6. Raises nozzle above plate
7. Homes axes

[Learn more →](README.md#automatic-ejection-sequence)

### Print Queue

Upload multiple files. System processes them sequentially, printing each file and executing ejection between prints.

### Filament Selection

Before each print, choose the filament color from available AMS slots. The system uses this for reporting and organization.

### Cloud Control

Access the system from anywhere via Render cloud hosting. Uses Bambu Cloud MQTT for printer communication.

---

## Getting Help

### Troubleshooting Steps

1. Check [README.md](README.md) for feature details
2. Check [SETUP.md](SETUP.md) for setup help
3. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for error solutions
4. Check Log section in web interface

### Common Solutions

| Issue | Solution |
|-------|----------|
| Printer not connected | Run `python get_token.py` again |
| Upload fails | Ensure file ends with `.gcode` |
| Print won't start | Check printer is online |
| Piece won't fall | Increase cooldown in Settings |
| Render deploy fails | Check Render logs, redeploy |

---

## Support

For additional help:
- Check all documentation sections
- Review Log in web interface
- Verify all configuration steps completed
- Test manual ejection from Settings

---

*Documentation v1.0 — June 2026*
