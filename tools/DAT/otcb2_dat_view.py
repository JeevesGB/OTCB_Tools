import sys, struct, ctypes
import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

HDR_SIZE = 40
REC_SIZE = 20


# ─────────────────────────────
# PARSER
# ─────────────────────────────
def parse_dat(data):
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

        if r == g == b == 0:
            continue

        hexcol = f"#{r:02X}{g:02X}{b:02X}"

        prims.append({
            "i": i,
            "color": (r/255, g/255, b/255),
            "hex": hexcol,
            "v": [v0, v1, v2]
        })

        colors[hexcol] = colors.get(hexcol, 0) + 1

    return prims, colors


# ─────────────────────────────
# SHADERS
# ─────────────────────────────
VERT = """
#version 330
layout(location=0) in vec3 pos;
layout(location=1) in vec3 col;
uniform mat4 mvp;
out vec3 vcol;
void main(){
    gl_Position = mvp * vec4(pos,1);
    vcol = col;
}
"""

FRAG = """
#version 330
in vec3 vcol;
out vec4 frag;
void main(){
    frag = vec4(vcol,1);
}
"""


# ─────────────────────────────
# OPENGL VIEW
# ─────────────────────────────
class GLView(QOpenGLWidget):
    primSelected = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.prims = []
        self.verts = None
        self.triangles = []   # ✅ FIXED

        self.rotX = 30
        self.rotY = -40
        self.dist = 200

        self.last = None
        self.mode = "both"
        self.selected = -1

    def set_data(self, prims):
        self.prims = prims
        self.build()
        self.update()

    def build(self):
        self.triangles = []   # ✅ ALWAYS RESET

        data = []

        for p in self.prims:
            tri = []
            for v in p["v"]:
                x = (v & 0xFF)
                y = (v >> 8)
                z = (v % 7) * 2

                data += [x, y, z] + list(p["color"])
                tri.append(np.array([x, y, z], dtype=float))

            self.triangles.append((p["i"], tri))

        self.verts = np.array(data, dtype=np.float32)

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)

        self.shader = compileProgram(
            compileShader(VERT, GL_VERTEX_SHADER),
            compileShader(FRAG, GL_FRAGMENT_SHADER)
        )

        self.vbo = glGenBuffers(1)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def paintGL(self):
        glClearColor(0.05, 0.06, 0.07, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.verts is None:
            return

        glUseProgram(self.shader)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.verts.nbytes, self.verts, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, False, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 3, GL_FLOAT, False, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        mvp = self.mvp()
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "mvp"), 1, GL_FALSE, mvp)

        if self.mode in ("flat", "both"):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glDrawArrays(GL_TRIANGLES, 0, len(self.verts)//6)

        if self.mode in ("wire", "both"):
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glDrawArrays(GL_TRIANGLES, 0, len(self.verts)//6)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def mvp(self):
        aspect = self.width()/max(1,self.height())
        proj = self.perspective(45, aspect, 0.1, 1000)
        view = self.translate(0,0,-self.dist)
        view = view @ self.rotX_m(self.rotX) @ self.rotY_m(self.rotY)
        return proj @ view

    def perspective(self,f,a,n,f2):
        t = 1/np.tan(np.radians(f)/2)
        return np.array([
            [t/a,0,0,0],
            [0,t,0,0],
            [0,0,(f2+n)/(n-f2),-1],
            [0,0,(2*f2*n)/(n-f2),0]
        ],dtype=np.float32)

    def translate(self,x,y,z):
        m = np.eye(4,dtype=np.float32)
        m[3][:3]=[x,y,z]
        return m

    def rotX_m(self,a):
        r=np.radians(a)
        return np.array([
            [1,0,0,0],
            [0,np.cos(r),-np.sin(r),0],
            [0,np.sin(r),np.cos(r),0],
            [0,0,0,1]
        ],dtype=np.float32)

    def rotY_m(self,a):
        r=np.radians(a)
        return np.array([
            [np.cos(r),0,np.sin(r),0],
            [0,1,0,0],
            [-np.sin(r),0,np.cos(r),0],
            [0,0,0,1]
        ],dtype=np.float32)

    # ───── INPUT ─────
    def mousePressEvent(self,e):
        self.last = e.pos()

    def mouseMoveEvent(self,e):
        if self.last is None:
            return
        dx = e.x()-self.last.x()
        dy = e.y()-self.last.y()
        self.rotY += dx*0.5
        self.rotX += dy*0.5
        self.last = e.pos()
        self.update()

    def mouseReleaseEvent(self,e):
        if self.last is None:
            return

        dx = abs(e.x() - self.last.x())
        dy = abs(e.y() - self.last.y())

        if dx < 4 and dy < 4:   # ✅ CLICK threshold
            self.pick(e.pos())

        self.last = None

    def wheelEvent(self,e):
        self.dist *= 0.9 if e.angleDelta().y()>0 else 1.1
        self.update()

    # ───── RAY PICKING ─────
    def pick(self, pos):
        if not self.triangles:   # ✅ SAFE GUARD
            return

        x = (2*pos.x()/self.width()-1)
        y = (1-2*pos.y()/self.height())

        inv = np.linalg.inv(self.mvp())

        near = inv @ np.array([x,y,-1,1])
        far  = inv @ np.array([x,y, 1,1])

        near /= near[3]
        far  /= far[3]

        dir = far[:3]-near[:3]

        best = None
        dist = 1e9

        for i,tri in self.triangles:
            hit = intersect(near[:3],dir,tri)
            if hit is not None:
                d = np.linalg.norm(hit-near[:3])
                if d < dist:
                    dist = d
                    best = i

        if best is not None:
            self.selected = best
            self.primSelected.emit(best)
            self.update()


def intersect(orig,dir,tri):
    v0,v1,v2 = tri
    eps = 1e-6
    e1 = v1-v0
    e2 = v2-v0
    h = np.cross(dir,e2)
    a = np.dot(e1,h)
    if -eps<a<eps: return None
    f=1/a
    s=orig-v0
    u=f*np.dot(s,h)
    if u<0 or u>1: return None
    q=np.cross(s,e1)
    v=f*np.dot(dir,q)
    if v<0 or u+v>1: return None
    t=f*np.dot(e2,q)
    return orig+dir*t if t>eps else None


# ─────────────────────────────
# INFO PANEL
# ─────────────────────────────
class InfoPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        l = QtWidgets.QVBoxLayout(self)

        self.sel = QtWidgets.QLabel("—")
        self.col = QtWidgets.QLabel()
        self.col.setFixedHeight(40)
        self.vert = QtWidgets.QLabel()

        l.addWidget(QtWidgets.QLabel("Selection"))
        l.addWidget(self.sel)
        l.addWidget(QtWidgets.QLabel("Colour"))
        l.addWidget(self.col)
        l.addWidget(QtWidgets.QLabel("Vertices"))
        l.addWidget(self.vert)
        l.addStretch()

    def update_info(self,p):
        self.sel.setText(f"#{p['i']}")
        self.col.setStyleSheet(f"background:{p['hex']}")
        self.vert.setText(str(p["v"]))


# ─────────────────────────────
# MAIN WINDOW
# ─────────────────────────────
class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OTCB2 DAT Viewer PRO")
        self.resize(1600,900)

        self.gl = GLView()
        self.info = InfoPanel()

        self.list = QtWidgets.QListWidget()
        self.palette = QtWidgets.QListWidget()

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self.list,"PRIMS")
        tabs.addTab(self.palette,"PALETTE")

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(tabs,1)
        layout.addWidget(self.gl,4)
        layout.addWidget(self.info,1)

        w = QtWidgets.QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        # menu
        act = QtWidgets.QAction("Open",self)
        act.triggered.connect(self.open)
        self.menuBar().addMenu("File").addAction(act)

        # connections
        self.list.currentRowChanged.connect(self.select)
        self.gl.primSelected.connect(self.select)

    def open(self):
        path,_=QtWidgets.QFileDialog.getOpenFileName(self,"Open DAT","","*.dat")
        if not path: return
        data=open(path,"rb").read()
        prims,colors = parse_dat(data)

        self.prims = prims
        self.gl.set_data(prims)

        self.list.clear()
        for p in prims:
            self.list.addItem(f"#{p['i']} {p['hex']}")

        self.palette.clear()
        for c,v in colors.items():
            self.palette.addItem(f"{c} ({v})")

    def select(self,i):
        if i<0 or i>=len(self.prims): return
        self.gl.selected=i
        self.gl.update()
        self.info.update_info(self.prims[i])


app = QtWidgets.QApplication(sys.argv)
app.setStyle("Fusion")
win = Main()
win.show()
sys.exit(app.exec_())