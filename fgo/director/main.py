from PyQt5.QtWidgets import QApplication, QMainWindow

from fgo.ui.MainWindow import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.show()

class DirectorRunner():
    def run(self):
        app = QApplication([])
        w = MainWindow()
        app.exec_()
