import sys
import os
import time
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QTableView, QLabel, QVBoxLayout, 
    QWidget, QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QProgressBar,
    QPlainTextEdit, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QAbstractTableModel
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont


class ScanThread(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)

    def __init__(self, root_path):
        super().__init__()
        self.root_path = root_path

    def run(self):
        results = []
        total = 0
        for root, _, files in os.walk(self.root_path):
            for file in files:
                total += 1
                full_path = os.path.join(root, file)
                try:
                    stat = os.stat(full_path)
                    ext = Path(file).suffix.lower() or "(no extension)"

                    results.append({
                        'name': file,
                        'path': full_path,
                        'size': stat.st_size,
                        'size_str': self.format_size(stat.st_size),
                        'type': ext,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                        'modified_ts': stat.st_mtime
                    })
                except Exception:
                    continue

                if total % 100 == 0:
                    self.progress.emit(total, f"Scanned {total} files...")

        self.finished.emit(results)

    @staticmethod
    def format_size(size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


class FileTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.headers = ["Name", "Type", "Size", "Modified", "Path"]

    def rowCount(self, parent=None):
        return len(self.data)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            row = self.data[index.row()]
            col = index.column()
            if col == 0: return row['name']
            if col == 1: return row['type']
            if col == 2: return row['size_str']
            if col == 3: return row['modified']
            if col == 4: return row['path']
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None


class HexViewer(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        # Fixed font setup
        font = QFont("Courier New", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

    def show_hex(self, filepath, bytes_to_read=4096):
        try:
            with open(filepath, 'rb') as f:
                data = f.read(bytes_to_read)

            text = []
            for i in range(0, len(data), 16):
                chunk = data[i:i+16]
                hex_part = ' '.join(f'{b:02X}' for b in chunk)
                ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
                text.append(f"{i:08X}  {hex_part:<47}  {ascii_part}")
            
            if len(data) == bytes_to_read:
                text.append("\n... (truncated - first 4KB only)")

            self.setPlainText('\n'.join(text))
        except Exception as e:
            self.setPlainText(f"Error reading file:\n{str(e)}")


class FileScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Scanner & Hex Viewer")
        self.resize(1400, 900)

        self.files_data = []

        # Main layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # Left: Controls + Table
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        btn_layout = QHBoxLayout()
        self.btn_scan = QPushButton("📁 Choose Folder & Scan")
        self.btn_scan.clicked.connect(self.choose_and_scan)
        btn_layout.addWidget(self.btn_scan)
        left_layout.addLayout(btn_layout)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        left_layout.addWidget(self.progress)

        self.table = QTableView()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.clicked.connect(self.on_row_clicked)
        left_layout.addWidget(self.table)

        splitter.addWidget(left_panel)

        # Right: Info + Hex View
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.info_label = QLabel("Select a file to see details")
        self.info_label.setWordWrap(True)
        right_layout.addWidget(self.info_label)

        hex_label = QLabel("Hex Preview (first 4KB)")
        right_layout.addWidget(hex_label)

        self.hex_viewer = HexViewer()
        right_layout.addWidget(self.hex_viewer)

        splitter.addWidget(right_panel)
        splitter.setSizes([700, 700])

    def choose_and_scan(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Scan")
        if not folder:
            return

        self.btn_scan.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)

        self.scan_thread = ScanThread(folder)
        self.scan_thread.progress.connect(self.update_progress)
        self.scan_thread.finished.connect(self.scan_complete)
        self.scan_thread.start()

    def update_progress(self, count, message):
        self.progress.setFormat(f"{message} ({count} files)")

    def scan_complete(self, results):
        self.files_data = sorted(results, key=lambda x: x['modified_ts'], reverse=True)
        self.model = FileTableModel(self.files_data)
        self.table.setModel(self.model)

        self.progress.setVisible(False)
        self.btn_scan.setEnabled(True)

        QMessageBox.information(self, "Scan Complete", 
                              f"Found {len(self.files_data)} files.")

    def on_row_clicked(self, index):
        row = index.row()
        file_info = self.files_data[row]

        # Info panel
        info_text = f"""
        <b>File:</b> {file_info['name']}
        <br><b>Full Path:</b> {file_info['path']}
        <br><b>Type:</b> {file_info['type']}
        <br><b>Size:</b> {file_info['size_str']} ({file_info['size']:,} bytes)
        <br><b>Modified:</b> {file_info['modified']}
        """
        self.info_label.setText(info_text)

        # Hex view
        self.hex_viewer.show_hex(file_info['path'])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileScannerApp()
    window.show()
    sys.exit(app.exec())