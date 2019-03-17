from enum import Enum, unique
import logging
import atexit
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QLineEdit, QMenu
from PyQt5.QtCore import pyqtSlot, Qt, QTimer, QThreadPool
from fgo.gql.types import TimeOfDay

from fgo.ui.MainWindow import Ui_MainWindow

from fgo.director.listener import Listener
from fgo.director.registry import Registry
from fgo.director.registry_model import RegistryModel
from fgo.director.signals import Signals

@unique
class SessionErrorCodes(Enum):
    UNKNOWN = 0

    def description(self):
        pass

@unique
class DirectorState(Enum):
    IDLE = 1
    INSTALLING_AIRCRAFT = 2
    WAITING_FOR_MASTER = 3
    WAITING_FOR_SLAVES = 4
    IN_SESSION = 5


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

        # file menu
        self.actionNew_Scenario.triggered.connect(self.handle_new_scenario)
        self.actionExit.triggered.connect(lambda: QApplication.exit(0))
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

        self.agent_check_timer = QTimer()
        self.agent_check_timer.timeout.connect(self.check_agent_status_and_update_model)
        self.agent_check_timer.start(10000)

        self._state = DirectorState.IDLE
        self.state_machine_timer = QTimer()
        self.state_machine_timer.timeout.connect(self.run_state_machine)
        self.state_machine_timer.start(10000)

        self._master_candidates = []
        self.registry.signals.master_candidate_add.connect(self.handle_master_candidate_add)
        self.registry.signals.master_candidate_remove.connect(self.handle_master_candidate_remove)

        self._scenario_file_path = None
        self._scenario_changed = False
        self._ai_scenarios = []

    def _set_defaults(self):
        # Basics tab
        self.leAircraft.setText('c172p')
        self.cbTimeOfDay.setCurrentIndex(0)
        self.cbMasterAgent.setCurrentIndex(-1)
        self.rbAirport.setChecked(True)
        self.leAirport.setText('YBBN')
        self.leCarrier.clear()
        self.rbRunway.setChecked(True)
        self.leRunway.setText('01')
        self.leParking.clear()
        # Advanced tab
        self.leTSEndpoint.setText('http://flightgear.sourceforge.net/scenery')
        self.leCeiling.clear()
        self.cbAutoCoordination.setChecked(True)
        self.leVisibilityMeters.clear()
        # Clear AI scenarios
        self._ai_scenarios = []
        # Reset open tab
        self.tabScenarioSettings.setCurrentIndex(0)
        # Reset agent custom settings
        self.registry.reset_all_custom_agent_settings_to_default()
        self._state = DirectorState.IDLE

    def handle_new_scenario(self):
        # reset the state
        self._scenario_file_path = None
        self._scenario_changed = False
        self._set_defaults()

    def start_session(self):
        errors = self.do_preflight_checks()

        if len(errors) > 0:
            # TODO: display a dialog with error codes
            pass

        aircraft = self.leAircraft.text.strip()

        if aircraft not in [None, "", "c172p"]:
            # TODO: call each of the agents and get them to install/update themselves
            self._state = DirectorState.INSTALLING_AIRCRAFT
            return

        # else startup the master
        self.start_master()
        self._state = DirectorState.WAITING_FOR_MASTER

    def run_state_machine(self):
        current_state = self._state
        next_state = current_state

        if current_state == DirectorState.INSTALLING_AIRCRAFT:
            # TODO: check whether all agents in the session are READY
            # TODO: if ready, start up the master and increment the state
            self.start_master()
            next_state = DirectorState.WAITING_FOR_MASTER
        elif current_state == DirectorState.WAITING_FOR_MASTER:
            # TODO: check whether the master is up
            # TODO: if it is up, start up the slaves
            self.start_slaves()
            next_state = DirectorState.WAITING_FOR_SLAVES
        elif current_state == DirectorState.WAITING_FOR_SLAVES:
            # TODO: check if the slaves are up
            # TODO: if up progress the state machine
            next_state = DirectorState.IN_SESSION
        elif current_state == DirectorState.IN_SESSION:
            # TODO: check to see whether all agents have dropped out
            # TODO: if so, set state to idle
            next_state = DirectorState.IDLE

        logging.debug(f"run_state_machine current_state: {current_state}, next_state: {next_state}")
        self.statusbar.showMessage(next_state.name.lower())
        self._state = next_state

    def do_preflight_checks(self):
        # what things need to be checked for??
        # return
        return []

    def start_master(self):
        '''Ask the designated master to start up'''
        pass

    def start_slaves(self):
        '''Ask the slaves to start up'''
        pass

    def check_agent_status_and_update_model(self):
        self.registry.check_agent_status()
        self.registry_model.updateModel()
        self.tvAgents.resizeColumnsToContents()

    @pyqtSlot(str)
    def handle_master_candidate_add(self, host):
        if host not in self._master_candidates:
            logging.info(f"Adding master candidate {host}")
            self.cbMasterAgent.addItem(host)
            self._master_candidates.append(host)

    @pyqtSlot(str)
    def handle_master_candidate_remove(self, host):
        if host in self._master_candidates:
            logging.info(f"Removing master candidate {host}")
            index = self._master_candidates.index(host)
            self.cbMasterAgent.removeItem(index)
            self._master_candidates.remove(host)

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
        reset_fail_count_action = menu.addAction("Reset fail count")
        reset_fail_count_action.setEnabled(False)
        remove_host_action = menu.addAction("Remove Host")

        if not self._selected_agent:
            customise_host_action.setEnabled(False)

            remove_host_action.setEnabled(False)
        else:
            host = self._selected_agent['host']

            if self.registry.is_agent_failed(host):
                reset_fail_count_action.setEnabled(True)

        res = menu.exec_(self.tvAgents.mapToGlobal(position))

        if res == remove_host_action:
            self.signals.agent_manually_removed.emit(
                self._selected_agent.get('host', None),
                self._selected_agent.get('uuid', None)
            )
            self._selected_agent = None
            self.registry_model.updateModel()
        if res == reset_fail_count_action:
            self.registry.reset_failed_count(host)
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
