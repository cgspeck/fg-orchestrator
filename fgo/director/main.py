import atexit
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QLineEdit
from PyQt5.QtCore import QThreadPool

from fgo.ui.MainWindow import Ui_MainWindow

from fgo.director.listener import Listener
from fgo.director.registry import Registry
from fgo.director.registry_model import RegistryModel
from fgo.director.signals import Signals


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.registry = Registry()
        self.registry_model = RegistryModel(self, self.registry)
        self.tvAgents.setModel(self.registry_model)

        self.actionExit.triggered.connect(lambda: sys.exit(0))
        self.actionAddHost.triggered.connect(self.handle_add_host_triggered)
        self.signals = Signals()
        self.signals.agent_manually_added.connect(self.registry.handle_agent_manually_added)

        self.show()

        listener = Listener()
        atexit.register(listener.stop)
        listener.signals.zeroconf_agent_found.connect(self.registry.handle_zeroconf_agent_found)
        listener.signals.zeroconf_agent_removed.connect(self.registry.handle_zeroconf_agent_removed)
        listener.run()

    def handle_add_host_triggered(self):
        text, okPressed = QInputDialog.getText(
            self,
            'Add host',
            'Enter IP Address or hostname:',
            QLineEdit.Normal,
            ''
        )

        if okPressed and len(text.strip()) > 0:
            self.signals.agent_manually_added.emit(text.strip())


class DirectorRunner():
    def run(self):
        app = QApplication([])
        w = MainWindow()
        app.exec_()
