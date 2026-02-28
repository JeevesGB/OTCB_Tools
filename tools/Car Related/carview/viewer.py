# viewer.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class Viewer(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("3D Viewer (coming next)"))