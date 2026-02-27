import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QSlider, QWidget
from PySide6.QtCore import Qt
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
from CarView_ui import Ui_MainWindow  # Import the generated UI from Qt Designer
from car_parser import load_car_file  # Assuming car_parser.py contains load_car_file function

class OpenGLWidget(QOpenGLWidget):
    def __init__(self, meshes, parent=None):
        super().__init__(parent)
        self.meshes = meshes
        self.rotation_x = 0
        self.rotation_y = 0

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        gluPerspective(45, 1, 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Apply rotations based on the slider values
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)

        # Render meshes
        for vertices, indices in self.meshes:
            glBegin(GL_TRIANGLES)
            for i1, i2, i3 in indices:
                glVertex3fv(vertices[i1])
                glVertex3fv(vertices[i2])
                glVertex3fv(vertices[i3])
            glEnd()

        self.update()  # Keep updating the canvas

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        gluPerspective(45, w / h, 0.1, 50.0)

    def update_rotation(self, x, y):
        self.rotation_x = x
        self.rotation_y = y
        self.update()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Set up the UI from the .ui file

        # Initialize OpenGL widget (empty until a model is loaded)
        self.opengl_widget = None
        self.pushButton.clicked.connect(self.load_file)
        self.horizontalSlider.valueChanged.connect(self.update_rotation)
        self.horizontalSlider_2.valueChanged.connect(self.update_rotation)

    def update_rotation(self):
        if self.opengl_widget:
            self.opengl_widget.rotation_x = self.horizontalSlider.value()
            self.opengl_widget.rotation_y = self.horizontalSlider_2.value()
            self.opengl_widget.update()

    def load_file(self):
        # Open file dialog to choose the .car file
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CAR File", "", "CAR Files (*.car)")
        if file_path:
            meshes = load_car_file(file_path)  # Load meshes from the file
            self.textEdit.append(f"Loaded {len(meshes)} meshes from {file_path}")

            if self.opengl_widget:
                self.opengl_widget.deleteLater()  # Remove the previous OpenGL widget

            # Create a new OpenGLWidget and add it to the layout
            self.opengl_widget = OpenGLWidget(meshes)
            self.centralwidget.layout().addWidget(self.opengl_widget)
            self.opengl_widget.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())