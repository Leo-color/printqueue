"""
PrusaSlicer wrapper for Bambu Lab A1 (256x256mm bed, 0.4mm nozzle).
Installed via build.sh during Render deploy.
"""

import os
import subprocess
import tempfile
from pathlib import Path

# PrusaSlicer binary: prefer the one installed by build.sh into ./vendor,
# next to this file. Fall back to env var or system PATH.
_HERE = Path(__file__).resolve().parent
_CANDIDATES = [
    _HERE / "vendor" / "squashfs-root" / "usr" / "bin" / "prusa-slicer",
    _HERE / "vendor" / "prusa-slicer",
    Path(os.getenv("PRUSASLICER_BIN", "")) if os.getenv("PRUSASLICER_BIN") else None,
    Path("/usr/bin/prusa-slicer"),
]

def _find_bin() -> str:
    for c in _CANDIDATES:
        if c and Path(c).exists():
            return str(c)
    return "prusa-slicer"  # last resort: PATH

PRUSA_BIN = _find_bin()

# Bambu A1 base config
BAMBU_A1_CONFIG = """
[printer]
bed_shape = 0x0,256x0,256x256,0x256
max_print_height = 256
nozzle_diameter = 0.4
filament_diameter = 1.75
printer_technology = FFF
extruder_count = 1
default_filament_profile = Generic PLA
default_print_profile = 0.20mm Quality

[print]
layer_height = {layer_height}
perimeters = 3
fill_density = {infill}%
fill_pattern = gyroid
support_material = {supports}
support_material_style = {support_style}
support_material_threshold = 45
brim_width = 0
skirts = 1

[filament]
filament_type = PLA
filament_colour = {color}
temperature = 220
bed_temperature = 35
"""


def slice_stl(
    stl_path: str,
    output_dir: str,
    layer_height: float = 0.2,
    infill: int = 15,
    supports: str = "none",   # "none", "normal", "tree"
    filament_color: str = "#FF8000",
) -> tuple[bool, str, str]:
    """
    Slice an STL file using PrusaSlicer CLI.
    Returns (success, gcode_path, message).
    """
    stl_path = Path(stl_path)
    out_path = Path(output_dir) / (stl_path.stem + ".gcode")

    # Build config ini
    support_enabled = "1" if supports != "none" else "0"
    support_style = "tree" if supports == "tree" else "normal"

    config_content = BAMBU_A1_CONFIG.format(
        layer_height=layer_height,
        infill=infill,
        supports=support_enabled,
        support_style=support_style,
        color=filament_color,
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        cmd = [
            _find_bin(),
            "--slice",
            "--export-gcode",
            "--load", config_path,
            "--output", str(out_path),
            str(stl_path),
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 min max
        )
        if result.returncode == 0 and out_path.exists():
            return True, str(out_path), "Slicing completato"
        else:
            err = result.stderr[-500:] if result.stderr else "Errore sconosciuto"
            return False, "", f"Slicing fallito: {err}"
    except subprocess.TimeoutExpired:
        return False, "", "Slicing timeout (file troppo complesso)"
    except FileNotFoundError:
        return False, "", "PrusaSlicer non trovato — controlla PRUSASLICER_BIN"
    except Exception as e:
        return False, "", str(e)
    finally:
        os.unlink(config_path)


def prusaslicer_available() -> bool:
    try:
        r = subprocess.run([_find_bin(), "--version"], capture_output=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False
