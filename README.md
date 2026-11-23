# Video Converter 480p x264 — Advanced & Subtitle Safe

Aplikasi desktop lokal untuk **mengkonversi dan mengecilkan semua jenis video** (x264, x265/HEVC, dll.) menjadi **format x264 dengan resolusi 480p**, ukuran file lebih kecil, dilengkapi panel monitoring real-time, tombol stop darurat, dan jaminan **subtitle aman tanpa rusak**.

Dibuat dengan Python + Tkinter untuk antarmuka grafis yang ringan dan FFmpeg untuk mesin video.

---

## 🎯 Fitur Unggulan

1. **Konversi Universal ke x264** — Mendukung input x265, x264, VP9, AV1, dll., dikonversi ke standar x264 yang kompatibel di semua perangkat.
2. **Resolusi Otomatis 480p** — Menjaga aspek rasio agar tidak gepeng (`scale=-2:480`).
3. **Kompresi Ukuran File** — Diatur melalui CRF (Konstanta Kualitas, default 24), preset encoder, dan audio AAC 128 kbps.
4. **Subtitle 100% Aman** — Menyalin semua stream subtitle (`-c:s copy`) tanpa di-encode ulang, sehingga subtitle (SRT, ASS, PGS, dll.) tidak rusak, terpotong, atau hilang.
5. **Monitoring Real-Time** — Menampilkan:
   - Persentase progress (`%`).
   - Bitrate saat ini.
   - Kecepatan proses (*Speed*, misal `1.5x`).
   - Estimasi waktu selesai (*ETA* / Sisa Waktu).
6. **Tombol Stop Darurat** — Menghentikan proses FFmpeg secara instan dan membersihkan file sisa jika dibatalkan di tengah jalan.
7. **Pilih Folder Fleksibel** — Tentukan folder sumber video dan folder hasil konversi dengan mudah.

---

## 📦 Format Video yang Didukung

- **Input:** `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`, `.flv`, `.m4v`, `.ts`, `.wmv`
- **Output:** `.mkv` (Sangat disarankan agar semua jenis subtitle aman) atau `.mp4`

---

## 🛠️ Persyaratan Sistem

| Komponen | Keterangan |
|----------|------------|
| Python 3.8+ | Diperlukan untuk menjalankan `app.py` |
| tkinter | Bawaan pustaka standar Python |
| FFmpeg | **Wajib.** Download dari [ffmpeg.org](https://ffmpeg.org/download.html) dan pastikan terdaftar di PATH. |
| PyInstaller | Opsional (hanya jika ingin membuat file `.exe` / executable tunggal). |

---

## 🖥️ Cara Menjalankan & Build di Windows

### A. Langsung Jalankan (Tanpa Build)
1. Pastikan Python & FFmpeg sudah terinstall.
2. Double-click file **`run.bat`** di folder ini (atau buka CMD dan ketik `python app.py`).

### B. Membuat File `.exe` Tunggal
1. Double-click file **`build.bat`**.
2. PyInstaller akan otomatis merakit aplikasi.
3. Hasil file `.exe` ada di folder **`dist\VideoConverter.exe`**. Anda bisa menyalin dan menjalankannya kapan saja.

---

## 🐧 Cara Menjalankan & Build di Linux

### A. Langsung Jalankan
1. Install dependensi:
   ```bash
   sudo apt update && sudo apt install -y ffmpeg python3-tk
   ```
2. Jalankan:
   ```bash
   python3 app.py
   ```

### B. Membuat Executable Linux
1. Jalankan script build Linux:
   ```bash
   chmod +x build_linux.sh
   ./build_linux.sh
   ```
2. Hasil binary native ada di `dist/VideoConverter`.

---

## 📖 Cara Penggunaan Aplikasi

1. Buka aplikasi (via `run.bat`, `python app.py`, atau `.exe`).
2. **Folder Sumber:** Klik **Pilih Folder...** dan arahkan ke folder yang berisi video-video Anda.
3. **Folder Hasil:** Klik **Pilih Folder...** dan tentukan tempat penyimpanan video hasil konversi 480p.
4. **Pengaturan:** Pilih CRF (default 24), preset encoder, dan format output (`.mkv` dianjurkan).
5. Klik **🚀 Mulai Konversi**.
6. **Pantau Real-Time:** 
   - Progress bar dan persentase (%) bergerak otomatis.
   - Lihat **Bitrate saat ini**, **Kecepatan (*Speed*)**, dan **Estimasi Selesai (*ETA*)**.
   - Jika ingin membatalkan, klik **⏹ Berhentikan** (proses FFmpeg langsung berhenti total seketika).
7. Selesai! Klik **📂 Buka Folder Hasil** untuk melihat hasilnya.

---

## 📂 Struktur Berkas

```
diarverter/
├── app.py              # Script utama (GUI Tkinter + Parser FFmpeg Real-Time)
├── build.bat           # Script pembuat .exe di Windows
├── build_linux.sh      # Script pembuat binary di Linux
├── run.bat             # Script shortcut jalankan di Windows
└── README.md           # Panduan lengkap
```

---
Made with Python & FFmpeg
