import os
import struct
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit, QMessageBox
)


class TimExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TIM Extractor")
        self.resize(500, 400)

        layout = QVBoxLayout()

        self.load_btn = QPushButton("Open .BIN File")
        self.load_btn.clicked.connect(self.load_bin)

        self.status_label = QLabel("No file loaded.")
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        layout.addWidget(self.load_btn)
        layout.addWidget(self.status_label)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def load_bin(self):
        bin_path, _ = QFileDialog.getOpenFileName(
            self, "Select BIN File", "", "BIN Files (*.BIN);;All Files (*)"
        )
        if not bin_path:
            return

        self.status_label.setText(f"Loaded: {os.path.basename(bin_path)}")
        self.extract_tims(bin_path)

    def extract_tims(self, bin_path):
        with open(bin_path, "rb") as f:
            data = f.read()

        magic = b"\x10\x00\x00\x00"  # TIM magic bytes
        pos = 0
        count = 0

        output_dir = os.path.join(os.path.dirname(bin_path), "TIMS")
        os.makedirs(output_dir, exist_ok=True)

        while True:
            idx = data.find(magic, pos)
            if idx == -1:
                break

            if idx + 8 > len(data):
                break

            # Read TIM length (from header: after magic, 4 bytes size)
            try:
                tim_size = struct.unpack_from("<I", data, idx + 4)[0]
            except struct.error:
                break

            if tim_size <= 0 or tim_size > len(data) - idx:
                pos = idx + 4
                continue

            tim_data = data[idx:idx + tim_size]
            out_file = os.path.join(output_dir, f"image_{count:03}.tim")

            with open(out_file, "wb") as out:
                out.write(tim_data)

            self.log_output.append(f"Extracted: {out_file}")
            count += 1
            pos = idx + tim_size

        QMessageBox.information(self, "Done", f"Extracted {count} TIM files to {output_dir}")


if __name__ == "__main__":
    app = QApplication([])
    window = TimExtractor()
    window.show()
    app.exec()
