"""
Local tool — slice STL/OBJ/3MF with YOUR PrusaSlicer, upload result to Render.
Run this once to slice + queue a file for printing.
"""

import sys
import os
import subprocess
import requests
from pathlib import Path

# Render cloud sito URL — metti qui il tuo
RENDER_URL = "https://printqueue-yjfk.onrender.com"
SITE_PASSWORD = "Leonardo Carlo Manzone"

# Percorso a PrusaSlicer — prova Bambu Studio prima, poi standalone
PRUSA_PATHS = [
    r"C:\Program Files\Bambu Studio\prusa-slicer.exe",
    r"C:\Program Files\Bambu Lab\Bambu Studio\prusa-slicer.exe",
    r"C:\Users\Utente\AppData\Local\Bambu Studio\prusa-slicer.exe",
    r"C:\Program Files\PrusaSlicer\prusa-slicer.exe",
]

PRUSA_PATH = None
for p in PRUSA_PATHS:
    if Path(p).exists():
        PRUSA_PATH = p
        break

def slice_file(stl_path: str, layer_h=0.2, infill=15, supports="none", color="#FF8000") -> str:
    """Slice con il tuo PrusaSlicer locale. Ritorna path a .gcode generato."""
    stl_path = Path(stl_path).resolve()

    if not PRUSA_PATH:
        print("ERRORE: PrusaSlicer non trovato!")
        print("\nSoluzioni:")
        print("1. Installa Bambu Studio (lo contiene): https://www.bambulab.com/en/download/studio")
        print("2. O installa PrusaSlicer standalone: https://www.prusa3d.com/en/product/prusaslicer-3/")
        print("\nPercorsi cercati:")
        for p in PRUSA_PATHS:
            print(f"  - {p}")
        sys.exit(1)

    out_gcode = stl_path.parent / (stl_path.stem + "_printqueue.gcode")

    # Minimal config for slicing
    cfg_content = f"""
[print]
layer_height = {layer_h}
infill_density = {infill}
support_material = {"1" if supports != "none" else "0"}

[filament]
filament_colour = {color}
"""
    cfg_path = stl_path.parent / "prusa_slice.ini"
    cfg_path.write_text(cfg_content)

    cmd = [
        str(PRUSA_PATH),
        "--slice",
        "--export-gcode",
        "--output", str(out_gcode),
        str(stl_path),
    ]

    print(f"Slicing {stl_path.name}...")
    print(f"  Layer: {layer_h}mm | Infill: {infill}% | Supporti: {supports}")

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"Slicing fallito:\n{r.stderr}")
        sys.exit(1)

    if not out_gcode.exists():
        print(f"Slicing non ha generato file: {out_gcode}")
        sys.exit(1)

    print(f"✓ Generato: {out_gcode.name}")
    cfg_path.unlink(missing_ok=True)
    return str(out_gcode)

def upload_to_render(gcode_path: str):
    """Upload il gcode a Render e aggiungi alla coda."""
    gcode_path = Path(gcode_path).resolve()

    # Step 1: login al sito cloud
    s = requests.Session()
    r = s.post(f"{RENDER_URL}/login", data={"password": SITE_PASSWORD})
    if r.status_code != 200 or "/login" in r.url:
        print("Login fallito. Password sbagliata o sito non raggiungibile.")
        sys.exit(1)

    print(f"Connesso a {RENDER_URL}")

    # Step 2: upload gcode
    with open(gcode_path, "rb") as f:
        files = {"files": (gcode_path.name, f)}
        r = s.post(f"{RENDER_URL}/api/upload", files=files)

    if not r.ok:
        print(f"Upload fallito: {r.text[:200]}")
        sys.exit(1)

    data = r.json()
    if not data.get("ok"):
        print(f"Upload errore: {data.get('error')}")
        sys.exit(1)

    print(f"✓ Uploaded: {gcode_path.name}")
    print(f"✓ In coda su {RENDER_URL}")

def find_file(filename: str) -> str:
    """Cerca il file. Prova percorso relativo, poi Desktop/Documents/Downloads."""
    p = Path(filename)
    if p.exists():
        return str(p.resolve())

    # Cerca nelle cartelle comuni
    search_dirs = [
        Path.home() / "Desktop",
        Path.home() / "Documents",
        Path.home() / "Downloads",
        Path.home(),
    ]

    print(f"Cerco {filename}...")
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for found in search_dir.rglob(f"*{Path(filename).suffix}"):
            if found.name == filename:
                print(f"✓ Trovato: {found}")
                return str(found)

    raise FileNotFoundError(f"File non trovato: {filename}\nCerca in Desktop, Documents, o Downloads")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python upload_gcode.py <file.stl|obj|3mf> [layer_mm] [infill_%] [supporti]")
        print("Esempi:")
        print("  python upload_gcode.py Vortex_Ball_Fidget.stl")
        print("  python upload_gcode.py Vortex_Ball_Fidget.stl 0.1 20 tree")
        sys.exit(1)

    filename = sys.argv[1]
    stl_file = find_file(filename)
    layer_h = float(sys.argv[2]) if len(sys.argv) > 2 else 0.2
    infill = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    supports = sys.argv[4] if len(sys.argv) > 4 else "none"

    gcode = slice_file(stl_file, layer_h, infill, supports)
    upload_to_render(gcode)
    print("\n✓ Pronto per stampare!")
