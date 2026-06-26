#!/bin/bash
set -e

# Install Python deps
pip install -r requirements.txt

# Install Slic3r (open source, lightweight slicer with CLI)
echo "Installing Slic3r..."
mkdir -p ./vendor
cd ./vendor

# Download Slic3r portable
wget -q --timeout=120 \
  "https://github.com/slic3r/Slic3r/releases/download/1.2.9/Slic3r-1.2.9-linux-x86_64.tar.bz2" \
  -O slic3r.tar.bz2 || { echo "Download Slic3r fallito"; exit 0; }

tar -xjf slic3r.tar.bz2 || { echo "Extract fallito"; exit 0; }
ln -sf "$(find . -name slic3r -type f | head -1)" slic3r
chmod +x slic3r

cd ..
echo "Slic3r OK: $(./vendor/slic3r --version 2>&1 || echo 'version check skipped')"
