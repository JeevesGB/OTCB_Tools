import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk
from pathlib import Path
import os

from tim_extractor import extract_tim_images  # Import backend

class TIMExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PS1 TIM Extractor")
        self.root.geometry("800x600")

        self.tim_images = []

        # Top buttons
        top_frame = tk.Frame(root)
        top_frame.pack(fill=tk.X, pady=5)

        btn_open = tk.Button(top_frame, text="Open BIN File", command=self.open_file)
        btn_open.pack(side=tk.LEFT, padx=5)

        btn_save_tim = tk.Button(top_frame, text="Save All TIMs", command=self.save_all_tim)
        btn_save_tim.pack(side=tk.LEFT, padx=5)

        btn_save_png = tk.Button(top_frame, text="Save All PNGs", command=self.save_all_png)
        btn_save_png.pack(side=tk.LEFT, padx=5)

        # Scrollable canvas for thumbnails
        self.canvas = tk.Canvas(root, bg="#222")
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select BIN File",
            filetypes=[("BIN files", "*.BIN"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            self.tim_images = extract_tim_images(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract TIM images:\n{e}")
            return

        if not self.tim_images:
            messagebox.showinfo("No TIMs Found", "No TIM textures were found in this file.")
            return

        self.show_thumbnails()

    def show_thumbnails(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        for t in self.tim_images:
            thumb = t.image.copy()
            thumb.thumbnail((64, 64))
            img_tk = ImageTk.PhotoImage(thumb)

            lbl = tk.Label(self.scroll_frame, image=img_tk, bg="#333")
            lbl.image = img_tk  # Keep reference
            lbl.pack(padx=5, pady=5, anchor="w")
            lbl.bind("<Button-1>", lambda e, tim=t: self.show_full_image(tim))

    def show_full_image(self, tim):
        win = tk.Toplevel(self.root)
        win.title(f"TIM #{tim.index}")
        img_tk = ImageTk.PhotoImage(tim.image)
        lbl = tk.Label(win, image=img_tk)
        lbl.image = img_tk
        lbl.pack()

    def save_all_tim(self):
        if not self.tim_images:
            return
        folder = filedialog.askdirectory(title="Select Output Folder")
        if not folder:
            return
        for t in self.tim_images:
            out_path = Path(folder) / f"tim_{t.index}.tim"
            out_path.write_bytes(t.raw_bytes)
        messagebox.showinfo("Done", f"Saved {len(self.tim_images)} TIM files.")

    def save_all_png(self):
        if not self.tim_images:
            return
        folder = filedialog.askdirectory(title="Select Output Folder")
        if not folder:
            return
        for t in self.tim_images:
            out_path = Path(folder) / f"tim_{t.index}.png"
            t.image.save(out_path)
        messagebox.showinfo("Done", f"Saved {len(self.tim_images)} PNG files.")


if __name__ == "__main__":
    root = tk.Tk()
    app = TIMExtractorGUI(root)
    root.mainloop()
