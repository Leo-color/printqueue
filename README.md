# Print Queue Automation for Bambu Lab A1

An automated continuous printing system with automatic piece ejection for Bambu Lab A1. Access and control your printer from anywhere using Bambu Cloud.

## Key Features

- **Automatic Print Queue** — Upload .gcode files and the system prints them one after another
- **Automatic Piece Ejection** — Nozzle automatically pushes completed pieces off the plate (active movement, no mechanical parts needed)
- **Filament Selection** — Choose filament color before each print
- **Continuous Printing Loop** — Automatically continues through all queued files
- **Web Control** — Access from any device, anywhere in the world
- **Real-time Monitoring** — Printer status, temperatures, and time remaining
- **Emergency Controls** — Stop and Cancel buttons with forced ejection

## What Makes This Different

Unlike static ejection systems (FarmLoop Stage 1), this system uses **active nozzle movement** to push pieces off the plate:
- No mechanical parts needed
- Works with any Bambu Lab A1
- Reliable and repeatable
- Fully automated via G-code injection

---

## How It Works

The system automatically injects a specialized G-code sequence at the end of each print that uses the nozzle itself to eject pieces:

1. **Cooldown** — Let the part cool
2. **Position** — Move nozzle to piece location
3. **Push** — Use nozzle to push piece forward
4. **Eject** — Piece falls off plate
5. **Home** — Return to safe position

No mechanical parts, actuators, or modifications needed. Pure G-code automation.

---

## Compared to Other Systems

| Feature | This System | FarmLoop Stage 1 | FarmLoop Stage 2 |
|---------|-------------|-----------------|-----------------|
| **Ejection Method** | Active nozzle push | Static scraper | Linear actuator |
| **Mechanical Parts** | None | Yes | Yes |
| **Setup Complexity** | Easy | Moderate | Complex |
| **Cost** | Free | ~$50 | ~$300+ |
| **Reliability** | High | High | Very High |
| **Automation** | 100% cloud | Partial | Full electronics |

---

## Getting Started

### Requirements

- Bambu Lab A1 printer
- Bambu Lab account (email + password)
- PrusaSlicer or Bambu Studio (local installation)
- Render.com account (free tier)

### Six-Step Journey

1. **Get Bambu Token** — Authenticate with your Bambu Lab account
2. **Configure Environment** — Set up .env with credentials
3. **Deploy to Cloud** — Push to Render for cloud hosting
4. **Slice Locally** — Generate .gcode files using PrusaSlicer
5. **Upload & Select** — Load files to queue, choose filament color
6. **Print Continuously** — System prints automatically, ejects pieces

---

## Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/Leo-color/printqueue.git
cd printqueue
```

### Step 2: Obtain Bambu Token

```bash
python get_token.py
```

Enter your Bambu Lab credentials and 2FA code when prompted.

**Output:**
- `BAMBU_TOKEN`
- `BAMBU_UID`

Save these values for the next step.

### Step 3: Configure .env

Create a file named `.env` in the `printqueue` directory:

```bash
BAMBU_TOKEN=<your_token>
BAMBU_UID=<your_uid>
BAMBU_SERIAL=<printer_serial>
BASE_URL=https://printqueue-yjfk.onrender.com
SECRET_KEY=Leonardo Carlo Manzone
COOLDOWN_SECONDS=300
PLATE_X=256.0
PLATE_Y=256.0
```

**Where to find BAMBU_SERIAL:**
- Printer Menu → Settings → System Information → Serial Number

### Step 4: Deploy to Render

```bash
git push origin main
```

Render will automatically build and deploy your application. This takes 2-3 minutes.

### Step 5: Access the Application

Once deployed, visit:
```
https://printqueue-yjfk.onrender.com
```

Password: `Leonardo Carlo Manzone`

Verify that the printer shows as "Connected" in the Printer section.

---

## How to Use

### Generate G-code Locally

Use Bambu Studio or PrusaSlicer to slice your STL/OBJ/3MF files:

```
File → Export → Save as: part.gcode
```

Or use the local script:

```bash
python upload_gcode.py part.stl 0.2 15 none
```

Parameters:
- `0.2` = Layer height (mm)
- `15` = Infill (%)
- `none` = Supports (none|tree|linear)

### Upload to Queue

1. Go to `https://printqueue-yjfk.onrender.com`
2. Drag and drop your `.gcode` file into the upload area
3. The system will automatically:
   - Extract piece height from the file
   - Inject ejection sequence
   - Add to print queue

