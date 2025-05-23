import os
import struct
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np

##########################
#### WORK IN PROGRESS ####
##########################

def read_tim(filepath, palette_index=0):
    with open(filepath, 'rb') as f:
        if struct.unpack("<I", f.read(4))[0] != 0x10:
            raise ValueError("Not a TIM file")

        flags = struct.unpack("<I", f.read(4))[0]
        has_clut = flags & 0x08
        bpp_mode = flags & 0x07

        bpp = {0: 4, 1: 8, 2: 16, 3: 24}.get(bpp_mode, None)
        if bpp is None:
            raise ValueError("Unsupported BPP")

        clut = None
        if has_clut:
            clut_size = struct.unpack("<I", f.read(4))[0]
            clut_x, clut_y, clut_w, clut_h = struct.unpack("<4H", f.read(8))
            clut_data = f.read(clut_size - 12)
            clut_colors = np.frombuffer(clut_data, dtype=np.uint16)
            clut = clut_colors.reshape((-1, clut_w))
            if palette_index >= len(clut):
                palette_index = 0  # fallback to first palette
            selected_palette = clut[palette_index]
        else:
            selected_palette = None

        image_size = struct.unpack("<I", f.read(4))[0]
        x, y, w_words, h = struct.unpack("<4H", f.read(8))

        # Convert width from words to pixels
        if bpp == 4:
            w = w_words * 4
        elif bpp == 8:
            w = w_words * 2
        else:
            w = w_words
        raw_data = f.read()

        if bpp == 4:
            num_pixels = w * h
            bytes_needed = (num_pixels + 1) // 2
            pixels = np.frombuffer(raw_data[:bytes_needed], dtype=np.uint8)
            pixels_unpack = np.zeros(num_pixels, dtype=np.uint8)
            for i in range(num_pixels):
                byte = pixels[i // 2]
                pixels_unpack[i] = byte & 0x0F if i % 2 == 0 else (byte >> 4) & 0x0F
            pixels = pixels_unpack.reshape((h, w))
            color_vals = selected_palette[pixels]

        elif bpp == 8:
            pixels = np.frombuffer(raw_data[:w * h], dtype=np.uint8).reshape((h, w))
            color_vals = selected_palette[pixels]

        elif bpp == 16:
            img_array = np.frombuffer(raw_data, dtype=np.uint16).reshape((h, w))
            r = (img_array & 0x1F) << 3
            g = ((img_array >> 5) & 0x1F) << 3
            b = ((img_array >> 10) & 0x1F) << 3
            return Image.merge("RGB", [Image.fromarray(r.astype(np.uint8)),
                                       Image.fromarray(g.astype(np.uint8)),
                                       Image.fromarray(b.astype(np.uint8))])

        elif bpp == 24:
            return Image.frombytes("RGB", (w, h), raw_data[:w * h * 3], "raw", "RGB")

        else:
            raise NotImplementedError("Unsupported BPP")

        r = (color_vals & 0x1F) << 3
        g = ((color_vals >> 5) & 0x1F) << 3
        b = ((color_vals >> 10) & 0x1F) << 3
        return Image.merge("RGB", [Image.fromarray(r.astype(np.uint8)),
                                   Image.fromarray(g.astype(np.uint8)),
                                   Image.fromarray(b.astype(np.uint8))])


class TIMViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TIM Viewer")
        self.geometry("1000x800")

        self.tim_files = []
        self.images = []
        self.tk_images_cache = []  # Cache PhotoImage per image+zoom
        self.palettes = []
        self.palette_indices = []
        self.zoom_levels = []
        self.bpp_modes = []

        self.index = 0

        # Image display
        self.img_label = tk.Label(self)
        self.img_label.pack(pady=10)
        self.img_label.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.img_label.bind("<Button-4>", self.on_mouse_wheel)    # Linux scroll up
        self.img_label.bind("<Button-5>", self.on_mouse_wheel)    # Linux scroll down

        # Status label
        self.status_label = tk.Label(self, text="")
        self.status_label.pack()

        # Controls frame
        ctrl_frame = tk.Frame(self)
        ctrl_frame.pack(pady=5)

        tk.Button(ctrl_frame, text="<< Prev", command=self.prev_image).pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl_frame, text="Next >>", command=self.next_image).pack(side=tk.LEFT, padx=5)

        zoom_frame = tk.Frame(self)
        zoom_frame.pack(pady=5)
        tk.Label(zoom_frame, text="Zoom:").pack(side=tk.LEFT)
        self.zoom_level = tk.IntVar(value=4)
        self.zoom_slider = tk.Scale(zoom_frame, from_=1, to=8, orient=tk.HORIZONTAL,
                                    variable=self.zoom_level, command=lambda e: self.display_image())
        self.zoom_slider.pack(side=tk.LEFT)

        palette_frame = tk.Frame(self)
        palette_frame.pack(pady=5)
        tk.Label(palette_frame, text="Palette:").pack(side=tk.LEFT)
        self.palette_cb = ttk.Combobox(palette_frame, state="readonly")
        self.palette_cb.pack(side=tk.LEFT)
        self.palette_cb.bind("<<ComboboxSelected>>", self.on_palette_change)

        self.debug_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self, text="Show Debug Info", variable=self.debug_var, command=self.display_image).pack(pady=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Select Folder", command=self.select_folder).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Batch Convert to PNG", command=self.batch_convert).pack(side=tk.LEFT, padx=10)

        # Keyboard bindings for left/right arrows
        self.bind("<Left>", lambda e: self.prev_image())
        self.bind("<Right>", lambda e: self.next_image())

    def select_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        all_files = [os.path.join(folder, f) for f in os.listdir(folder)]
        self.tim_files.clear()
        self.images.clear()
        self.tk_images_cache.clear()
        self.palettes.clear()
        self.palette_indices.clear()
        self.zoom_levels.clear()
        self.bpp_modes.clear()

        for path in all_files:
            try:
                with open(path, "rb") as f:
                    if struct.unpack("<I", f.read(4))[0] == 0x10:
                        self.tim_files.append(path)
            except Exception:
                continue

        if not self.tim_files:
            messagebox.showinfo("No Valid Files", "No valid TIM files found.")
            return

        # Gather palette counts, bpp and init state
        for path in self.tim_files:
            try:
                with open(path, 'rb') as f:
                    f.seek(4)
                    flags = struct.unpack("<I", f.read(4))[0]
                    has_clut = flags & 0x08
                    bpp_mode = flags & 0x07
                    bpp = {0: 4, 1: 8, 2: 16, 3: 24}.get(bpp_mode, None)

                    if has_clut:
                        f.seek(12)
                        clut_size = struct.unpack("<I", f.read(4))[0]
                        clut_x, clut_y, clut_w, clut_h = struct.unpack("<4H", f.read(8))
                        f.seek(24)
                        clut_data = f.read(clut_size - 12)
                        clut_colors = np.frombuffer(clut_data, dtype=np.uint16)
                        num_palettes = clut_colors.size // clut_w
                    else:
                        num_palettes = 0

                    self.palettes.append(num_palettes)
                    self.palette_indices.append(0)
                    self.zoom_levels.append(4)
                    self.bpp_modes.append(bpp)
            except Exception:
                self.palettes.append(0)
                self.palette_indices.append(0)
                self.zoom_levels.append(4)
                self.bpp_modes.append(None)

        self.index = 0
        self.load_images()
        self.update_palette_dropdown()
        self.display_image()

    def load_images(self):
        self.images.clear()
        self.tk_images_cache.clear()
        for i, path in enumerate(self.tim_files):
            try:
                img = read_tim(path, palette_index=self.palette_indices[i])
                self.images.append(img)
                self.tk_images_cache.append({})  # Cache dict for zoom levels
            except Exception as e:
                print(f"Failed loading {path}: {e}")
                self.images.append(None)
                self.tk_images_cache.append({})

    def update_palette_dropdown(self):
        palette_count = self.palettes[self.index]
        if palette_count > 1:
            self.palette_cb['values'] = [str(i) for i in range(palette_count)]
            self.palette_cb.current(self.palette_indices[self.index])
            self.palette_cb.config(state="readonly")
        else:
            self.palette_cb.set("N/A")
            self.palette_cb.config(state="disabled")

    def on_palette_change(self, event):
        new_index = int(self.palette_cb.get())
        self.palette_indices[self.index] = new_index
        try:
            self.images[self.index] = read_tim(self.tim_files[self.index], palette_index=new_index)
            self.tk_images_cache[self.index].clear()  # Clear cached zoomed images
            self.display_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reload image with palette {new_index}: {e}")

    def display_image(self):
        if not self.images or self.images[self.index] is None:
            self.img_label.config(image="", text="Failed to load image")
            self.status_label.config(text="")
            return

        zoom = self.zoom_level.get()
        self.zoom_levels[self.index] = zoom

        cache = self.tk_images_cache[self.index]
        if zoom not in cache:
            img = self.images[self.index]
            zoomed_img = img.resize((img.width * zoom, img.height * zoom), Image.NEAREST)
            tk_img = ImageTk.PhotoImage(zoomed_img)
            cache[zoom] = tk_img
        else:
            tk_img = cache[zoom]

        self.img_label.config(image=tk_img, text="")
        self.img_label.image = tk_img

        fname = os.path.basename(self.tim_files[self.index])
        palette_info = f"Palette: {self.palette_indices[self.index]}" if self.palettes[self.index] > 1 else ""
        zoom_info = f"Zoom: {zoom}x"
        debug_info = ""
        if self.debug_var.get():
            debug_info = f" | BPP: {self.bpp_modes[self.index]} | Palettes: {self.palettes[self.index]}"
        status = f"{fname} [{self.index + 1}/{len(self.tim_files)}] {palette_info} {zoom_info}{debug_info}"
        self.status_label.config(text=status)

    def prev_image(self):
        if not self.tim_files:
            return
        self.index = (self.index - 1) % len(self.tim_files)
        self.update_palette_dropdown()
        self.display_image()

    def next_image(self):
        if not self.tim_files:
            return
        self.index = (self.index + 1) % len(self.tim_files)
        self.update_palette_dropdown()
        self.display_image()

    def on_mouse_wheel(self, event):
        if event.num == 4 or event.delta > 0:
            new_zoom = min(self.zoom_level.get() + 1, 8)
        else:
            new_zoom = max(self.zoom_level.get() - 1, 1)
        self.zoom_level.set(new_zoom)
        self.display_image()

    def batch_convert(self):
        if not self.tim_files:
            messagebox.showinfo("No Files", "No files loaded.")
            return
        out_dir = filedialog.askdirectory()
        if not out_dir:
            return

        count = 0
        for i, path in enumerate(self.tim_files):
            try:
                img = read_tim(path, palette_index=self.palette_indices[i])
                base = os.path.basename(path)
                base_noext = os.path.splitext(base)[0]
                out_path = os.path.join(out_dir, f"{base_noext}.png")
                img.save(out_path)
                count += 1
            except Exception as e:
                print(f"Failed to convert {path}: {e}")

        messagebox.showinfo("Batch Conversion", f"Converted {count} files.")


if __name__ == "__main__":
    app = TIMViewer()
    app.mainloop()
