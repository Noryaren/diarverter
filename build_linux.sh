#!/bin/bash
echo "=== Building VideoConverter for Linux ==="
python3 -m pip install --user pyinstaller || pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "VideoConverter" app.py
echo ""
echo "=== Selesai! Binary Linux ada di: dist/VideoConverter ==="
