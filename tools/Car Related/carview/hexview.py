# hexview.py
from PyQt6.QtWidgets import QPlainTextEdit

class HexView(QPlainTextEdit):
    def load(self, data: bytes):
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hexs = " ".join(f"{b:02X}" for b in chunk)
            lines.append(f"{i:06X}: {hexs}")
        self.setPlainText("\n".join(lines))
        self.setReadOnly(True)