import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog,
    QLabel, QPushButton, QListWidget, QListWidgetItem,
    QVBoxLayout, QHBoxLayout, QMessageBox, QSplitter
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from tim_core import extract_bin, rebuild_bin

class TIMTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OTCB TIM Tool")
        self.resize(1200, 750)

        self.bin_path = None
        self.png_dir = "extracted_tim"

        self.build_ui()
        self.apply_style()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        bar = QHBoxLayout()
        self.btn_open = QPushButton("📦 Open BIN")
        self.btn_extract = QPushButton("⬇ Extract")
        self.btn_rebuild = QPushButton("🔁 Rebuild BIN")

        self.btn_open.clicked.connect(self.open_bin)
        self.btn_extract.clicked.connect(self.extract)
        self.btn_rebuild.clicked.connect(self.rebuild)

        bar.addWidget(self.btn_open)
        bar.addWidget(self.btn_extract)
        bar.addWidget(self.btn_rebuild)
        bar.addStretch()
        layout.addLayout(bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.list = QListWidget()
        self.list.currentItemChanged.connect(self.preview)
        splitter.addWidget(self.list)

        self.preview_label = QLabel("Select a texture")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background:#111; border-radius:10px;")
        splitter.addWidget(self.preview_label)

        splitter.setSizes([350, 850])
        layout.addWidget(splitter)

    def apply_style(self):
        self.setStyleSheet("""
        QWidget {
            background: #1e1e1e;
            color: white;
            font-family: Segoe UI;
            font-size: 11pt;
        }
        QPushButton {
            background: #2d2d2d;
            border-radius: 8px;
            padding: 8px 16px;
        }
        QPushButton:hover { background: #3a3a3a; }
        QPushButton:pressed { background: #0078d4; }
        QListWidget {
            background: #252526;
            border-radius: 8px;
        }
        """)

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
        self.load_pngs()

    def rebuild(self):
        if not self.bin_path:
            return

        out, _ = QFileDialog.getSaveFileName(self, "Save BIN", "CAR_MOD.BIN", "BIN files (*.bin)")
        if out:
            rebuild_bin(self.bin_path, self.png_dir, out)
            QMessageBox.information(self, "Done", "BIN rebuilt")

    def load_pngs(self):
        self.list.clear()
        if not os.path.isdir(self.png_dir):
            return

        for f in sorted(os.listdir(self.png_dir)):
            if f.endswith(".png"):
                item = QListWidgetItem(f)
                item.setData(Qt.ItemDataRole.UserRole, os.path.join(self.png_dir, f))
                self.list.addItem(item)

    def preview(self, item):
        if not item:
            return
        pix = QPixmap(item.data(Qt.ItemDataRole.UserRole))
        self.preview_label.setPixmap(
            pix.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def resizeEvent(self, e):
        self.preview(self.list.currentItem())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TIMTool()
    win.show()
    sys.exit(app.exec())