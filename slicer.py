"""
Slic3r lightweight slicer for Bambu Lab A1.
Simple, reliable, ~30MB, works on Render.
"""

import os
import subprocess
from pathlib import Path

def _find_slic3r() -> str:
    candidates = [
        Path(__file__).parent / "vendor" / "slic3r",
        Path(__file__).parent / "vendor" / "Slic3r" / "slic3r.pl",
        Path("/usr/bin/slic3r"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return "slic3r"

SLIC3R = _find_slic3r()

def slice_stl(
    input_file: str,
    output_dir: str = None,
    layer_height: float = 0.2,
    infill: int = 15,
    supports: str = "none",  # "none", "linear", "grid", "tree"
    filament_color: str = "#FF8000",
    plate_x_mm: float = 256.0,
    plate_y_mm: float = 256.0,
    cooldown_seconds: int = 300,
    piece_height_mm: float = 5.0,
    **kwargs
) -> tuple[bool, str, str]:
    """
    Slice STL/OBJ/3MF with Slic3r.
    Returns (success, output_gcode_path, message).
    """
    input_path = Path(input_file)
    if not input_path.exists():
        return False, "", f"File not found: {input_file}"

    output_dir = Path(output_dir or input_path.parent)
    output_gcode = output_dir / (input_path.stem + ".gcode")

    # Slic3r CLI args for Bambu A1
    cmd = [
        _find_slic3r(),
        "--layer-height", str(layer_height),
        "--infill-density", str(infill),
        "--perimeters", "3",
        "--bed-size", f"{int(plate_x_mm)},{int(plate_y_mm)}",
        "--nozzle-diameter", "0.4",
        "--filament-diameter", "1.75",
        "--extrusion-width", "0.4",
    ]

    if supports != "none":
        cmd += ["--support-material"]
        if supports == "tree":
            cmd += ["--support-material-style", "tree"]

    cmd += [
        "--output", str(output_gcode),
        str(input_path),
    ]

    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if r.returncode != 0:
            err = (r.stderr or r.stdout)[-200:]
            return False, "", f"Slic3r error: {err}"

        if not output_gcode.exists():
            return False, "", "No output file generated"

        # Success
        size_mb = output_gcode.stat().st_size / (1024 * 1024)
        return True, str(output_gcode), f"Done ({size_mb:.1f}MB)"

    except subprocess.TimeoutExpired:
        return False, "", "Slicing timeout (5 min)"
    except FileNotFoundError:
        return False, "", f"Slic3r not found. Reinstall: bash build.sh"
    except Exception as e:
        return False, "", f"Error: {str(e)[:100]}"

def prusaslicer_available() -> bool:
    """Check if Slic3r is available."""
    try:
        r = subprocess.run([_find_slic3r(), "--version"], capture_output=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False
