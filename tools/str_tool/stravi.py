import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import time
from threading import Thread

class STRAVITool:
    def __init__(self, root):
        self.root = root
        self.root.title("STRAVI - STR ⇄ AVI Converter")
        self.root.geometry("1920x1080")
        self.root.resizable(False, False)

        self.file_path = None
        self.mode = tk.StringVar(value="STR to AVI")
        self.preview_running = False
        self.preview_thread = None

        self.left_frame = tk.Frame(root, width=500, bg="#f0f0f0")
        self.left_frame.pack(side="left", fill="y")

        self.right_frame = tk.Frame(root, width=1420, bg="black")
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.build_left_ui()
        self.build_right_ui()

    def build_left_ui(self):
        self.label = tk.Label(self.left_frame, text="No file selected", wraplength=480, bg="#f0f0f0")
        self.label.pack(pady=10)

        self.select_button = tk.Button(self.left_frame, text="Select File", width=30, command=self.select_file)
        self.select_button.pack(pady=5)

        self.mode_menu = tk.OptionMenu(self.left_frame, self.mode, "STR to AVI", "AVI to STR")
        self.mode_menu.config(width=28)
        self.mode_menu.pack(pady=5)

        self.play_button = tk.Button(self.left_frame, text="▶ Play", width=30, command=self.play_preview)
        self.play_button.pack(pady=5)

        self.pause_button = tk.Button(self.left_frame, text="⏸ Pause", width=30, command=self.pause_preview)
        self.pause_button.pack(pady=5)

        self.convert_button = tk.Button(self.left_frame, text="🔁 Convert", width=30, command=self.convert)
        self.convert_button.pack(pady=20)

        self.log_label = tk.Label(self.left_frame, text="Log Output", bg="#f0f0f0")
        self.log_label.pack()

        self.log_text = tk.Text(self.left_frame, height=20, width=60)
        self.log_text.pack(padx=10, pady=10)

    def build_right_ui(self):
        self.preview_canvas = tk.Label(self.right_frame, bg="black")
        self.preview_canvas.place(relx=0.5, rely=0.5, anchor="center")

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def select_file(self):
        filetypes = [("STR files", "*.str"), ("AVI files", "*.avi"), ("All files", "*.*")]
        self.file_path = filedialog.askopenfilename(filetypes=filetypes)
        if self.file_path:
            self.label.config(text=f"Selected: {os.path.basename(self.file_path)}")
            self.log(f"Selected file: {self.file_path}")

    def convert(self):
        if not self.file_path:
            messagebox.showwarning("No file", "Please select a file first.")
            return

        self.log(f"Starting conversion: {self.mode.get()}")
        if self.mode.get() == "STR to AVI":
            self.convert_str_to_avi(self.file_path)
        else:
            self.convert_avi_to_str(self.file_path)

    def convert_str_to_avi(self, path):
        self.log(f"Converting STR to AVI: {path}")
        # TODO: Real conversion logic
        self.log("Conversion complete (placeholder).")

    def convert_avi_to_str(self, path):
        self.log(f"Converting AVI to STR: {path}")
        # TODO: Real conversion logic
        self.log("Conversion complete (placeholder).")

    def play_preview(self):
        if not self.file_path:
            self.log("No file selected for preview.")
            return

        if not self.preview_running:
            self.preview_running = True
            ext = os.path.splitext(self.file_path)[1].lower()
            self.log(f"Starting preview: {ext}")
            if ext == ".avi":
                self.preview_thread = Thread(target=self.simulate_avi_preview)
            elif ext == ".str":
                self.preview_thread = Thread(target=self.simulate_str_preview)
            else:
                self.log("Unsupported file format for preview.")
                return
            self.preview_thread.start()

    def pause_preview(self):
        self.preview_running = False
        self.log("Preview paused.")

    def simulate_avi_preview(self):
        frame = 0
        total = 60
        while self.preview_running and frame < total:
            img = Image.new("RGB", (640, 480), (frame * 4 % 255, 128, 128))
            self.display_image(img)
            time.sleep(1 / 30.0)
            frame += 1
        self.preview_running = False
        self.log("AVI preview finished.")

    def simulate_str_preview(self):
        frame = 0
        total = 60
        while self.preview_running and frame < total:
            img = Image.new("RGB", (320, 240), (128, frame * 4 % 255, 128))
            self.display_image(img)
            time.sleep(1 / 15.0)
            frame += 1
        self.preview_running = False
        self.log("STR preview finished.")

    def display_image(self, img):
        # Resize to fit preview window
        img = img.resize((960, 540), Image.NEAREST)
        self.tk_img = ImageTk.PhotoImage(img)
        self.preview_canvas.config(image=self.tk_img)

if __name__ == "__main__":
    root = tk.Tk()
    app = STRAVITool(root)
    root.mainloop()
