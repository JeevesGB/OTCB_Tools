import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog,
    QLabel, QPushButton, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QHBoxLayout, QMessageBox, QSplitter
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from tim_core import extract_bin, rebuild_bin

STYLE = "styles.qss"

class TIMTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(".BIN Ripper")
        self.resize(1200, 750)

        self.bin_path = None
        self.folder_path = None

        # Output folder relative to script
        self.png_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted_tims")
        os.makedirs(self.png_dir, exist_ok=True)

        self.build_ui()
        self.apply_style()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        bar = QHBoxLayout()
        self.btn_open_bin = QPushButton("📦 Open BIN")
        self.btn_extract = QPushButton("⬇ Extract")
        self.btn_rebuild = QPushButton("🔁 Rebuild BIN")
        self.btn_open_folder = QPushButton("📁 Open Image Folder")
        self.btn_open_explorer = QPushButton("📂 Open Folder in Explorer")

        self.btn_open_bin.clicked.connect(self.open_bin)
        self.btn_extract.clicked.connect(self.extract)
        self.btn_rebuild.clicked.connect(self.rebuild)
        self.btn_open_folder.clicked.connect(self.select_folder)
        self.btn_open_explorer.clicked.connect(self.open_folder_in_explorer)

        bar.addWidget(self.btn_open_bin)
        bar.addWidget(self.btn_extract)
        bar.addWidget(self.btn_rebuild)
        bar.addWidget(self.btn_open_folder)
        bar.addWidget(self.btn_open_explorer)
        bar.addStretch()
        layout.addLayout(bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self.preview)
        splitter.addWidget(self.tree)

        self.preview_label = QLabel("Select an image")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background:#111; border-radius:10px;")
        splitter.addWidget(self.preview_label)

        # Image details display
        self.image_info = QLabel("Image Details: Not selected")
        self.image_info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.image_info)

        splitter.setSizes([350, 850])
        layout.addWidget(splitter)

    def apply_style(self):
        # Get the absolute path of the current script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        qss_file_path = os.path.join(script_dir, STYLE)

        # Now open the file using the correct path
        try:
            with open(qss_file_path, "r") as f:
                self.setStyleSheet(f.read())  # Apply the stylesheet to the window
        except FileNotFoundError:
            print(f"Error: The file {qss_file_path} was not found.")

    # -----------------------------
    # BIN Extraction / Rebuild
    # -----------------------------
    def open_bin(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open BIN", "", "BIN files (*.bin)")
        if path:
            self.bin_path = path
            self.statusBar().showMessage(os.path.basename(path))

    def extract(self):
        if not self.bin_path:
            QMessageBox.warning(self, "Error", "Open a BIN first")
            return
        extract_bin(self.bin_path, self.png_dir)
        self.folder_path = self.png_dir
        self.load_images()

    def rebuild(self):
        if not self.bin_path:
            return
        out, _ = QFileDialog.getSaveFileName(self, "Save BIN", "CAR_MOD.BIN", "BIN files (*.bin)")
        if out:
            rebuild_bin(self.bin_path, self.png_dir, out)
            QMessageBox.information(self, "Done", "BIN rebuilt")

    # -----------------------------
    # Folder / Image Viewer
    # -----------------------------
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder", "")
        if folder:
            self.folder_path = folder
            self.load_images()

    def load_images(self):
        self.tree.clear()
        if not self.folder_path:
            return

        for f in sorted(os.listdir(self.folder_path)):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                item = QTreeWidgetItem([f])
                item.setData(0, Qt.ItemDataRole.UserRole, os.path.join(self.folder_path, f))
                self.tree.addTopLevelItem(item)

        self.preview_label.setText("Select an image")

    def preview(self, item, column=None):
        if not item:
            return
        path = item.data(0, Qt.ItemDataRole.UserRole)
        pix = QPixmap(path)
        self.preview_label.setPixmap(
            pix.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

        # Display image details
        self.display_image_info(path)

    def display_image_info(self, path):
        pixmap = QPixmap(path)
        width = pixmap.width()
        height = pixmap.height()
        file_size = os.path.getsize(path) // 1024  # in KB

        info_text = f"File: {os.path.basename(path)}\n"
        info_text += f"Dimensions: {width}x{height}\n"
        info_text += f"Size: {file_size} KB"

        self.image_info.setText(info_text)

    def open_folder_in_explorer(self):
        if self.folder_path and os.path.exists(self.folder_path):
            os.startfile(self.folder_path)
        else:
            QMessageBox.warning(self, "Error", "No folder selected or folder does not exist")

    def resizeEvent(self, e):
        self.preview(self.tree.currentItem())
        super().resizeEvent(e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TIMTool()
    win.show()
    sys.exit(app.exec())