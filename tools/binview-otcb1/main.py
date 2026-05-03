#!/usr/bin/env python3
"""
OTCB1 Viewer — Option Tuning Car Battle 1 Demo asset viewer
Supports: BIN files (TIM image containers), raw TIM images, MAINMENU strings

Requirements: PyQt6, Pillow
    pip install PyQt6 pillow
"""

import sys
import os
import struct
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QLabel, QScrollArea,
    QStatusBar, QFileDialog, QMenuBar, QMenu, QToolBar, QFrame,
    QSizePolicy, QSlider, QSpinBox, QGroupBox, QGridLayout,
    QTextEdit, QPushButton, QProgressBar, QTabWidget, QMessageBox,
    QAbstractItemView, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import (
    Qt, QSize, QThread, pyqtSignal, QTimer, QRect, QPoint
)
from PyQt6.QtGui import (
    QPixmap, QImage, QColor, QPalette, QFont, QFontDatabase,
    QAction, QIcon, QPainter, QPen, QBrush, QKeySequence,
    QDragEnterEvent, QDropEvent
)

from PIL import Image
import io


# ─────────────────────────────────────────────
#  PSX FORMAT PARSERS
# ─────────────────────────────────────────────

class TIMImage:
    """Parsed PSX TIM image."""

    BPP_NAMES = {0: '4bpp', 1: '8bpp', 2: '16bpp', 3: '24bpp'}

    def __init__(self):
        self.bpp = 0
        self.has_clut = False
        self.clut_x = self.clut_y = 0
        self.clut_w = self.clut_h = 0
        self.clut_data = b''
        self.img_x = self.img_y = 0
        self.img_w = self.img_h = 0
        self.img_data = b''
        self.pil_image = None
        self.offset = 0
        self.raw_size = 0

    @classmethod
    def from_data(cls, data, offset=0):
        pos = offset
        if pos + 8 > len(data):
            return None
        magic = struct.unpack_from('<I', data, pos)[0]
        if magic != 0x10:
            return None

        tim = cls()
        tim.offset = offset
        flags = struct.unpack_from('<I', data, pos + 4)[0]
        tim.bpp = flags & 0x07
        tim.has_clut = bool(flags & 0x08)
        pos += 8

        if tim.has_clut:
            if pos + 12 > len(data):
                return None
            clut_size = struct.unpack_from('<I', data, pos)[0]
            tim.clut_x, tim.clut_y = struct.unpack_from('<HH', data, pos + 4)
            tim.clut_w, tim.clut_h = struct.unpack_from('<HH', data, pos + 8)
            tim.clut_data = data[pos + 12: pos + clut_size]
            pos += clut_size

        if pos + 12 > len(data):
            return None
        img_size = struct.unpack_from('<I', data, pos)[0]
        tim.img_x, tim.img_y = struct.unpack_from('<HH', data, pos + 4)
        tim.img_w, tim.img_h = struct.unpack_from('<HH', data, pos + 8)
        tim.img_data = data[pos + 12: pos + img_size]
        tim.raw_size = (pos + img_size) - offset

        tim.pil_image = tim._decode()
        return tim

    def _decode(self):
        try:
            if self.bpp == 1:  # 8bpp
                px_w = self.img_w * 2
                px_h = self.img_h
                palette = self._build_palette(256)
                if len(self.img_data) < px_w * px_h:
                    return None
                img = Image.frombytes('P', (px_w, px_h), self.img_data[:px_w * px_h])
                img.putpalette(palette)
                return img.convert('RGBA')

            elif self.bpp == 0:  # 4bpp
                px_w = self.img_w * 4
                px_h = self.img_h
                palette = self._build_palette(16)
                pixels = []
                for byte in self.img_data:
                    pixels.append(byte & 0x0F)
                    pixels.append((byte >> 4) & 0x0F)
                pixels = bytes(pixels[:px_w * px_h])
                if len(pixels) < px_w * px_h:
                    return None
                img = Image.frombytes('P', (px_w, px_h), pixels)
                img.putpalette(palette)
                return img.convert('RGBA')

            elif self.bpp == 2:  # 16bpp BGR5551
                px_w = self.img_w
                px_h = self.img_h
                pixels = []
                for i in range(0, min(len(self.img_data), px_w * px_h * 2), 2):
                    c = struct.unpack_from('<H', self.img_data, i)[0]
                    r = (c & 0x1F) << 3
                    g = ((c >> 5) & 0x1F) << 3
                    b = ((c >> 10) & 0x1F) << 3
                    a = 0 if (c == 0) else 255
                    pixels.extend([r, g, b, a])
                img = Image.frombytes('RGBA', (px_w, px_h), bytes(pixels))
                return img

            elif self.bpp == 3:  # 24bpp
                px_w = self.img_w
                px_h = self.img_h
                img = Image.frombytes('RGB', (px_w, px_h), self.img_data[:px_w * px_h * 3])
                return img.convert('RGBA')

        except Exception:
            return None

    def _build_palette(self, count):
        palette = []
        for i in range(count):
            if i * 2 + 1 < len(self.clut_data):
                c = struct.unpack_from('<H', self.clut_data, i * 2)[0]
                r = (c & 0x1F) << 3
                g = ((c >> 5) & 0x1F) << 3
                b = ((c >> 10) & 0x1F) << 3
                palette.extend([r, g, b])
            else:
                palette.extend([0, 0, 0])
        # Pad to 256
        while len(palette) < 256 * 3:
            palette.extend([0, 0, 0])
        return palette

    @property
    def pixel_width(self):
        return self.img_w * {0: 4, 1: 2, 2: 1, 3: 1}.get(self.bpp, 1)

    @property
    def pixel_height(self):
        return self.img_h

    @property
    def bpp_name(self):
        return self.BPP_NAMES.get(self.bpp, f'?{self.bpp}bpp')

    @property
    def vram_pos(self):
        return f"({self.img_x}, {self.img_y})"


