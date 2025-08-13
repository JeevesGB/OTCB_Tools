import sys
import os
import struct
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QFileDialog, QAction, QScrollArea, QMessageBox, QToolBar
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

# -----------------------------
# TIM Loader
# -----------------------------
def load_tim(filepath):
    with open(filepath, "rb") as f:
        # TIM Header
        magic = f.read(4)
        if magic != b'\x10\x00\x00\x00':
            raise ValueError("Not a valid TIM file")

        flags = struct.unpack("<I", f.read(4))[0]
        has_clut = flags & 0x08 != 0
        bpp_mode = flags & 0x07  # 0=4bpp, 1=8bpp, 2=16bpp, 3=24bpp

        # Read CLUT if present
        palette = []
        if has_clut:
            clut_size = struct.unpack("<I", f.read(4))[0]
            f.read(4)  # skip CLUT X, Y
            colors = struct.unpack("<HH", f.read(4))
            num_colors = colors[0]
            num_palettes = colors[1]
            # Read actual CLUT data
            f.seek(-4, 1)
            clut_data = f.read(clut_size - 4)
            palette = []
            for i in range(0, len(clut_data), 2):
                if i + 1 < len(clut_data):
                    raw_color = struct.unpack("<H", clut_data[i:i + 2])[0]
                    r = (raw_color & 0x1F) << 3
                    g = ((raw_color >> 5) & 0x1F) << 3
                    b = ((raw_color >> 10) & 0x1F) << 3
                    palette.append((r, g, b))

        # Image block
        image_size_data = f.read(4)
        if len(image_size_data) != 4:
            raise ValueError("Unexpected EOF while reading image size")
        image_size = struct.unpack("<I", image_size_data)[0]
        image_data = f.read(image_size - 4)

        # Width & height
        if len(image_data) < 4:
            raise ValueError("Unexpected EOF while reading image dimensions")
        width, height = struct.unpack("<HH", image_data[:4])

        # Extract pixel data (simple 16bpp handling)
        pixels = image_data[4:]
        if bpp_mode == 2:  # 16bpp
            img = QImage(width, height, QImage.Format_RGB888)
            idx = 0
            for y in range(height):
                for x in range(width):
                    if idx + 1 < len(pixels):
                        raw_color = struct.unpack("<H", pixels[idx:idx + 2])[0]
                        r = (raw_color & 0x1F) << 3
                        g = ((raw_color >> 5) & 0x1F) << 3
                        b = ((raw_color >> 10) & 0x1F) << 3
                        img.setPixelColor(x, y, Qt.qRgb(r, g, b))
                    idx += 2
            return img
        else:
            raise NotImplementedError(f"BPP mode {bpp_mode} not yet implemented")

# -----------------------------
# Main Window
# -----------------------------
class TIMViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PlayStation TIM Viewer")
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_label)
        self.setCentralWidget(self.scroll_area)

        self.files = []
        self.current_index = -1
        self.scale_factor = 1.0

        self.create_actions()
        self.create_toolbar()

    def create_actions(self):
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)

        next_action = QAction("Next", self)
        next_action.triggered.connect(self.show_next)

        prev_action = QAction("Previous", self)
        prev_action.triggered.connect(self.show_previous)

        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(lambda: self.zoom(1.25))

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(lambda: self.zoom(0.8))

        fit_action = QAction("Fit to Window", self)
        fit_action.triggered.connect(self.fit_to_window)

        self.actions = {
            "open": open_action,
            "next": next_action,
            "prev": prev_action,
            "zoom_in": zoom_in_action,
            "zoom_out": zoom_out_action,
            "fit": fit_action
        }

    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.addAction(self.actions["open"])
        toolbar.addAction(self.actions["prev"])
        toolbar.addAction(self.actions["next"])
        toolbar.addAction(self.actions["zoom_in"])
        toolbar.addAction(self.actions["zoom_out"])
        toolbar.addAction(self.actions["fit"])
        self.addToolBar(toolbar)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open TIM File", "", "TIM Images (*.tim)")
        if file_path:
            folder = os.path.dirname(file_path)
            self.files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".tim")]
            self.files.sort()
            self.current_index = self.files.index(file_path)
            self.load_image(file_path)

    def load_image(self, file_path):
        try:
            img = load_tim(file_path)
            self.image_label.setPixmap(QPixmap.fromImage(img))
            self.scale_factor = 1.0
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load {os.path.basename(file_path)}:\n{str(e)}")

    def show_next(self):
        if self.files:
            self.current_index = (self.current_index + 1) % len(self.files)
            self.load_image(self.files[self.current_index])

    def show_previous(self):
        if self.files:
            self.current_index = (self.current_index - 1) % len(self.files)
            self.load_image(self.files[self.current_index])

    def zoom(self, factor):
        self.scale_factor *= factor
        if self.image_label.pixmap():
            self.image_label.resize(self.scale_factor * self.image_label.pixmap().size())

    def fit_to_window(self):
        if self.image_label.pixmap():
            self.scale_factor = min(
                self.scroll_area.width() / self.image_label.pixmap().width(),
                self.scroll_area.height() / self.image_label.pixmap().height()
            )
            self.image_label.resize(self.scale_factor * self.image_label.pixmap().size())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = TIMViewer()
    viewer.show()
    sys.exit(app.exec_())
