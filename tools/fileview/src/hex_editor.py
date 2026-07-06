import os
from PyQt6.QtWidgets import (
    QMainWindow, QPlainTextEdit, QVBoxLayout, QWidget,
    QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QLabel
)
from PyQt6.QtGui import QFont


class HexEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hex Editor - OTCB Tools")
        self.resize(1300, 750)
        self.current_file = None
        self.original_data = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Toolbar
        toolbar = QHBoxLayout()
        open_btn = QPushButton("Open File")
        open_btn.clicked.connect(self.open_file)
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_file)
        toolbar.addWidget(open_btn)
        toolbar.addWidget(save_btn)
        toolbar.addStretch()
        self.status = QLabel("No file loaded")
        toolbar.addWidget(self.status)
        layout.addLayout(toolbar)

        # Hex Area
        self.hex_edit = QPlainTextEdit()
        self.hex_edit.setFont(QFont("Courier New", 10))
        self.hex_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.hex_edit)

    def load_file(self, filepath: str):
        """Called from main app"""
        try:
            with open(filepath, 'rb') as f:
                self.original_data = f.read()

            self.current_file = filepath
            self.status.setText(f"Loaded: {os.path.basename(filepath)} ({len(self.original_data):,} bytes)")
            self._display_hex()
            self.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load:\n{str(e)}")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if file_path:
            self.load_file(file_path)

    def _display_hex(self):
        lines = []
        for i in range(0, len(self.original_data), 16):
            chunk = self.original_data[i:i+16]
            hex_line = ' '.join(f'{b:02X}' for b in chunk)
            ascii_line = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            lines.append(f"{i:08X}  {hex_line:<47}  {ascii_line}")
        self.hex_edit.setPlainText('\n'.join(lines))

    def save_file(self):
        QMessageBox.information(self, "Save", 
                              "Full hex editing & saving is not implemented yet.\n\nThis is viewer mode for now.")