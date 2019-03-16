import logging
import atexit
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QLineEdit, QMenu
from PyQt5.QtCore import Qt, QThreadPool

from fgo.gql.types import TimeOfDay

from fgo.ui.MainWindow import Ui_MainWindow

from fgo.director.listener import Listener
from fgo.director.registry import Registry
from fgo.director.registry_model import RegistryModel
from fgo.director.signals import Signals


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self._selected_agent = None

        self.registry = Registry()
        self.registry_model = RegistryModel(self, self.registry)
        self.tvAgents.setModel(self.registry_model)
        self.tvAgents.customContextMenuRequested.connect(self.handle_agents_context_menu_requested)
        self.tvAgents.clicked.connect(self.handle_agent_selected)

        self.actionExit.triggered.connect(lambda: sys.exit(0))
        self.actionAddHost.triggered.connect(self.handle_add_host_triggered)
        self.signals = Signals()
        self.signals.agent_manually_added.connect(self.registry.handle_agent_manually_added)
        self.signals.agent_manually_removed.connect(self.registry.handle_agent_manually_removed)

        # populate the TimeOfDay picker
        for time_of_day in TimeOfDay._meta.enum.__members__.values():
            self.cbTimeOfDay.addItem(time_of_day.lower_name)

        self.show()

        listener = Listener()
        atexit.register(listener.stop)
        listener.signals.zeroconf_agent_found.connect(self.registry.handle_zeroconf_agent_found)
        listener.signals.zeroconf_agent_removed.connect(self.registry.handle_zeroconf_agent_removed)
        listener.run()

    def handle_agent_selected(self, index):
        logging.debug(f"agent selected {index}")
        row = index.row()
        host_index = self.registry_model.createIndex(row, 0)
        uuid_index = self.registry_model.createIndex(row, 2)
        self._selected_agent = {
            'host': self.registry_model.data(host_index, Qt.DisplayRole),
            'uuid': self.registry_model.data(uuid_index, Qt.DisplayRole)
        }
        logging.debug(f"self._selected_agent={self._selected_agent}")

    def handle_agents_context_menu_requested(self, position):
        menu = QMenu()
        customise_host_action = menu.addAction("Custom Host Settings")
        remove_host_action = menu.addAction("Remove Host")

        if not self._selected_agent:
            customise_host_action.setEnabled(False)
            remove_host_action.setEnabled(False)

        res = menu.exec_(self.tvAgents.mapToGlobal(position))

        if res == remove_host_action:
            self.signals.agent_manually_removed.emit(
                self._selected_agent.get('host', None),
                self._selected_agent.get('uuid', None)
            )
            self._selected_agent = None
            self.registry_model.updateModel()

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
            self.registry_model.updateModel()


class DirectorRunner():
    def run(self):
        app = QApplication([])
        w = MainWindow()
        app.exec_()
