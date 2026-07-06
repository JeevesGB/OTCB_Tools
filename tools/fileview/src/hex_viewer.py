import os
import re
from PyQt6.QtWidgets import (
    QPlainTextEdit, QListWidget, QTabWidget, QWidget, 
    QVBoxLayout, QListWidgetItem, QPushButton, QTextEdit
)
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
from PyQt6.QtCore import Qt


class HexViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.current_filepath = None
        self.current_extra_selections = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

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

        try:
            file_size = os.path.getsize(filepath)
            
            if file_size > max_bytes:
                print(f"Note: File is {file_size/1024/1024:.1f} MB. Showing first 100MB.")

            read_limit = max_bytes
            with open(filepath, 'rb') as f:
                data = f.read(read_limit)

            self._build_hex_view(data, file_size)
            self._extract_strings(data)

        except Exception as e:
            self.hex_text.setPlainText(f"Error reading file:\n{str(e)}")

    def _build_hex_view(self, data: bytes, file_size: int):
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_part = ' '.join(f'{b:02X}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            lines.append(f"{i:08X}  {hex_part:<47}  {ascii_part}")

        if len(data) < file_size:
            lines.append(f"\n... TRUNCATED: First 100MB of {file_size:,} bytes total")
        else:
            lines.append(f"\n[End of file - {file_size:,} bytes]")

        self.hex_text.setPlainText('\n'.join(lines))

    def _extract_strings(self, data: bytes):
        seen = set()
        # ASCII
        for match in re.finditer(b'[ -~]{4,}', data):
            offset = match.start()
            s = match.group().decode('ascii', errors='replace').strip()
            if len(s) >= 4 and s not in seen:
                seen.add(s)
                self.strings_list.addItem(f"ASCII  {offset:08X}  |  {s}")

        # UTF-16LE
        for match in re.finditer(b'(?:[\x20-\x7E]\x00){4,}', data):
            offset = match.start()
            try:
                s = match.group().decode('utf-16le', errors='replace').strip()
                if len(s) >= 4 and s not in seen:
                    seen.add(s)
                    self.strings_list.addItem(f"UTF-16 {offset:08X}  |  {s}")
            except:
                continue

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