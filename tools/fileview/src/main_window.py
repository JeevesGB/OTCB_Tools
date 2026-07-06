import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QTableView, QTreeView, QLabel, QVBoxLayout, QWidget,
    QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QProgressBar,
    QHeaderView
)
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QFont, QFileSystemModel

from file_model import FileTableModel
from scan_thread import ScanThread
from hex_viewer import HexViewer
from hex_editor import HexEditor   # ← New import


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Scanner & Hex Viewer")
        self.resize(1600, 900)

        self.current_root = None
        self.files_data = []
        self.current_model = None

        self._setup_ui()
        self._load_styles()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_select_root = QPushButton("📁 Select Root Folder")
        self.btn_select_root.clicked.connect(self.select_root_folder)
        self.btn_full_scan = QPushButton("🔍 Full Recursive Scan")
        self.btn_full_scan.clicked.connect(self.start_full_scan)

        toolbar.addWidget(self.btn_select_root)
        toolbar.addWidget(self.btn_full_scan)
        toolbar.addStretch()
        main_layout.addLayout(toolbar)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        main_layout.addWidget(self.progress)

        # Main Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Tree
        self.tree_model = QFileSystemModel()
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.tree_model)
        self.tree_view.clicked.connect(self.on_tree_clicked)
        splitter.addWidget(self.tree_view)

        # Center: Table
        self.table = QTableView()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.clicked.connect(self.on_file_selected)
        splitter.addWidget(self.table)

        # Right: Info + Hex + Editor
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.info_label = QLabel("Select a root folder to begin")
        self.info_label.setWordWrap(True)
        self.info_label.setMinimumHeight(140)
        right_layout.addWidget(self.info_label)

        hex_title = QLabel("Hex Preview")
        hex_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_layout.addWidget(hex_title)

        self.hex_viewer = HexViewer()
        right_layout.addWidget(self.hex_viewer)

        # Hex Editor Button
        editor_btn = QPushButton("✏️ Open in Hex Editor")
        editor_btn.clicked.connect(self.open_in_hex_editor)
        right_layout.addWidget(editor_btn)

        splitter.addWidget(right_panel)
        splitter.setSizes([380, 650, 570])
        main_layout.addWidget(splitter)

    def _load_styles(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            qss_path = os.path.join(base_dir, "styles.qss")
            if os.path.exists(qss_path):
                with open(qss_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Stylesheet error: {e}")

    def select_root_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Root Folder")
        if folder:
            self.current_root = folder
            self.tree_model.setRootPath(folder)
            root_index = self.tree_model.index(folder)
            self.tree_view.setRootIndex(root_index)
            self.tree_view.expand(root_index)
            self.show_files_in_folder(folder)

    def on_tree_clicked(self, index):
        path = self.tree_model.filePath(index)
        self.show_files_in_folder(path)

    def show_files_in_folder(self, folder_path: str):
        if not os.path.isdir(folder_path):
            return
        results = []
        try:
            for item in os.listdir(folder_path):
                full_path = os.path.join(folder_path, item)
                if os.path.isfile(full_path):
                    try:
                        stat = os.stat(full_path)
                        ext = os.path.splitext(item)[1].lower() or "(none)"
                        results.append({
                            'name': item,
                            'path': full_path,
                            'size': stat.st_size,
                            'size_str': ScanThread._format_size(stat.st_size),
                            'type': ext,
                            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                            'modified_ts': stat.st_mtime
                        })
                    except:
                        continue
            results.sort(key=lambda x: x['modified_ts'], reverse=True)
        except Exception as e:
            print(f"Error reading folder: {e}")

        self.files_data = results
        self.current_model = FileTableModel(results)
        self.table.setModel(self.current_model)

    def on_file_selected(self, index):
        row = index.row()
        if row >= len(self.files_data):
            return
        file_info = self.files_data[row]

        info = f"""
        <b>Name:</b> {file_info['name']}<br>
        <b>Type:</b> {file_info['type']}<br>
        <b>Size:</b> {file_info['size_str']}<br>
        <b>Modified:</b> {file_info['modified']}<br>
        <b>Path:</b> {file_info['path']}
        """
        self.info_label.setText(info)
        self.hex_viewer.show_hex(file_info['path'])

    def open_in_hex_editor(self):
        """Open currently selected file in Hex Editor"""
        if self.current_model is None or len(self.files_data) == 0:
            QMessageBox.warning(self, "No Data", "Please load a folder first.")
            return

        # Get selected row
        selection_model = self.table.selectionModel()
        if not selection_model:
            QMessageBox.warning(self, "No Selection", "Please select a file in the table first.")
            return

        selected = selection_model.selectedRows()
        if not selected:
            # Fallback: use current index
            current = self.table.currentIndex()
            if current.isValid():
                row = current.row()
            else:
                QMessageBox.warning(self, "No Selection", "Please select a file in the table first.")
                return
        else:
            row = selected[0].row()

        if row >= len(self.files_data):
            QMessageBox.warning(self, "No Selection", "Please select a file in the table first.")
            return

        file_info = self.files_data[row]
        self.hex_editor = HexEditor()
        self.hex_editor.load_file(file_info['path'])

    def start_full_scan(self):
        if not self.current_root:
            QMessageBox.warning(self, "No Root", "Please select a root folder first.")
            return
        self.btn_full_scan.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)

        self.scan_thread = ScanThread(self.current_root)
        self.scan_thread.progress.connect(self.update_progress)
        self.scan_thread.finished.connect(self.full_scan_finished)
        self.scan_thread.start()

    def update_progress(self, count: int, message: str):
        self.progress.setFormat(f"{message} ({count:,})")

    def full_scan_finished(self, results: list):
        self.files_data = results
        self.current_model = FileTableModel(results)
        self.table.setModel(self.current_model)

        self.progress.setVisible(False)
        self.btn_full_scan.setEnabled(True)

        QMessageBox.information(self, "Full Scan Complete", 
                              f"Found {len(results):,} files recursively in:\n{self.current_root}")