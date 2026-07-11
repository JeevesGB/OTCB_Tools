import os
import shutil
from PyQt6.QtWidgets import (
    QMainWindow, QPlainTextEdit, QVBoxLayout, QWidget,
    QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QLabel
)
from PyQt6.QtGui import QFont

from hex_utils import build_hex_lines, parse_hex_lines

# Above this size we refuse to load into the editor - editing multi-GB
# files as one giant in-memory bytearray + QPlainTextEdit buffer isn't
# something this tool is built for. The read-only Hex Viewer already
# handles large files safely (it truncates); this editor is meant for
# small/medium files you actually intend to modify.
MAX_EDIT_BYTES = 20 * 1024 * 1024  # 20 MB


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
            size = os.path.getsize(filepath)
            if size > MAX_EDIT_BYTES:
                QMessageBox.warning(
                    self, "File Too Large",
                    f"This file is {size / (1024 * 1024):.1f} MB.\n\n"
                    f"The Hex Editor only supports files up to "
                    f"{MAX_EDIT_BYTES / (1024 * 1024):.0f} MB, since edits are "
                    f"held in memory and rewritten in full on save.\n\n"
                    f"Use the read-only Hex Viewer to inspect larger files."
                )
                return

            with open(filepath, 'rb') as f:
                self.original_data = f.read()

            self.current_file = filepath
            self.status.setText(f"Loaded: {os.path.basename(filepath)} ({len(self.original_data):,} bytes)")
            self._display_hex()
            self.show()
            self.raise_()
            self.activateWindow()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load:\n{str(e)}")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if file_path:
            self.load_file(file_path)

    def _display_hex(self):
        lines = build_hex_lines(self.original_data)
        self.hex_edit.setPlainText('\n'.join(lines))

    def save_file(self):
        if not self.current_file or self.original_data is None:
            QMessageBox.warning(self, "No File", "No file is currently loaded.")
            return

        new_data = parse_hex_lines(self.hex_edit.toPlainText())

        if new_data == self.original_data:
            QMessageBox.information(self, "No Changes", "Nothing to save - the file is unchanged.")
            return

        size_note = ""
        if len(new_data) != len(self.original_data):
            size_note = (
                f"\n\nNote: size changed from {len(self.original_data):,} "
                f"to {len(new_data):,} bytes."
            )

        reply = QMessageBox.question(
            self, "Confirm Save",
            f"Write {len(new_data):,} bytes back to:\n{self.current_file}\n\n"
            f"A backup of the original will be saved as '{os.path.basename(self.current_file)}.bak' "
            f"in the same folder.{size_note}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            backup_path = self.current_file + ".bak"
            shutil.copy2(self.current_file, backup_path)

            with open(self.current_file, 'wb') as f:
                f.write(new_data)

            self.original_data = new_data
            self.status.setText(
                f"Saved: {os.path.basename(self.current_file)} ({len(new_data):,} bytes) "
                f"- backup at {os.path.basename(backup_path)}"
            )
            QMessageBox.information(self, "Saved", "Changes written successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save:\n{str(e)}")
