import os
import struct
import sys
from typing import List, Tuple, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QLabel, QListView,
    QAbstractItemView, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt6.QtGui import QPixmap, QImage, QStandardItemModel, QStandardItem, QColor
from PyQt6.QtCore import Qt

TIM_MAGIC = b"\x10\x00\x00\x00"
FLAG_CLUT = 0x08  # bit 3
# bpp_code: 0=4bpp, 1=8bpp, 2=16bpp, 3=24bpp


# ------------------------------- Utilities -------------------------------- #

def _bgr555_to_rgb(v: int) -> Tuple[int, int, int]:
    r = (v & 0x1F) << 3
    g = ((v >> 5) & 0x1F) << 3
    b = ((v >> 10) & 0x1F) << 3
    return r, g, b


# ------------------------------- Parsers ----------------------------------- #

def parse_tix(file_path: str) -> List[Tuple[str, bytes]]:
    with open(file_path, "rb") as f:
        data = f.read()

    tims: List[Tuple[str, bytes]] = []
    i = 0
    n = len(data)
    idx = 0

    while i + 8 <= n:
        if data[i:i + 4] != TIM_MAGIC:
            i += 1
            continue

        try:
            flags = struct.unpack_from("<I", data, i + 4)[0]
            pos = i + 8

            if (flags & FLAG_CLUT) != 0:
                if pos + 4 > n:
                    raise ValueError("CLUT length field out of range")
                clut_len = struct.unpack_from("<I", data, pos)[0]
                if clut_len < 12:
                    raise ValueError("CLUT length too small")
                if pos + clut_len > n:
                    raise ValueError("CLUT block exceeds file")
                pos += clut_len

            # Image block
            if pos + 4 > n:
                raise ValueError("Image length field out of range")

            img_len = struct.unpack_from("<I", data, pos)[0]
            if img_len < 12:
                raise ValueError("Image length too small")
            total_len = (pos - i) + img_len
            if i + total_len > n:
                raise ValueError("TIM total length exceeds file")

            raw_tim = data[i:i + total_len]
            tims.append((f"tex_{idx:04d}.tim", raw_tim))
            idx += 1
            i += total_len
            continue

        except Exception as e:
            i += 1
            continue

    return tims


def tim_to_qimage(tim_data: bytes) -> Optional[QImage]:
    try:
        if len(tim_data) < 8 or tim_data[:4] != TIM_MAGIC:
            return None

        flags = struct.unpack_from("<I", tim_data, 4)[0]
        bpp_code = flags & 0x07
        pos = 8
        n = len(tim_data)

        palette = []
        if (flags & FLAG_CLUT) != 0:
            if pos + 4 > n:
                return None
            clut_len = struct.unpack_from("<I", tim_data, pos)[0]
            if clut_len < 12 or pos + clut_len > n:
                return None
            # CLUT header
            clut_x, clut_y, clut_w, clut_h = struct.unpack_from("<4H", tim_data, pos + 4)
            pal_entries = clut_w * clut_h
            pal_data_start = pos + 12
            pal_data_end = pal_data_start + pal_entries * 2
            if pal_data_end > n:
                return None
            for off in range(pal_data_start, pal_data_end, 2):
                v = struct.unpack_from("<H", tim_data, off)[0]
                palette.append(_bgr555_to_rgb(v))
            pos += clut_len

        if pos + 12 > n:
            return None
        img_len = struct.unpack_from("<I", tim_data, pos)[0]
        if img_len < 12 or pos + img_len > n:
            return None

        img_x, img_y, img_w_words, img_h = struct.unpack_from("<4H", tim_data, pos + 4)
        pixel_data = tim_data[pos + 12: pos + img_len]

        if bpp_code == 0:
            width = img_w_words * 4
            bytes_per_row = img_w_words * 2
        elif bpp_code == 1:
            width = img_w_words * 2
            bytes_per_row = img_w_words * 2
        elif bpp_code == 2:
            width = img_w_words
            bytes_per_row = img_w_words * 2
        elif bpp_code == 3:
            bytes_per_row = img_w_words * 2
            if bytes_per_row == 0:
                return None
            width = bytes_per_row // 3
        else:
            return None

        height = img_h
        if width <= 0 or height <= 0 or width > 4096 or height > 4096:
            return None

        expected_min = bytes_per_row * height
        if len(pixel_data) < expected_min:
            return None

        # Decode
        img = QImage(width, height, QImage.Format.Format_ARGB32)
        transparent_rgb = QColor(0, 0, 0).rgba()

        if bpp_code in (0, 1):
            if not palette:
                return None
            pal_len = len(palette)

            if bpp_code == 0:
                for y in range(height):
                    row = pixel_data[y * bytes_per_row:(y + 1) * bytes_per_row]
                    x = 0
                    for byte in row:
                        i0 = byte & 0x0F
                        i1 = (byte >> 4) & 0x0F
                        if x < width:
                            r, g, b = palette[i0 % pal_len]
                            img.setPixel(x, y, QColor(r, g, b).rgba())
                        x += 1
                        if x < width:
                            r, g, b = palette[i1 % pal_len]
                            img.setPixel(x, y, QColor(r, g, b).rgba())
                        x += 1

            else:
                for y in range(height):
                    row = pixel_data[y * bytes_per_row:(y + 1) * bytes_per_row]
                    for x in range(min(width, len(row))):
                        idx = row[x]
                        r, g, b = palette[idx % pal_len]
                        img.setPixel(x, y, QColor(r, g, b).rgba())

        elif bpp_code == 2:
            for y in range(height):
                row = pixel_data[y * bytes_per_row:(y + 1) * bytes_per_row]
                # Safety if row shorter:
                if len(row) < width * 2:
                    return None
                off = 0
                for x in range(width):
                    v = struct.unpack_from("<H", row, off)[0]
                    off += 2
                    r, g, b = _bgr555_to_rgb(v)
                    # Optional: treat 0 as transparent
                    if (v & 0x7FFF) == 0:
                        img.setPixel(x, y, transparent_rgb)
                    else:
                        img.setPixel(x, y, QColor(r, g, b).rgba())

        elif bpp_code == 3:
            for y in range(height):
                row = pixel_data[y * bytes_per_row:(y + 1) * bytes_per_row]
                off = 0
                x = 0
                while off + 2 < len(row) and x < width:
                    r = row[off]
                    g = row[off + 1]
                    b = row[off + 2]
                    off += 3
                    img.setPixel(x, y, QColor(r, g, b).rgba())
                    x += 1
        else:
            return None

        return img

    except Exception:
        return None