class BINFile:
    """Parsed BIN container holding multiple TIM images."""

    def __init__(self, path):
        self.path = Path(path)
        self.name = self.path.name
        self.tims = []
        self.raw_data = b''
        self.error = None
        self._parse()

    def _parse(self):
        try:
            with open(self.path, 'rb') as f:
                self.raw_data = f.read()

            if len(self.raw_data) < 8:
                self.error = "File too small"
                return

            num = struct.unpack_from('<I', self.raw_data, 0)[0]
            if num == 0 or num > 512:
                self.error = f"Unexpected entry count: {num}"
                return

            offsets = []
            for i in range(num):
                pos = 4 + i * 4
                if pos + 4 > len(self.raw_data):
                    break
                offsets.append(struct.unpack_from('<I', self.raw_data, pos)[0])

            for off in offsets:
                if off >= len(self.raw_data):
                    continue
                tim = TIMImage.from_data(self.raw_data, off)
                if tim:
                    self.tims.append(tim)

        except Exception as e:
            self.error = str(e)


def pil_to_qpixmap(pil_img):
    """Convert PIL Image to QPixmap."""
    if pil_img is None:
        return None
    if pil_img.mode != 'RGBA':
        pil_img = pil_img.convert('RGBA')
    data = pil_img.tobytes('raw', 'RGBA')
    qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(qimg)


# ─────────────────────────────────────────────
#  CHECKERBOARD BACKGROUND WIDGET (transparency)
# ─────────────────────────────────────────────

