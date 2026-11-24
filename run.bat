@echo off
title Video Converter 480p x264
echo Menjalankan Aplikasi Video Converter...
python app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ada kesalahan saat menjalankan app.py.
    echo Pastikan Python sudah terinstall dan terdaftar di PATH Windows.
    pause
)