def save_tix(file_path: str, tims: List[Tuple[str, bytes]]) -> None:
    with open(file_path, "wb") as f:
        for _, tim_data in tims:
            f.write(tim_data)


# ------------------------------- GUI -------------------------------------- #

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TIX2TIM")
        self.resize(1000, 850)

        self.tims: List[Tuple[str, bytes]] = []

        # Widgets
        self.list_view = QListView()
        self.list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.model = QStandardItemModel()
        self.list_view.setModel(self.model)
        # Connect after model is set (avoids NoneType selectionModel)
        self.list_view.selectionModel().selectionChanged.connect(self.on_selection_changed)

        self.preview_label = QLabel("Preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(256, 256)
        self.preview_label.setStyleSheet("QLabel { background: #222; color: #ddd; border: 1px solid #444; }")

        open_button = QPushButton("Open .TIX")
        open_button.clicked.connect(self.open_tix)

        extract_button = QPushButton("Extract TIMs")
        extract_button.clicked.connect(self.extract_tims)

        repack_button = QPushButton("Repack .TIX")
        repack_button.clicked.connect(self.repack_tix)

        # Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(open_button)
        button_layout.addWidget(extract_button)
        button_layout.addWidget(repack_button)

        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.list_view)
        layout.addWidget(self.preview_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_tix(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open .TIX File", "", "TIX Files (*.TIX *.tix)")
        if not file_path:
            return

        tims = parse_tix(file_path)
        if not tims:
            QMessageBox.warning(self, "No TIMs", "No TIM images were found in this file.")
            return

        self.tims = tims
        self.model.clear()
        for name, blob in self.tims:
            qimg = tim_to_qimage(blob)
            item = QStandardItem(f"{name} {'(ok)' if qimg is not None else '(bad)'}")
            self.model.appendRow(item)

        for row, (_, blob) in enumerate(self.tims):
            if tim_to_qimage(blob) is not None:
                self.list_view.setCurrentIndex(self.model.index(row, 0))
                self.on_selection_changed(self.list_view.selectionModel().selection(), None)
                break

    def extract_tims(self):
        if not self.tims:
            QMessageBox.warning(self, "No Data", "No TIMs loaded.")
            return
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not folder:
            return
        count = 0
        for name, data in self.tims:
            out_path = os.path.join(folder, name)
            with open(out_path, "wb") as f:
                f.write(data)
            count += 1
        QMessageBox.information(self, "Done", f"Extracted {count} TIM(s).")

    def repack_tix(self):
        if not self.tims:
            QMessageBox.warning(self, "No Data", "No TIMs loaded.")
            return

        QMessageBox.information(self, "Repack",
                                "Choose an optional folder of replacement .TIM files.\n"
                                "Files should be named exactly like the entries (e.g., tex_0000.tim).")
        repl_dir = QFileDialog.getExistingDirectory(self, "Replacement TIMs (optional)")
        file_path, _ = QFileDialog.getSaveFileName(self, "Save .TIX File", "", "TIX Files (*.TIX *.tix)")
        if not file_path:
            return

        out_list: List[Tuple[str, bytes]] = []
        for name, data in self.tims:
            repl_path = os.path.join(repl_dir, name) if repl_dir else None
            if repl_path and os.path.isfile(repl_path):
                with open(repl_path, "rb") as f:
                    new_blob = f.read()
                # sanity: must start with TIM magic
                if new_blob[:4] == TIM_MAGIC:
                    out_list.append((name, new_blob))
                else:
                    QMessageBox.warning(self, "Warning", f"{name} is not a TIM; keeping original.")
                    out_list.append((name, data))
            else:
                out_list.append((name, data))

        save_tix(file_path, out_list)
        QMessageBox.information(self, "Done", f"TIX repacked:\n{file_path}")

    def on_selection_changed(self, selected, _):
        if not selected or not selected.indexes():
            return
        row = selected.indexes()[0].row()
        if row < 0 or row >= len(self.tims):
            return

        name, data = self.tims[row]
        qimg = tim_to_qimage(data)
        if qimg is None:
            self.preview_label.setText("Cannot decode this TIM")
            self.preview_label.setPixmap(QPixmap())
            return

        pm = QPixmap.fromImage(qimg)
        self.preview_label.setPixmap(pm.scaled(self.preview_label.size() * 0.98,
                                               Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        idxs = self.list_view.selectedIndexes()
        if idxs:
            row = idxs[0].row()
            if 0 <= row < len(self.tims):
                name, data = self.tims[row]
                qimg = tim_to_qimage(data)
                if qimg:
                    pm = QPixmap.fromImage(qimg)
                    self.preview_label.setPixmap(pm.scaled(self.preview_label.size() * 0.98,
                                                           Qt.AspectRatioMode.KeepAspectRatio,
                                                           Qt.TransformationMode.SmoothTransformation))


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
