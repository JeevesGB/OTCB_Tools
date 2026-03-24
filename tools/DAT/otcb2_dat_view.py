import sys, struct
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QOpenGLWidget
from OpenGL.GL import *

HDR_SIZE = 40
REC_SIZE = 20


# ─────────────────────────────
# PARSER (same logic)
# ─────────────────────────────
def parse_dat(data):
    header_vals = struct.unpack("<10I", data[:40])

    header = {
        "id": header_vals[0],
        "faceCount": header_vals[6],
        "totalVerts": header_vals[5],
    }

    prims = []
    colors = {}

    total = (len(data) - HDR_SIZE) // REC_SIZE

    for i in range(total):
        o = HDR_SIZE + i * REC_SIZE
        c = data[o:o+REC_SIZE]

        r, g, b = c[0], c[1], c[2]
        v0 = struct.unpack("<H", c[10:12])[0]
        v1 = struct.unpack("<H", c[12:14])[0]
        v2 = struct.unpack("<H", c[14:16])[0]
        v3 = struct.unpack("<H", c[16:18])[0]

        if r == g == b == 0:
            continue

        hexcol = f"#{r:02X}{g:02X}{b:02X}"

        prims.append({
            "i": i,
            "color": (r/255, g/255, b/255),
            "hex": hexcol,
            "v": [v0, v1, v2, v3],
        })

        colors[hexcol] = colors.get(hexcol, 0) + 1

    return header, prims, colors


# ─────────────────────────────
# OPENGL VIEWPORT
# ─────────────────────────────
class GLView(QOpenGLWidget):
    primSelected = QtCore.pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.prims = []
        self.zoom = 1.0
        self.offset = [0, 0]
        self.last = None
        self.selected = -1

    def set_data(self, prims):
        self.prims = prims
        self.update()

    def initializeGL(self):
        glClearColor(0.05, 0.06, 0.07, 1)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        glPushMatrix()
        glTranslatef(self.offset[0], self.offset[1], 0)
        glScalef(self.zoom, self.zoom, 1)

        for p in self.prims:
            x = (p["v"][0] & 0xFF) * 12
            y = (p["v"][0] >> 8) * 12

            glColor3f(*p["color"])
            if p["i"] == self.selected:
                glColor3f(0, 1, 1)

            glBegin(GL_LINE_LOOP)
            glVertex2f(x, y)
            glVertex2f(x+10, y)
            glVertex2f(x+10, y+10)
            glVertex2f(x, y+10)
            glEnd()

        glPopMatrix()

    def mousePressEvent(self, e):
        self.last = e.pos()

    def mouseMoveEvent(self, e):
        if self.last:
            dx = e.x() - self.last.x()
            dy = e.y() - self.last.y()
            self.offset[0] += dx
            self.offset[1] += dy
            self.last = e.pos()
            self.update()

    def mouseReleaseEvent(self, e):
        self.last = None

    def wheelEvent(self, e):
        self.zoom *= 1.1 if e.angleDelta().y() > 0 else 0.9
        self.update()


# ─────────────────────────────
# INFO PANEL (RIGHT SIDE)
# ─────────────────────────────
class InfoPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout(self)

        self.selLabel = QtWidgets.QLabel("No selection")
        self.colorBox = QtWidgets.QLabel()
        self.colorBox.setFixedHeight(40)

        self.vertLabel = QtWidgets.QLabel()

        self.layout.addWidget(QtWidgets.QLabel("Selection"))
        self.layout.addWidget(self.selLabel)

        self.layout.addWidget(QtWidgets.QLabel("Colour"))
        self.layout.addWidget(self.colorBox)

        self.layout.addWidget(QtWidgets.QLabel("Vertices"))
        self.layout.addWidget(self.vertLabel)

        self.layout.addStretch()

    def update_info(self, prim):
        if not prim:
            return

        self.selLabel.setText(f"Primitive #{prim['i']}")

        self.colorBox.setStyleSheet(f"background:{prim['hex']}")

        self.vertLabel.setText(
            f"V0: {prim['v'][0]}\nV1: {prim['v'][1]}\n"
            f"V2: {prim['v'][2]}\nV3: {prim['v'][3]}"
        )


# ─────────────────────────────
# MAIN WINDOW (FULL LAYOUT)
# ─────────────────────────────
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OTCB2 DAT Viewer PRO (OpenGL)")
        self.resize(1600, 900)

        self.gl = GLView()
        self.info = InfoPanel()

        # Sidebar
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setMaximumWidth(300)

        self.primList = QtWidgets.QListWidget()
        self.tabs.addTab(self.primList, "PRIMS")

        self.palette = QtWidgets.QListWidget()
        self.tabs.addTab(self.palette, "PALETTE")

        self.headerBox = QtWidgets.QTextEdit()
        self.tabs.addTab(self.headerBox, "HEADER")

        # Layout
        main = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(main)

        layout.addWidget(self.tabs)
        layout.addWidget(self.gl, 1)
        layout.addWidget(self.info)

        self.setCentralWidget(main)

        # Menu
        openAct = QtWidgets.QAction("Open", self)
        openAct.triggered.connect(self.open_file)
        self.menuBar().addMenu("File").addAction(openAct)

        # Signals
        self.primList.currentRowChanged.connect(self.select_prim)

        self.prims = []

    def open_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open DAT", "", "*.dat")
        if not path:
            return

        with open(path, "rb") as f:
            data = f.read()

        header, prims, colors = parse_dat(data)

        self.prims = prims
        self.gl.set_data(prims)

        self.primList.clear()
        for p in prims:
            self.primList.addItem(f"#{p['i']} {p['hex']}")

        self.palette.clear()
        for c, count in colors.items():
            self.palette.addItem(f"{c} ({count})")

        self.headerBox.setText(str(header))

    def select_prim(self, idx):
        if idx < 0 or idx >= len(self.prims):
            return

        p = self.prims[idx]
        self.gl.selected = idx
        self.gl.update()
        self.info.update_info(p)


# ─────────────────────────────
# RUN
# ─────────────────────────────
app = QtWidgets.QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())