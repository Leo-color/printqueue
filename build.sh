#!/bin/bash
set -e

# Install Python deps (required)
pip install -r requirements.txt

# Install PrusaSlicer CLI (optional — sito funziona anche senza)
echo "Downloading PrusaSlicer..."
mkdir -p /opt/prusaslicer

wget -q --timeout=120 \
  "https://github.com/prusa3d/PrusaSlicer/releases/download/version_2.7.4/PrusaSlicer-2.7.4+linux-x64-GTK2-202404050928.AppImage" \
  -O /tmp/prusaslicer.AppImage || { echo "Download PrusaSlicer fallito — slicing disabilitato"; exit 0; }

chmod +x /tmp/prusaslicer.AppImage

# Extract without FUSE
cd /tmp
/tmp/prusaslicer.AppImage --appimage-extract > /dev/null 2>&1 || { echo "Estrazione fallita — slicing disabilitato"; exit 0; }

cp /tmp/squashfs-root/usr/bin/prusa-slicer /opt/prusaslicer/prusa-slicer 2>/dev/null || \
  find /tmp/squashfs-root -name "prusa-slicer" -type f -exec cp {} /opt/prusaslicer/prusa-slicer \; 2>/dev/null || \
  { echo "Binary non trovato — slicing disabilitato"; exit 0; }

chmod +x /opt/prusaslicer/prusa-slicer
echo "PrusaSlicer OK: $(/opt/prusaslicer/prusa-slicer --version 2>&1 | head -1)"
