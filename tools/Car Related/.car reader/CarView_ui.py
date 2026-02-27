from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtOpenGLWidgets import QOpenGLWidget  # Correct import for OpenGL widget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1060, 700)
        MainWindow.setMaximumSize(1060, 700)
        MainWindow.setStyleSheet("background: rgb(154, 154, 154)")
        
        # Initialize centralwidget without parent
        self.centralwidget = QtWidgets.QWidget()
        
        # Set a layout for centralwidget
        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)  # Create layout and set it to centralwidget
        MainWindow.setCentralWidget(self.centralwidget)  # Set the central widget for MainWindow
        
        self.openGLWidget = QOpenGLWidget(parent=self.centralwidget)
        self.openGLWidget.setGeometry(QtCore.QRect(240, -1, 821, 651))
        self.openGLWidget.setObjectName("openGLWidget")
        
        self.widget = QtWidgets.QWidget(parent=self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(10, 100, 221, 181))
        self.widget.setStyleSheet("background: rgb(220, 220, 220)\n"
"")
        self.widget.setObjectName("widget")
        
        self.pushButton = QtWidgets.QPushButton(parent=self.widget)
        self.pushButton.setGeometry(QtCore.QRect(20, 30, 181, 31))
        self.pushButton.setObjectName("pushButton")
        
        self.horizontalSlider = QtWidgets.QSlider(parent=self.widget)
        self.horizontalSlider.setGeometry(QtCore.QRect(19, 90, 181, 31))
        self.horizontalSlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        
        self.horizontalSlider_2 = QtWidgets.QSlider(parent=self.widget)
        self.horizontalSlider_2.setGeometry(QtCore.QRect(20, 140, 181, 31))
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 0, 221, 91))
        font = QtGui.QFont()
        font.setFamily("Microsoft Yi Baiti")
        font.setPointSize(50)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        
        self.textEdit = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(10, 280, 221, 371))
        self.textEdit.setStyleSheet("background: rgb(220, 220, 220)")
        self.textEdit.setObjectName("textEdit")
        
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1060, 22))
        self.menubar.setObjectName("menubar")
        
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.actionLoad_CAR_File = QtGui.QAction(parent=MainWindow)
        self.actionLoad_CAR_File.setObjectName("actionLoad_CAR_File")
        
        self.actionExit = QtGui.QAction(parent=MainWindow)
        self.actionExit.setObjectName("actionExit")
        
        self.menuFile.addAction(self.actionLoad_CAR_File)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        
        self.menubar.addAction(self.menuFile.menuAction())
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.label.setText(_translate("MainWindow", "CarView"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionLoad_CAR_File.setText(_translate("MainWindow", "Load .CAR File"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))