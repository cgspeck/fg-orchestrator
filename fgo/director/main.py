import atexit

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThreadPool

from fgo.ui.MainWindow import Ui_MainWindow

from fgo.director.listener import Listener

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.show()

        listener = Listener()
        atexit.register(listener.stop)
        listener.run()


class DirectorRunner():
    def run(self):
        app = QApplication([])
        w = MainWindow()
        app.exec_()
