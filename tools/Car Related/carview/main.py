import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QTreeView,
     QTabWidget
)
from  PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import QDir

from carfile import CarFile
from viewer import Viewer
from tuning import TuningEditor
from hexview import HexView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OTCR Spec-R CAR Tool")

        splitter = QSplitter()
        self.setCentralWidget(splitter)

        # Left: file browser
        model = QFileSystemModel()
        model.setRootPath(QDir.currentPath())
        model.setNameFilters(["*.CAR", "*.car"])
        model.setNameFilterDisables(False)

        self.tree = QTreeView()
        self.tree.setModel(model)
        self.tree.setRootIndex(model.index(QDir.currentPath()))
        self.tree.clicked.connect(self.load_car)

        splitter.addWidget(self.tree)

        # Right: tabs
        self.tabs = QTabWidget()
        self.viewer = Viewer()
        self.tuning = TuningEditor()
        self.hexview = HexView()

        self.tabs.addTab(self.viewer, "Viewer")
        self.tabs.addTab(self.tuning, "Tuning")
        self.tabs.addTab(self.hexview, "Hex")

        splitter.addWidget(self.tabs)
        splitter.setSizes([300, 900])

    def load_car(self, index):
        path = index.model().filePath(index)
        if not path.lower().endswith(".car"):
            return

        self.car = CarFile(path)
        self.tuning.load(self.car)
        self.hexview.load(self.car.data)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("style.qss") as f:
        app.setStyleSheet(f.read())

    w = MainWindow()
    w.resize(1200, 700)
    w.show()
    sys.exit(app.exec())