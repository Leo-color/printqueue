#!/bin/bash
set -e

# Install Python deps (required)
pip install -r requirements.txt

# Install PrusaSlicer into the PROJECT directory (only writable path on Render).
# /opt is read-only, so we use ./vendor relative to the repo root.
VENDOR="$(pwd)/vendor"
echo "Installing PrusaSlicer into $VENDOR ..."
mkdir -p "$VENDOR"

URL="https://github.com/prusa3d/PrusaSlicer/releases/download/version_2.7.4/PrusaSlicer-2.7.4+linux-x64-GTK2-202404050928.AppImage"

wget -q --timeout=180 "$URL" -O /tmp/prusaslicer.AppImage || {
    echo "Download PrusaSlicer fallito — slicing disabilitato"; exit 0; }

chmod +x /tmp/prusaslicer.AppImage

cd /tmp
./prusaslicer.AppImage --appimage-extract > /dev/null 2>&1 || {
    echo "Estrazione fallita — slicing disabilitato"; exit 0; }

# Copy just the binary + needed libs folder
BIN="$(find /tmp/squashfs-root -name prusa-slicer -type f | head -1)"
if [ -z "$BIN" ]; then
    echo "Binary non trovato — slicing disabilitato"; exit 0;
fi

# Copy the whole extracted tree (binary needs its bundled libs)
cp -r /tmp/squashfs-root "$VENDOR/squashfs-root"
ln -sf "$VENDOR/squashfs-root/usr/bin/prusa-slicer" "$VENDOR/prusa-slicer" 2>/dev/null || true

echo "PrusaSlicer installato in $VENDOR"
"$VENDOR/squashfs-root/usr/bin/prusa-slicer" --version 2>&1 | head -1 || echo "(version check non disponibile)"
