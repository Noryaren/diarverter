import os
import sys
import subprocess
import threading
import queue
import time
import re
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class VideoConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("diarverter — Video Converter 480p x264")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Variables
        self.source_dir = tk.StringVar()
        self.dest_dir = tk.StringVar()
        self.crf_var = tk.StringVar(value="24")
        self.preset_var = tk.StringVar(value="medium")
        self.output_ext_var = tk.StringVar(value=".mkv")

        self.is_converting = False
        self.stop_requested = False
        self.current_process = None
        self.log_queue = queue.Queue()

        self.setup_styles()
        self.create_widgets()

        # Check ffmpeg on startup
        self.check_ffmpeg()

        # Start queue processor for thread-safe UI logging & stats
        self.process_queue()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        BG_COLOR = "#f4f6f9"
        self.root.configure(bg=BG_COLOR)

        style.configure('.', background=BG_COLOR, font=('Segoe UI', 10))
        style.configure('TLabel', background=BG_COLOR, font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#2c3e50')
        style.configure('Subheader.TLabel', font=('Segoe UI', 9, 'italic'), foreground='#7f8c8d')
        style.configure('TButton', font=('Segoe UI', 10), padding=5)
        style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'), foreground='#ffffff', background='#2980b9')

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header_frame, text="🎬 diarverter", style='Header.TLabel').pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Nama Asli Tetap • Subtitle Aman • Auto 480p", style='Subheader.TLabel').pack(side=tk.LEFT, padx=10, pady=5)

        # Folder Selection Frame
        folder_frame = ttk.LabelFrame(main_frame, text=" Direktori Sumber & Tujuan ", padding=10)
        folder_frame.pack(fill=tk.X, pady=(0, 8))
        folder_frame.columnconfigure(1, weight=1)

        ttk.Label(folder_frame, text="Folder Sumber:").grid(row=0, column=0, sticky=tk.W, pady=4)
        ttk.Entry(folder_frame, textvariable=self.source_dir, font=('Segoe UI', 10)).grid(row=0, column=1, sticky=tk.EW, padx=8, pady=4)
        ttk.Button(folder_frame, text="Pilih Folder...", command=self.browse_source).grid(row=0, column=2, pady=4)

        ttk.Label(folder_frame, text="Folder Hasil:").grid(row=1, column=0, sticky=tk.W, pady=4)
        ttk.Entry(folder_frame, textvariable=self.dest_dir, font=('Segoe UI', 10)).grid(row=1, column=1, sticky=tk.EW, padx=8, pady=4)
        ttk.Button(folder_frame, text="Pilih Folder...", command=self.browse_dest).grid(row=1, column=2, pady=4)

        # Settings Frame
        settings_frame = ttk.LabelFrame(main_frame, text=" Pengaturan Konversi ", padding=10)
        settings_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(settings_frame, text="Kualitas (CRF):").grid(row=0, column=0, sticky=tk.W, pady=4, padx=4)
        crf_combo = ttk.Combobox(settings_frame, textvariable=self.crf_var, values=["20", "22", "24", "26", "28"], width=8, state="readonly")
        crf_combo.grid(row=0, column=1, sticky=tk.W, pady=4, padx=4)
        ttk.Label(settings_frame, text="(Lebih besar = ukuran lebih kecil. Default: 24)").grid(row=0, column=2, sticky=tk.W, padx=4)

        ttk.Label(settings_frame, text="Preset Encoder:").grid(row=1, column=0, sticky=tk.W, pady=4, padx=4)
        preset_combo = ttk.Combobox(settings_frame, textvariable=self.preset_var, values=["fast", "medium", "slow"], width=8, state="readonly")
        preset_combo.grid(row=1, column=1, sticky=tk.W, pady=4, padx=4)
        ttk.Label(settings_frame, text="(medium = seimbang kecepatan & kompresi)").grid(row=1, column=1, sticky=tk.W, padx=4)

        ttk.Label(settings_frame, text="Format Output:").grid(row=2, column=0, sticky=tk.W, pady=4, padx=4)
        ext_combo = ttk.Combobox(settings_frame, textvariable=self.output_ext_var, values=[".mkv", ".mp4"], width=8, state="readonly")
        ext_combo.grid(row=2, column=1, sticky=tk.W, pady=4, padx=4)
        ttk.Label(settings_frame, text="(.mkv sangat disarankan agar semua jenis subtitle aman tanpa rusak)").grid(row=2, column=2, sticky=tk.W, padx=4)

        # Action & Live Stats Frame
        stats_frame = ttk.LabelFrame(main_frame, text=" Progress & Statistik Real-Time ", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 8))

        # Buttons
        btn_box = ttk.Frame(stats_frame)
        btn_box.pack(fill=tk.X, pady=(0, 8))

        self.start_btn = ttk.Button(btn_box, text="🚀 Mulai Konversi", command=self.start_conversion, style='Accent.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = ttk.Button(btn_box, text="⏹ Berhentikan", command=self.stop_conversion, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.open_dest_btn = ttk.Button(btn_box, text="📂 Buka Folder Hasil", command=self.open_destination_folder)
        self.open_dest_btn.pack(side=tk.LEFT)

        # Progress Bar & Percentage
        prog_box = ttk.Frame(stats_frame)
        prog_box.pack(fill=tk.X, pady=4)

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(prog_box, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.pct_label = ttk.Label(prog_box, text="0.0%", font=('Segoe UI', 10, 'bold'), width=7)
        self.pct_label.pack(side=tk.RIGHT)

        # Details Stats Grid
        info_grid = ttk.Frame(stats_frame)
        info_grid.pack(fill=tk.X, pady=(4, 0))

        self.status_label = ttk.Label(info_grid, text="Status: Siap", font=('Segoe UI', 9, 'bold'))
        self.status_label.grid(row=0, column=0, sticky=tk.W, pady=2, columnspan=2)

        ttk.Label(info_grid, text="Bitrate Saat Ini:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.bitrate_label = ttk.Label(info_grid, text="-", font=('Consolas', 9))
        self.bitrate_label.grid(row=1, column=1, sticky=tk.W)

        ttk.Label(info_grid, text="Kecepatan (Speed):").grid(row=1, column=2, sticky=tk.W, padx=(20, 10))
        self.speed_label = ttk.Label(info_grid, text="-", font=('Consolas', 9))
        self.speed_label.grid(row=1, column=3, sticky=tk.W)

        ttk.Label(info_grid, text="Estimasi Selesai (ETA):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=2)
        self.eta_label = ttk.Label(info_grid, text="-", font=('Consolas', 9))
        self.eta_label.grid(row=2, column=1, sticky=tk.W, pady=2)

        # Log / Console Output Frame
        log_frame = ttk.LabelFrame(main_frame, text=" Log Proses & FFmpeg ", padding=6)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(2, 0))

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=10, font=('Consolas', 9), bg="#1e1e1e", fg="#d4d4d4")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def browse_source(self):
        dir_path = filedialog.askdirectory(title="Pilih Folder Sumber Video")
        if dir_path:
            self.source_dir.set(dir_path)
            if not self.dest_dir.get():
                self.dest_dir.set(os.path.join(dir_path, "hasil_480p"))

    def browse_dest(self):
        dir_path = filedialog.askdirectory(title="Pilih Folder Hasil Video")
        if dir_path:
            self.dest_dir.set(dir_path)

    def open_destination_folder(self):
        dest = self.dest_dir.get()
        if dest and os.path.exists(dest):
            if sys.platform == 'win32':
                os.startfile(dest)
            elif sys.platform == 'darwin':
                subprocess.run(['open', dest])
            else:
                subprocess.run(['xdg-open', dest])
        else:
            messagebox.showwarning("Peringatan", "Folder hasil belum ada atau belum dipilih!")

    def check_ffmpeg(self):
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            self.log("✅ FFmpeg terdeteksi di sistem.\n")
        except (subprocess.SubprocessError, FileNotFoundError):
            self.log("⚠️ PERINGATAN: FFmpeg tidak ditemukan di PATH sistem!\n")
            messagebox.showwarning(
                "FFmpeg Tidak Ditemukan",
                "Aplikasi memerlukan FFmpeg untuk mengconvert video.\nPastikan FFmpeg sudah di-install."
            )

    def log(self, message):
        self.log_queue.put(message)

    def process_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, msg)
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)

    def start_conversion(self):
        src = self.source_dir.get().strip()
        dst = self.dest_dir.get().strip()

        if not src:
            messagebox.showerror("Error", "Silakan pilih Folder Sumber video terlebih dahulu!")
            return
        if not dst:
            messagebox.showerror("Error", "Silakan pilih Folder Hasil video terlebih dahulu!")
            return
        if os.path.abspath(src) == os.path.abspath(dst):
            messagebox.showerror("Error", "Folder Sumber dan Folder Hasil tidak boleh sama persis agar nama file asli tidak tertimpa!")
            return
        if not os.path.exists(src):
            messagebox.showerror("Error", "Folder sumber tidak ditemukan!")
            return

        self.is_converting = True
        self.stop_requested = False
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.pct_label.config(text="0.0%")

        threading.Thread(target=self.run_conversion_process, args=(src, dst), daemon=True).start()

    def stop_conversion(self):
        self.stop_requested = True
        self.status_label.config(text="Status: Menghentikan proses secara paksa...")
        self.log("\n⛔ Tombol STOP ditekan. Menghentikan proses ffmpeg yang sedang berjalan...\n")

        if self.current_process and self.current_process.poll() is None:
            try:
                self.current_process.terminate()
                self.current_process.kill()
            except Exception as e:
                self.log(f"⚠️ Error saat menghentikan proses: {e}\n")

    def get_video_duration(self, file_path):
        try:
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except Exception:
            pass
        return 0.0

    def run_conversion_process(self, src_dir, dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

        video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.m4v', '.ts', '.wmv')
        video_files = []

        for root_path, _, files in os.walk(src_dir):
            for file in files:
                if file.lower().endswith(video_extensions):
                    video_files.append(os.path.join(root_path, file))

        total_files = len(video_files)
        if total_files == 0:
            self.log(f"❌ Tidak ditemukan file video di folder: {src_dir}\n")
            self.finish_conversion("Tidak ada video ditemukan")
            return

        self.log(f"📁 Ditemukan {total_files} file video untuk dikonversi.\n")
        self.log(f"⚙️ Konfigurasi: 480p x264, CRF={self.crf_var.get()}, Preset={self.preset_var.get()}, Subtitle Disalin (-c:s copy)\n")
        self.log(f"🏷️ Catatan: Nama asli video dipertahankan sama persis di folder tujuan.\n")
        self.log("="*70 + "\n")

        success_count = 0
        fail_count = 0

        for index, file_path in enumerate(video_files, start=1):
            if self.stop_requested:
                break

            filename = os.path.basename(file_path)
            name_only, ext = os.path.splitext(filename)
            output_ext = self.output_ext_var.get()

            # MEMPERTAHANKAN NAMA ASLI VIDEO (TANPA TAMBAHAN _480p)
            output_filename = f"{name_only}{output_ext}"
            output_path = os.path.join(dest_dir, output_filename)

            self.log(f"[{index}/{total_files}] Memproses: {filename} ➔ {output_filename}\n")
            self.status_label.config(text=f"Status: [{index}/{total_files}] Memproses {filename}")

            duration = self.get_video_duration(file_path)

            cmd = [
                "ffmpeg",
                "-y",
                "-i", file_path,
                "-map", "0",
                "-c:v", "libx264",
                "-crf", self.crf_var.get(),
                "-preset", self.preset_var.get(),
                "-vf", "scale=-2:480",
                "-c:a", "aac",
                "-b:a", "128k",
                "-c:s", "copy",
                output_path
            ]

            try:
                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='ignore'
                )

                while True:
                    if self.stop_requested:
                        break

                    line = self.current_process.stdout.readline()
                    if line == '' and self.current_process.poll() is not None:
                        break

                    if line:
                        if duration == 0.0:
                            dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", line)
                            if dur_match:
                                h, m, s = map(float, dur_match.groups())
                                duration = h * 3600 + m * 60 + s

                        time_match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
                        if time_match and duration > 0:
                            th, tm, ts = map(float, time_match.groups())
                            current_secs = th * 3600 + tm * 60 + ts
                            pct = min(100.0, (current_secs / duration) * 100)

                            bitrate_match = re.search(r"bitrate=\s*([^\s]+)", line)
                            bitrate_str = bitrate_match.group(1) if bitrate_match else "-"

                            speed_match = re.search(r"speed=\s*([^\s]+)", line)
                            speed_str = speed_match.group(1) if speed_match else "-"

                            eta_str = "Menghitung..."
                            try:
                                speed_val = float(speed_str.rstrip('x')) if speed_str != '-' and 'x' in speed_str else 0.0
                                if speed_val > 0:
                                    rem_secs = (duration - current_secs) / speed_val
                                    mins, secs = divmod(int(rem_secs), 60)
                                    eta_str = f"{mins}m {secs}s"
                            except Exception:
                                pass

                            self.root.after(0, lambda p=pct, b=bitrate_str, sp=speed_str, et=eta_str: self.update_live_stats(p, b, sp, et))

                return_code = self.current_process.poll()

                if self.stop_requested:
                    self.log(f"   ⛔ Dihentikan oleh pengguna: {filename}\n")
                    if os.path.exists(output_path):
                        try:
                            os.remove(output_path)
                        except:
                            pass
                    break

                if return_code == 0:
                    success_count += 1
                    self.log(f"   ✅ Selesai: {output_filename}\n")
                else:
                    fail_count += 1
                    self.log(f"   ❌ Gagal mengkonversi: {filename} (Exit code: {return_code})\n")

            except Exception as e:
                if not self.stop_requested:
                    fail_count += 1
                    self.log(f"   ❌ Error pada {filename}: {str(e)}\n")

            overall_progress = (index / total_files) * 100
            self.progress_var.set(overall_progress)

        if self.stop_requested:
            self.log("="*70 + "\n")
            self.log(f"🛑 Proses dibatalkan oleh pengguna. Berhasil sebelumnya: {success_count}\n")
            self.finish_conversion("Dihentikan")
        else:
            self.log("="*70 + "\n")
            self.log(f"🎉 Semua Proses Selesai! Berhasil: {success_count}, Gagal: {fail_count}\n")
            self.finish_conversion("Selesai")

    def update_live_stats(self, pct, bitrate, speed, eta):
        self.progress_var.set(pct)
        self.pct_label.config(text=f"{pct:.1f}%")
        self.bitrate_label.config(text=bitrate)
        self.speed_label.config(text=speed)
        self.eta_label.config(text=eta)

    def finish_conversion(self, status_text):
        self.is_converting = False
        self.current_process = None
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text=f"Status: {status_text}")
        if status_text == "Selesai":
            messagebox.showinfo("Informasi", "Proses konversi video selesai dengan sukses!")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverterApp(root)
    root.mainloop()