class ImageCanvas(QLabel):
    """Displays a pixmap on a checkerboard background with zoom support."""

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pixmap = None
        self._zoom = 1.0
        self._checker_size = 8
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_image(self, pixmap):
        self._pixmap = pixmap
        self._zoom = 1.0
        self._update_display()

    def set_zoom(self, zoom):
        self._zoom = max(0.25, min(16.0, zoom))
        self._update_display()

    def _update_display(self):
        if self._pixmap is None:
            self.clear()
            return
        w = int(self._pixmap.width() * self._zoom)
        h = int(self._pixmap.height() * self._zoom)
        scaled = self._pixmap.scaled(
            w, h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )
        # Compose on checkerboard
        checker = self._make_checker(scaled.width(), scaled.height())
        painter = QPainter(checker)
        painter.drawPixmap(0, 0, scaled)
        painter.end()
        self.setPixmap(checker)

    def _make_checker(self, w, h):
        pm = QPixmap(w, h)
        painter = QPainter(pm)
        cs = self._checker_size
        c1 = QColor(60, 60, 60)
        c2 = QColor(80, 80, 80)
        for y in range(0, h, cs):
            for x in range(0, w, cs):
                color = c1 if ((x // cs + y // cs) % 2 == 0) else c2
                painter.fillRect(x, y, min(cs, w - x), min(cs, h - y), color)
        painter.end()
        return pm

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.set_zoom(self._zoom * 1.25)
        else:
            self.set_zoom(self._zoom / 1.25)

    @property
    def zoom(self):
        return self._zoom


# ─────────────────────────────────────────────
#  INFO PANEL
# ─────────────────────────────────────────────

class InfoPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedWidth(220)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        title = QLabel("IMAGE INFO")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        self._fields = {}
        for key in ['File', 'Index', 'Offset', 'BPP', 'Size (px)', 'VRAM pos',
                    'CLUT', 'CLUT size', 'Raw size', 'Zoom']:
            row = QHBoxLayout()
            lbl = QLabel(key)
            lbl.setObjectName("infoKey")
            lbl.setFixedWidth(72)
            val = QLabel("—")
            val.setObjectName("infoVal")
            val.setWordWrap(True)
            row.addWidget(lbl)
            row.addWidget(val)
            layout.addLayout(row)
            self._fields[key] = val

        layout.addStretch()

        # Zoom controls
        zoom_group = QGroupBox("ZOOM")
        zoom_group.setObjectName("zoomGroup")
        zl = QVBoxLayout(zoom_group)
        self.zoom_label = QLabel("1.0×")
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_label.setObjectName("zoomLabel")

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(1, 64)   # 0.25× to 16×
        self.zoom_slider.setValue(4)        # 1×
        self.zoom_slider.setTickInterval(4)

        btn_row = QHBoxLayout()
        self.btn_fit = QPushButton("FIT")
        self.btn_1x = QPushButton("1×")
        self.btn_2x = QPushButton("2×")
        self.btn_4x = QPushButton("4×")
        for b in [self.btn_fit, self.btn_1x, self.btn_2x, self.btn_4x]:
            b.setObjectName("zoomBtn")
            b.setFixedHeight(22)
            btn_row.addWidget(b)

        zl.addWidget(self.zoom_label)
        zl.addWidget(self.zoom_slider)
        zl.addLayout(btn_row)
        layout.addWidget(zoom_group)

        # Export button
        self.btn_export = QPushButton("⬇  EXPORT PNG")
        self.btn_export.setObjectName("exportBtn")
        self.btn_export.setEnabled(False)
        layout.addWidget(self.btn_export)

        self.btn_export_all = QPushButton("⬇  EXPORT ALL")
        self.btn_export_all.setObjectName("exportBtn")
        self.btn_export_all.setEnabled(False)
        layout.addWidget(self.btn_export_all)

    def update_info(self, tim, file_name, index, zoom):
        if tim is None:
            for v in self._fields.values():
                v.setText("—")
            return
        clut_str = f"{tim.clut_w}×{tim.clut_h} @ ({tim.clut_x},{tim.clut_y})" if tim.has_clut else "none"
        self._fields['File'].setText(file_name)
        self._fields['Index'].setText(str(index))
        self._fields['Offset'].setText(f"0x{tim.offset:06X}")
        self._fields['BPP'].setText(tim.bpp_name)
        self._fields['Size (px)'].setText(f"{tim.pixel_width} × {tim.pixel_height}")
        self._fields['VRAM pos'].setText(tim.vram_pos)
        self._fields['CLUT'].setText(clut_str)
        self._fields['CLUT size'].setText(f"{len(tim.clut_data)} B" if tim.has_clut else "—")
        self._fields['Raw size'].setText(f"{tim.raw_size:,} B")
        self._fields['Zoom'].setText(f"{zoom:.2f}×")

    def set_zoom_display(self, zoom):
        self._fields['Zoom'].setText(f"{zoom:.2f}×")
        self.zoom_label.setText(f"{zoom:.2f}×")
        # Update slider without triggering signal
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(max(1, min(64, int(zoom * 4))))
        self.zoom_slider.blockSignals(False)


# ─────────────────────────────────────────────
#  THUMBNAIL STRIP
# ─────────────────────────────────────────────

class ThumbnailStrip(QListWidget):
    image_selected = pyqtSignal(int)

    THUMB = 80

    def __init__(self):
        super().__init__()
        self.setFlow(QListWidget.Flow.LeftToRight)
        self.setWrapping(False)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setIconSize(QSize(self.THUMB, self.THUMB))
        self.setFixedHeight(self.THUMB + 28)
        self.setSpacing(4)
        self.setObjectName("thumbStrip")
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.currentRowChanged.connect(self.image_selected.emit)

    def load_tims(self, tims):
        self.clear()
        checker_pm = self._make_checker(self.THUMB, self.THUMB)
        for i, tim in enumerate(tims):
            if tim.pil_image:
                pm = pil_to_qpixmap(tim.pil_image)
                if pm:
                    # Composite on checker
                    result = QPixmap(checker_pm)
                    p = QPainter(result)
                    scaled = pm.scaled(self.THUMB, self.THUMB,
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.FastTransformation)
                    ox = (self.THUMB - scaled.width()) // 2
                    oy = (self.THUMB - scaled.height()) // 2
                    p.drawPixmap(ox, oy, scaled)
                    p.end()
                    icon = QIcon(result)
                else:
                    icon = QIcon()
            else:
                icon = QIcon()

            item = QListWidgetItem(icon, f"{i:02d}")
            item.setToolTip(f"#{i:02d}  {tim.bpp_name}  {tim.pixel_width}×{tim.pixel_height}")
            item.setSizeHint(QSize(self.THUMB + 4, self.THUMB + 20))
            self.addItem(item)

    def _make_checker(self, w, h):
        pm = QPixmap(w, h)
        p = QPainter(pm)
        cs = 8
        c1, c2 = QColor(55, 55, 55), QColor(70, 70, 70)
        for y in range(0, h, cs):
            for x in range(0, w, cs):
                p.fillRect(x, y, cs, cs, c1 if (x // cs + y // cs) % 2 == 0 else c2)
        p.end()
        return pm


# ─────────────────────────────────────────────
#  FILE TREE
# ─────────────────────────────────────────────

class FileTree(QTreeWidget):
    file_selected = pyqtSignal(str)  # path

    def __init__(self):
        super().__init__()
        self.setHeaderLabel("LOADED FILES")
        self.setObjectName("fileTree")
        self.setRootIsDecorated(True)
        self.setAnimated(True)
        self.setIndentation(16)
        self.itemClicked.connect(self._on_click)
        self._path_map = {}  # item id -> path

    def add_bin(self, bin_file):
        root = QTreeWidgetItem(self, [f"📦  {bin_file.name}"])
        root.setData(0, Qt.ItemDataRole.UserRole, str(bin_file.path))
        root.setExpanded(True)
        for i, tim in enumerate(bin_file.tims):
            child = QTreeWidgetItem(root, [f"  🖼  [{i:02d}] {tim.bpp_name}  {tim.pixel_width}×{tim.pixel_height}"])
            child.setData(0, Qt.ItemDataRole.UserRole, f"{bin_file.path}::{i}")
        self._path_map[id(root)] = str(bin_file.path)

    def _on_click(self, item, col):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            self.file_selected.emit(str(data))


# ─────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OTCB1 Viewer — Option Tuning Car Battle 1")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        self._loaded_bins = {}   # path -> BINFile
        self._current_bin = None
        self._current_index = 0

        self._build_ui()
        self._apply_style()
        self._connect_signals()
        self.setAcceptDrops(True)

    # ── UI Construction ──────────────────────

    def _build_ui(self):
        # Menu bar
        mb = self.menuBar()
        file_menu = mb.addMenu("File")
        act_open = QAction("Open BIN file…", self)
        act_open.setShortcut(QKeySequence.StandardKey.Open)
        act_open.triggered.connect(self.open_files)
        act_export = QAction("Export current image…", self)
        act_export.triggered.connect(self._export_current)
        act_export_all = QAction("Export all images…", self)
        act_export_all.triggered.connect(self._export_all)
        act_quit = QAction("Quit", self)
        act_quit.setShortcut(QKeySequence.StandardKey.Quit)
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_open)
        file_menu.addSeparator()
        file_menu.addAction(act_export)
        file_menu.addAction(act_export_all)
        file_menu.addSeparator()
        file_menu.addAction(act_quit)

        view_menu = mb.addMenu("View")
        act_1x = QAction("Zoom 1×", self)
        act_1x.triggered.connect(lambda: self._set_zoom(1.0))
        act_2x = QAction("Zoom 2×", self)
        act_2x.triggered.connect(lambda: self._set_zoom(2.0))
        act_4x = QAction("Zoom 4×", self)
        act_4x.triggered.connect(lambda: self._set_zoom(4.0))
        view_menu.addActions([act_1x, act_2x, act_4x])

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left: file tree
        self.file_tree = FileTree()
        self.file_tree.setFixedWidth(240)

        # Middle: canvas + thumb strip
        mid = QWidget()
        mid_layout = QVBoxLayout(mid)
        mid_layout.setContentsMargins(0, 0, 0, 0)
        mid_layout.setSpacing(0)

        # Toolbar row
        toolbar = QWidget()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(36)
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(8, 0, 8, 0)
        tl.setSpacing(6)

        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")
        self.btn_prev.setObjectName("navBtn")
        self.btn_next.setObjectName("navBtn")
        self.btn_prev.setFixedSize(28, 28)
        self.btn_next.setFixedSize(28, 28)

        self.img_counter = QLabel("—")
        self.img_counter.setObjectName("imgCounter")

        self.filename_label = QLabel("No file loaded")
        self.filename_label.setObjectName("filenameLabel")

        open_btn = QPushButton("+ OPEN BIN")
        open_btn.setObjectName("openBtn")
        open_btn.clicked.connect(self.open_files)

        tl.addWidget(self.btn_prev)
        tl.addWidget(self.img_counter)
        tl.addWidget(self.btn_next)
        tl.addSpacing(12)
        tl.addWidget(self.filename_label)
        tl.addStretch()
        tl.addWidget(open_btn)

        # Canvas
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("canvasScroll")
        self.canvas = ImageCanvas()
        self.scroll_area.setWidget(self.canvas)

        # Drop hint
        self.drop_hint = QLabel("Drop BIN files here\nor click + OPEN BIN")
        self.drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_hint.setObjectName("dropHint")

        # Stack canvas and hint
        self.canvas_container = QWidget()
        cc_layout = QVBoxLayout(self.canvas_container)
        cc_layout.setContentsMargins(0, 0, 0, 0)
        cc_layout.addWidget(self.drop_hint)
        cc_layout.addWidget(self.scroll_area)
        self.scroll_area.hide()

        # Thumb strip
        self.thumb_strip = ThumbnailStrip()

        mid_layout.addWidget(toolbar)
        mid_layout.addWidget(self.canvas_container, 1)
        mid_layout.addWidget(self.thumb_strip)

        # Right: info panel
        self.info_panel = InfoPanel()

        main_layout.addWidget(self.file_tree)
        main_layout.addWidget(mid, 1)
        main_layout.addWidget(self.info_panel)

        # Status bar
        self.status = QStatusBar()
        self.status.setObjectName("statusBar")
        self.setStatusBar(self.status)
        self.status.showMessage("Ready  —  open a BIN file to begin")

    def _connect_signals(self):
        self.btn_prev.clicked.connect(self._prev_image)
        self.btn_next.clicked.connect(self._next_image)
        self.thumb_strip.image_selected.connect(self._select_image)
        self.file_tree.file_selected.connect(self._on_tree_select)

        self.info_panel.zoom_slider.valueChanged.connect(
            lambda v: self._set_zoom(v / 4.0)
        )
        self.info_panel.btn_1x.clicked.connect(lambda: self._set_zoom(1.0))
        self.info_panel.btn_2x.clicked.connect(lambda: self._set_zoom(2.0))
        self.info_panel.btn_4x.clicked.connect(lambda: self._set_zoom(4.0))
        self.info_panel.btn_fit.clicked.connect(self._fit_zoom)
        self.info_panel.btn_export.clicked.connect(self._export_current)
        self.info_panel.btn_export_all.clicked.connect(self._export_all)

    # ── File Loading ─────────────────────────

    def open_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Open BIN file(s)", "",
            "BIN files (*.BIN *.bin);;All files (*)"
        )
        for path in paths:
            self._load_bin(path)

    def _load_bin(self, path):
        path = str(path)
        if path in self._loaded_bins:
            self.status.showMessage(f"Already loaded: {os.path.basename(path)}")
            return

        self.status.showMessage(f"Loading {os.path.basename(path)}…")
        QApplication.processEvents()

        bin_file = BINFile(path)
        if bin_file.error:
            self.status.showMessage(f"Error loading {bin_file.name}: {bin_file.error}")
            return

        self._loaded_bins[path] = bin_file
        self.file_tree.add_bin(bin_file)
        self._set_active_bin(bin_file)
        self.status.showMessage(
            f"Loaded {bin_file.name}  —  {len(bin_file.tims)} TIM images  "
            f"({os.path.getsize(path) // 1024} KB)"
        )

    def _set_active_bin(self, bin_file):
        self._current_bin = bin_file
        self._current_index = 0
        self.filename_label.setText(bin_file.name)
        self.thumb_strip.load_tims(bin_file.tims)
        self.drop_hint.hide()
        self.scroll_area.show()
        self.info_panel.btn_export.setEnabled(True)
        self.info_panel.btn_export_all.setEnabled(True)
        if bin_file.tims:
            self.thumb_strip.setCurrentRow(0)
            self._show_image(0)

    # ── Navigation ───────────────────────────

    def _prev_image(self):
        if self._current_bin and self._current_index > 0:
            self._select_image(self._current_index - 1)

    def _next_image(self):
        if self._current_bin and self._current_index < len(self._current_bin.tims) - 1:
            self._select_image(self._current_index + 1)

    def _select_image(self, index):
        if self._current_bin is None:
            return
        index = max(0, min(index, len(self._current_bin.tims) - 1))
        self._current_index = index
        self.thumb_strip.blockSignals(True)
        self.thumb_strip.setCurrentRow(index)
        self.thumb_strip.blockSignals(False)
        self._show_image(index)

    def _show_image(self, index):
        if not self._current_bin or index >= len(self._current_bin.tims):
            return
        tim = self._current_bin.tims[index]
        total = len(self._current_bin.tims)
        self.img_counter.setText(f"{index + 1} / {total}")
        self.btn_prev.setEnabled(index > 0)
        self.btn_next.setEnabled(index < total - 1)

        if tim.pil_image:
            pm = pil_to_qpixmap(tim.pil_image)
            self.canvas.set_image(pm)
        else:
            self.canvas.set_image(None)
            self.canvas.setText("⚠ Could not decode image")

        self.info_panel.update_info(
            tim, self._current_bin.name, index, self.canvas.zoom
        )

    def _on_tree_select(self, data):
        if '::' in data:
            path, idx_str = data.rsplit('::', 1)
            if path in self._loaded_bins:
                bin_file = self._loaded_bins[path]
                if self._current_bin is not bin_file:
                    self._set_active_bin(bin_file)
                self._select_image(int(idx_str))
        else:
            if data in self._loaded_bins:
                self._set_active_bin(self._loaded_bins[data])

    # ── Zoom ─────────────────────────────────

    def _set_zoom(self, zoom):
        self.canvas.set_zoom(zoom)
        self.info_panel.set_zoom_display(self.canvas.zoom)
        if self._current_bin:
            tim = self._current_bin.tims[self._current_index]
            self.info_panel.update_info(
                tim, self._current_bin.name, self._current_index, self.canvas.zoom
            )

    def _fit_zoom(self):
        if self._current_bin and self._current_bin.tims:
            tim = self._current_bin.tims[self._current_index]
            if tim.pil_image:
                cw = self.scroll_area.width() - 20
                ch = self.scroll_area.height() - 20
                zx = cw / max(tim.pixel_width, 1)
                zy = ch / max(tim.pixel_height, 1)
                self._set_zoom(min(zx, zy))

    # ── Export ───────────────────────────────

    def _export_current(self):
        if not self._current_bin:
            return
        tim = self._current_bin.tims[self._current_index]
        if tim.pil_image is None:
            return
        stem = self._current_bin.path.stem
        default = f"{stem}_{self._current_index:02d}.png"
        path, _ = QFileDialog.getSaveFileName(self, "Export image", default, "PNG (*.png)")
        if path:
            tim.pil_image.save(path)
            self.status.showMessage(f"Exported: {path}")

    def _export_all(self):
        if not self._current_bin:
            return
        dir_path = QFileDialog.getExistingDirectory(self, "Export all images to folder")
        if not dir_path:
            return
        stem = self._current_bin.path.stem
        count = 0
        for i, tim in enumerate(self._current_bin.tims):
            if tim.pil_image:
                out = os.path.join(dir_path, f"{stem}_{i:02d}.png")
                tim.pil_image.save(out)
                count += 1
        self.status.showMessage(f"Exported {count} images to {dir_path}")

    # ── Keyboard ─────────────────────────────

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key.Key_Left, Qt.Key.Key_A):
            self._prev_image()
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
            self._next_image()
        elif key == Qt.Key.Key_1:
            self._set_zoom(1.0)
        elif key == Qt.Key.Key_2:
            self._set_zoom(2.0)
        elif key == Qt.Key.Key_4:
            self._set_zoom(4.0)
        elif key == Qt.Key.Key_F:
            self._fit_zoom()
        elif key == Qt.Key.Key_O and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.open_files()
        else:
            super().keyPressEvent(event)

    # ── Drag & Drop ──────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.upper().endswith('.BIN'):
                self._load_bin(path)

    # ── Style ────────────────────────────────

    def _apply_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background: #0f0f0f;
            }

            QMenuBar {
                background: #0f0f0f;
                color: #c8b89a;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                border-bottom: 1px solid #2a2a2a;
                padding: 2px 0;
            }
            QMenuBar::item:selected {
                background: #1e1e1e;
                color: #e8d5b0;
            }
            QMenu {
                background: #141414;
                color: #c8b89a;
                border: 1px solid #2a2a2a;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
            QMenu::item:selected {
                background: #ff6b00;
                color: #000;
            }

            /* File tree */
            QTreeWidget#fileTree {
                background: #0c0c0c;
                color: #8a9a7a;
                border: none;
                border-right: 1px solid #1e1e1e;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                outline: none;
            }
            QTreeWidget#fileTree::item:selected {
                background: #1a2a1a;
                color: #a8d890;
            }
            QTreeWidget#fileTree::item:hover {
                background: #141414;
            }
            QHeaderView::section {
                background: #0c0c0c;
                color: #ff6b00;
                border: none;
                border-bottom: 1px solid #2a2a2a;
                padding: 4px 8px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                letter-spacing: 2px;
            }

            /* Toolbar */
            QWidget#toolbar {
                background: #111111;
                border-bottom: 1px solid #1e1e1e;
            }
            QPushButton#navBtn {
                background: #1a1a1a;
                color: #c8b89a;
                border: 1px solid #2a2a2a;
                border-radius: 3px;
                font-size: 12px;
                font-family: 'Courier New', monospace;
            }
            QPushButton#navBtn:hover {
                background: #ff6b00;
                color: #000;
                border-color: #ff6b00;
            }
            QPushButton#navBtn:disabled {
                color: #333;
                border-color: #1a1a1a;
            }
            QLabel#imgCounter {
                color: #ff6b00;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                font-weight: bold;
                min-width: 60px;
            }
            QLabel#filenameLabel {
                color: #7a8a6a;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
            QPushButton#openBtn {
                background: transparent;
                color: #ff6b00;
                border: 1px solid #ff6b00;
                border-radius: 3px;
                padding: 4px 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                letter-spacing: 1px;
            }
            QPushButton#openBtn:hover {
                background: #ff6b00;
                color: #000;
            }

            /* Canvas */
            QScrollArea#canvasScroll {
                background: #0a0a0a;
                border: none;
            }
            QLabel#dropHint {
                background: #0a0a0a;
                color: #2a3a2a;
                font-family: 'Courier New', monospace;
                font-size: 18px;
                border: 2px dashed #1e2e1e;
                margin: 40px;
                border-radius: 8px;
            }

            /* Thumbnail strip */
            QListWidget#thumbStrip {
                background: #090909;
                border: none;
                border-top: 1px solid #1e1e1e;
                outline: none;
            }
            QListWidget#thumbStrip::item {
                color: #5a6a4a;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                border: 1px solid transparent;
                border-radius: 3px;
            }
            QListWidget#thumbStrip::item:selected {
                background: #1a2a1a;
                border: 1px solid #ff6b00;
                color: #ff6b00;
            }
            QListWidget#thumbStrip::item:hover {
                border: 1px solid #2a3a2a;
            }

            /* Info panel */
            QFrame {
                background: #0c0c0c;
                border-left: 1px solid #1e1e1e;
            }
            QLabel#panelTitle {
                color: #ff6b00;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                letter-spacing: 3px;
                font-weight: bold;
                border-bottom: 1px solid #1e1e1e;
                padding-bottom: 6px;
                margin-bottom: 4px;
            }
            QLabel#infoKey {
                color: #4a5a3a;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
            QLabel#infoVal {
                color: #9aaa8a;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
            QGroupBox#zoomGroup {
                color: #4a5a3a;
                border: 1px solid #1e1e1e;
                border-radius: 4px;
                margin-top: 8px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                letter-spacing: 2px;
            }
            QGroupBox#zoomGroup::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }
            QLabel#zoomLabel {
                color: #ff6b00;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                font-weight: bold;
            }
            QSlider::groove:horizontal {
                height: 3px;
                background: #1e1e1e;
                border-radius: 1px;
            }
            QSlider::handle:horizontal {
                background: #ff6b00;
                width: 12px;
                height: 12px;
                margin: -5px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #ff6b00;
                border-radius: 1px;
            }
            QPushButton#zoomBtn {
                background: #141414;
                color: #6a7a5a;
                border: 1px solid #1e1e1e;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                padding: 2px;
            }
            QPushButton#zoomBtn:hover {
                background: #ff6b00;
                color: #000;
                border-color: #ff6b00;
            }
            QPushButton#exportBtn {
                background: transparent;
                color: #6a9a5a;
                border: 1px solid #2a3a2a;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                letter-spacing: 1px;
            }
            QPushButton#exportBtn:hover {
                background: #2a3a2a;
                color: #aada9a;
                border-color: #6a9a5a;
            }
            QPushButton#exportBtn:disabled {
                color: #2a2a2a;
                border-color: #1a1a1a;
            }

            /* Scrollbars */
            QScrollBar:vertical {
                background: #0c0c0c;
                width: 8px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #2a2a2a;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #ff6b00;
            }
            QScrollBar:horizontal {
                background: #0c0c0c;
                height: 8px;
                border: none;
            }
            QScrollBar::handle:horizontal {
                background: #2a2a2a;
                border-radius: 4px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #ff6b00;
            }
            QScrollBar::add-line, QScrollBar::sub-line { background: none; }

            /* Status bar */
            QStatusBar#statusBar {
                background: #0a0a0a;
                color: #4a5a3a;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                border-top: 1px solid #1a1a1a;
            }
        """)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("OTCB1 Viewer")
    app.setStyle("Fusion")

    # Dark base palette so native widgets inherit the theme
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(15, 15, 15))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(200, 184, 154))
    palette.setColor(QPalette.ColorRole.Base, QColor(12, 12, 12))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(20, 20, 20))
    palette.setColor(QPalette.ColorRole.Text, QColor(154, 170, 138))
    palette.setColor(QPalette.ColorRole.Button, QColor(20, 20, 20))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(200, 184, 154))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(255, 107, 0))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

    win = MainWindow()
    win.show()

    # Load any files passed as CLI args
    for arg in sys.argv[1:]:
        if arg.upper().endswith('.BIN') and os.path.isfile(arg):
            win._load_bin(arg)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()