import os
from PyQt6.QtWidgets import (
    QPlainTextEdit, QListWidget, QTabWidget, QWidget,
    QVBoxLayout, QListWidgetItem, QPushButton, QTextEdit, QLabel
)
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from hex_utils import build_hex_lines, extract_strings


class HexLoadThread(QThread):
    """
    Reads the file and builds the hex dump + extracted strings off the GUI
    thread. Without this, show_hex() used to read up to 100MB and run two
    regex passes directly inside the button-click handler, which visibly
    froze the UI on large files.
    """
    finished = pyqtSignal(str, list, int, bool)  # hex_text, strings, file_size, truncated
    error = pyqtSignal(str)

    def __init__(self, filepath: str, max_bytes: int):
        super().__init__()
        self.filepath = filepath
        self.max_bytes = max_bytes

    def run(self):
        try:
            file_size = os.path.getsize(self.filepath)
            with open(self.filepath, 'rb') as f:
                data = f.read(self.max_bytes)

            truncated = file_size > self.max_bytes

            lines = build_hex_lines(data)
            if truncated:
                lines.append(f"\n... TRUNCATED: First {self.max_bytes:,} bytes of {file_size:,} bytes total")
            else:
                lines.append(f"\n[End of file - {file_size:,} bytes]")

            strings = extract_strings(data)
            self.finished.emit('\n'.join(lines), strings, file_size, truncated)
        except Exception as e:
            self.error.emit(str(e))


class HexViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.current_filepath = None
        self.current_extra_selections = []
        self.load_thread = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Hex View
        self.hex_text = QPlainTextEdit()
        self.hex_text.setReadOnly(True)
        self.hex_text.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        font = QFont("Courier New", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.hex_text.setFont(font)
        self.tabs.addTab(self.hex_text, "Hex View")

        # Strings Tab
        strings_panel = QWidget()
        strings_layout = QVBoxLayout(strings_panel)

        self.strings_list = QListWidget()
        self.strings_list.itemClicked.connect(self.highlight_string)
        strings_layout.addWidget(self.strings_list)

        clear_btn = QPushButton("Clear Highlight")
        clear_btn.clicked.connect(self.clear_highlight)
        strings_layout.addWidget(clear_btn)

        self.tabs.addTab(strings_panel, "Extracted Strings")

    def show_hex(self, filepath: str, max_bytes: int = 104_857_600):  # 100 MB default
        self.current_filepath = filepath
        self.strings_list.clear()
        self.clear_highlight()
        self.hex_text.setPlainText("Loading...")
        self.status_label.setText(f"Loading {os.path.basename(filepath)}...")

        # If a previous load is still running, disconnect its signals so
        # its result is ignored - starting a second QThread on the same
        # object before the first finishes would be unsafe otherwise.
        if self.load_thread is not None and self.load_thread.isRunning():
            try:
                self.load_thread.finished.disconnect()
                self.load_thread.error.disconnect()
            except TypeError:
                pass

        self.load_thread = HexLoadThread(filepath, max_bytes)
        self.load_thread.finished.connect(self._on_load_finished)
        self.load_thread.error.connect(self._on_load_error)
        self.load_thread.start()

    def _on_load_finished(self, hex_text: str, strings: list, file_size: int, truncated: bool):
        self.hex_text.setPlainText(hex_text)
        for kind, offset, s in strings:
            self.strings_list.addItem(f"{kind:<6} {offset:08X}  |  {s}")

        note = " (truncated to first 100MB)" if truncated else ""
        self.status_label.setText(f"{os.path.basename(self.current_filepath)} - {file_size:,} bytes{note}")

    def _on_load_error(self, message: str):
        self.hex_text.setPlainText(f"Error reading file:\n{message}")
        self.status_label.setText("")

    def highlight_string(self, item: QListWidgetItem):
        self.clear_highlight()
        try:
            offset_hex = item.text().split()[1]
            content = self.hex_text.toPlainText()
            pos = content.find(offset_hex)

            if pos != -1:
                cursor = self.hex_text.textCursor()
                cursor.setPosition(pos)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)

                fmt = QTextCharFormat()
                fmt.setBackground(QColor("#ffd700"))   # Gold
                fmt.setForeground(QColor("#000000"))

                extra = QTextEdit.ExtraSelection()
                extra.cursor = cursor
                extra.format = fmt
                self.current_extra_selections = [extra]

                self.hex_text.setExtraSelections(self.current_extra_selections)
                self.hex_text.ensureCursorVisible()

            self.tabs.setCurrentIndex(0)
        except Exception as e:
            print("Highlight error:", e)

    def clear_highlight(self):
        self.current_extra_selections = []
        self.hex_text.setExtraSelections([])