### Start Printing

1. Click the "Play" button to show color selection
2. Choose a filament color from available slots
3. Click "Print" to start
4. Monitor progress in the Log section

The system will:
- Download the file to your printer via Bambu Cloud
- Print automatically
- Execute ejection sequence when complete
- Continue to the next file in queue

### Monitor in Real-time

The Log section shows:
- Upload status
- Print progress (percentage, temperature, time remaining)
- Ejection status
- Next file starting

### Emergency Controls

**Stop** — Pause current print, continue with next file  
**Cancel** — Stop printing completely, execute forced ejection, remove file from queue

---

## Automatic Ejection Sequence

After each print, the injected G-code executes:

```gcode
M400                    ; wait for all moves to complete
M104 S0                 ; nozzle heater off
M140 S0                 ; bed heater off
G4 P300000              ; cooldown period (300 seconds)
G28 Z                   ; home Z axis (safe position)
G1 Z25 F600             ; raise 25mm (above hotend)
G1 X128 Y254 F6000      ; move to back center
G1 Z3 F300              ; lower gently to piece
G1 Y2 F200              ; push piece forward (slow)
G1 Z20 F600             ; raise immediately (piece falls free)
G28 X Y                 ; home XY axes
```

**Safety Features:**
- High Z raise prevents nozzle contact
- Slow push speed ensures controlled movement
- Immediate raise prevents piece touching hotend during fall
- Configurable cooldown (30-3600 seconds)

---

## Configuration

### Cooldown Period

In the web interface under Settings:

```
Cooldown (seconds): 300
```

Adjust if pieces don't fall completely. Increase for larger pieces or sticky PEI.

### Test Manual Ejection

Click "Test Manual Ejection" button to run the ejection sequence without printing.

---

## Documentation

- **[SETUP.md](SETUP.md)** — Detailed setup instructions
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** — Common issues and solutions
- **[DOCS.md](DOCS.md)** — Documentation index

---

## API Endpoints (Internal)

```
POST  /login                    # Web interface login
POST  /api/upload               # Upload G-code file
GET   /api/status               # Get printer status and queue
POST  /api/start                # Start print automation
POST  /api/stop                 # Stop automation (continue next)
POST  /api/cancel               # Cancel with forced ejection
POST  /api/cooldown             # Update cooldown seconds
POST  /api/eject                # Manual ejection test
GET   /api/ams                  # Get available filament colors
GET   /files/<filename>         # Download G-code file
```

---

## Troubleshooting

### Printer Not Connected

```
Status: Not Connected
```

**Solution:**
1. Run `python get_token.py` for fresh token
2. Verify printer serial in .env
3. Deploy: `git push origin main`

### Upload Fails

Ensure:
- File ends with `.gcode`
- File size under 100MB
- Using correct password

### Piece Doesn't Fall

**Solution:**
1. Increase cooldown to 600 seconds
2. Click "Test Manual Ejection"
3. Check if piece is stuck to PEI plate

For more issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Support

Check the Log section in the web interface for real-time debugging information.

For detailed help, see:
- [SETUP.md](SETUP.md) — Setup instructions
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common problems
- [DOCS.md](DOCS.md) — Complete documentation index

---

## License

Personal automation project for Bambu Lab A1.

---

*Print Queue Automation v1.0 — June 2026*
