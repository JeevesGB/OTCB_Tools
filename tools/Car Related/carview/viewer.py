from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *

class Viewer(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.geometry = None
        self.rot_x = self.rot_y = 0

    def load_geometry(self, geometry):
        self.geometry = geometry
        self.update()

    def initializeGL(self):
        glDisable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glClearColor(0.05, 0.05, 0.07, 1.0)

    def resizeGL(self, w, h):
        if w <= 0 or h <= 0:
            return

        h = max(1, min(h, 4096))
        w = max(1, min(w, 4096))

        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(w) / float(h), 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if not self.geometry:
            return

        glLoadIdentity()
        glTranslatef(0, 0, -15)
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)

        glColor3f(0.8, 0.8, 0.9)
        glBegin(GL_LINES)
        for a, b, c in self.geometry.faces:
            for i, j in ((a,b), (b,c), (c,a)):
                glVertex3fv(self.geometry.vertices[i])
                glVertex3fv(self.geometry.vertices[j])
        glEnd()

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.MouseButton.LeftButton:
            self.rot_x += e.position().y() * 0.01
            self.rot_y += e.position().x() * 0.01
            self.update()