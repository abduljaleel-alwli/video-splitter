import os
import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

# --- UI Setup ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# -----------------------------
# Functions
# -----------------------------

def run_ffmpeg(command, progress_bar, log_box, done_callback):
    """Run FFmpeg command in a separate thread."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    for line in process.stdout:
        log_box.insert("end", line)
        log_box.see("end")
    process.wait()
    done_callback(process.returncode == 0)

def split_video():
    input_file = entry_video.get().strip()
    duration = entry_duration.get().strip()
    mode = mode_var.get()
    fmt = format_var.get().lower()
    output_dir = entry_output.get().strip() or "output_segments"
    prefix = entry_prefix.get().strip() or "part_"

    if not os.path.exists(input_file):
        messagebox.showerror("Error", "⚠️ Video file not found!")
        return

    if not duration.isdigit():
        messagebox.showerror("Error", "Segment duration must be a number!")
        return

    duration = int(duration)
    os.makedirs(output_dir, exist_ok=True)
    output_pattern = os.path.join(output_dir, f"{prefix}%03d.{fmt}")

    # Choose FFmpeg mode
    if mode == "fast":
        command = [
            "ffmpeg", "-i", input_file,
            "-c", "copy", "-map", "0",
            "-f", "segment",
            "-segment_time", str(duration),
            "-reset_timestamps", "1",
            "-avoid_negative_ts", "1",
            output_pattern
        ]
    else:
        command = [
            "ffmpeg", "-i", input_file,
            "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k",
            "-map", "0", "-f", "segment",
            "-segment_time", str(duration),
            "-reset_timestamps", "1",
            output_pattern
        ]

    # UI Feedback
    btn_start.configure(state="disabled")
    progress_bar.set(0)
    log_box.delete("1.0", "end")
    log_box.insert("end", "🚀 Splitting video...\n")

    def on_done(success):
        if success:
            messagebox.showinfo("Done", f"✅ Segments saved in:\n{output_dir}")
        else:
            messagebox.showerror("Error", "Something went wrong during splitting.")
        btn_start.configure(state="normal")
        progress_bar.set(1)

    thread = threading.Thread(target=run_ffmpeg, args=(command, progress_bar, log_box, on_done))
    thread.start()

def browse_video():
    file_path = filedialog.askopenfilename(
        title="Select video file",
        filetypes=[("Video Files", "*.mp4;*.mov;*.avi;*.mkv"), ("All Files", "*.*")]
    )
    if file_path:
        entry_video.delete(0, "end")
        entry_video.insert(0, file_path)

def browse_output():
    folder = filedialog.askdirectory(title="Select output folder")
    if folder:
        entry_output.delete(0, "end")
        entry_output.insert(0, folder)

# -----------------------------
# UI Layout
# -----------------------------

root = ctk.CTk()
root.title("🎬 Video Splitter - FFmpeg")
root.geometry("820x680")
root.resizable(False, False)

title_label = ctk.CTkLabel(
    root,
    text="✂️ Split Video into Segments",
    font=ctk.CTkFont(size=22, weight="bold")
)
title_label.pack(pady=15)

main_frame = ctk.CTkFrame(root, corner_radius=15)
main_frame.pack(padx=20, pady=10, fill="both", expand=True)

# --- Video Input ---
ctk.CTkLabel(main_frame, text="🎥 Select Video File:").pack(pady=5)
frame_video = ctk.CTkFrame(main_frame)
frame_video.pack(pady=5)
entry_video = ctk.CTkEntry(frame_video, width=550)
entry_video.pack(side="left", padx=5)
ctk.CTkButton(frame_video, text="Browse", command=browse_video).pack(side="left")

# --- Segment Duration ---
ctk.CTkLabel(main_frame, text="⏱ Segment Duration (in seconds):").pack(pady=5)
entry_duration = ctk.CTkEntry(main_frame, width=100)
entry_duration.insert(0, "60")
entry_duration.pack()

# --- Mode Selection ---
ctk.CTkLabel(main_frame, text="⚙️ Split Mode:").pack(pady=5)
mode_var = ctk.StringVar(value="fast")
frame_mode = ctk.CTkFrame(main_frame)
frame_mode.pack(pady=5)
ctk.CTkRadioButton(frame_mode, text="⚡ Fast (no re-encode)", variable=mode_var, value="fast").pack(side="left", padx=10)
ctk.CTkRadioButton(frame_mode, text="🎯 Accurate (re-encode)", variable=mode_var, value="accurate").pack(side="left", padx=10)

# --- Output Format ---
ctk.CTkLabel(main_frame, text="📦 Output Format:").pack(pady=5)
format_var = ctk.StringVar(value="mp4")
ctk.CTkOptionMenu(main_frame, variable=format_var, values=["mp4", "mkv", "mov", "avi"]).pack()

# --- Output Folder ---
ctk.CTkLabel(main_frame, text="📂 Output Folder:").pack(pady=5)
frame_output = ctk.CTkFrame(main_frame)
frame_output.pack(pady=5)
entry_output = ctk.CTkEntry(frame_output, width=550)
entry_output.insert(0, "output_segments")
entry_output.pack(side="left", padx=5)
ctk.CTkButton(frame_output, text="Browse", command=browse_output).pack(side="left")

# --- File Prefix ---
ctk.CTkLabel(main_frame, text="📝 File Name Prefix:").pack(pady=5)
entry_prefix = ctk.CTkEntry(main_frame, width=150)
entry_prefix.insert(0, "part_")
entry_prefix.pack(pady=5)

# --- Start Button ---
btn_start = ctk.CTkButton(
    root,
    text="🚀 Start Splitting",
    font=ctk.CTkFont(size=16, weight="bold"),
    fg_color="#00A86B",
    hover_color="#00915F",
    height=45,
    command=split_video
)
btn_start.pack(pady=15)

# --- Progress Bar ---
progress_bar = ctk.CTkProgressBar(root, width=600)
progress_bar.pack(pady=10)
progress_bar.set(0)

# --- Log Box ---
ctk.CTkLabel(root, text="📜 Process Log:").pack(pady=5)
log_box = ctk.CTkTextbox(root, width=750, height=200)
log_box.pack(pady=10)

root.mainloop()
