@echo off
title Build VideoConverter EXE
echo [1/2] Memastikan PyInstaller terinstall...
pip install pyinstaller

echo.
echo [2/2] Memproses pembuatan file .exe (Onefile + GUI)...
pyinstaller --noconfirm --onefile --windowed --name "VideoConverter" app.py

echo.
echo ========================================================
echo Proses Selesai!
echo File .exe dapat ditemukan di dalam folder: dist\VideoConverter.exe
echo ========================================================
pause
