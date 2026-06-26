#!/bin/bash
# Install Python deps
pip install -r requirements.txt

# Install PrusaSlicer CLI
echo "Downloading PrusaSlicer..."
mkdir -p /opt/prusaslicer
wget -q "https://github.com/prusa3d/PrusaSlicer/releases/download/version_2.7.4/PrusaSlicer-2.7.4+linux-x64-GTK2-202404050928.AppImage" \
  -O /tmp/prusaslicer.AppImage

chmod +x /tmp/prusaslicer.AppImage

# Extract AppImage (no FUSE needed)
cd /tmp && /tmp/prusaslicer.AppImage --appimage-extract > /dev/null 2>&1
cp -r /tmp/squashfs-root/usr/bin/prusa-slicer /opt/prusaslicer/prusa-slicer
chmod +x /opt/prusaslicer/prusa-slicer

echo "PrusaSlicer installed: $(/opt/prusaslicer/prusa-slicer --version 2>&1 | head -1)"
