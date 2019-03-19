from enum import Enum, unique
import logging
import atexit
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QLineEdit, QMenu
from PyQt5.QtCore import pyqtSlot, Qt, QTimer, QThreadPool, QThread, QMetaObject
from fgo.gql.types import TimeOfDay

from fgo.ui.MainWindow import Ui_MainWindow

from fgo.director.registry import Registry
from fgo.director.registry_model import RegistryModel
from fgo.director.listener import Listener
from fgo.director.signals import MainUISignals
from fgo.director.agent_checker import AgentCheckerWorker
from fgo.director.checkbox_delegate import CheckBoxDelegate

from fgo.director.custom_settings_dialog import CustomSettingsDialog
from fgo.director.ai_scenarios_dialog import AiScenariosDialog

@unique
class SessionErrorCodes(Enum):
    UNKNOWN = 0

    def description(self):
        pass

@unique
class DirectorState(Enum):
    IDLE = 1
    START_SEQUENCE_REQUESTED = 6
    INSTALLING_AIRCRAFT = 2
    WAITING_FOR_MASTER = 3
    WAITING_FOR_SLAVES = 4
    IN_SESSION = 5


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.tvAgents.setItemDelegateForColumn(0, CheckBoxDelegate(None))

        self._selected_agent = None

        self.registry = Registry()
        self.registry_model = RegistryModel(self, self.registry)

        self.tvAgents.setModel(self.registry_model)
        self.tvAgents.customContextMenuRequested.connect(self.handle_agents_context_menu_requested)
        self.tvAgents.clicked.connect(self.handle_agent_selected)

        # file menu
        self.actionNew_Scenario.triggered.connect(self.handle_new_scenario)
        self.actionExit.triggered.connect(self._handle_exit)
        self.signals = MainUISignals()

        # populate the TimeOfDay picker
        for time_of_day in TimeOfDay._meta.enum.__members__.values():
            self.cbTimeOfDay.addItem(time_of_day.lower_name)

        self.show()
        # https://stackoverflow.com/questions/35527439/pyqt4-wait-in-thread-for-user-input-from-gui/35534047#35534047
        self._agent_checker_thread = QThread()
        self.agent_checker_worker = AgentCheckerWorker()
        self.agent_checker_worker.moveToThread(self._agent_checker_thread)
        self._agent_checker_thread.started.connect(self.agent_checker_worker.run)

        listener = Listener()
        atexit.register(listener.stop)
        listener.signals.zeroconf_agent_found.connect(self.registry.handle_zeroconf_agent_found)
        listener.signals.zeroconf_agent_found.connect(self.agent_checker_worker.registry.handle_zeroconf_agent_found)
        listener.signals.zeroconf_agent_removed.connect(self.registry.handle_zeroconf_agent_removed)
        listener.signals.zeroconf_agent_removed.connect(self.agent_checker_worker.registry.handle_zeroconf_agent_removed)
        listener.run()

        # our registry
        self.signals.agent_manually_added.connect(self.registry.handle_agent_manually_added)
        self.signals.agent_manually_removed.connect(self.registry.handle_agent_manually_removed)
        # thread's registry
        self.signals.agent_manually_added.connect(self.agent_checker_worker.registry.handle_agent_manually_added)
        self.signals.agent_manually_removed.connect(self.agent_checker_worker.registry.handle_agent_manually_removed)

        self.agent_checker_worker.signals.agents_changed.connect(self.update_agent_view)
        self.agent_checker_worker.signals.agent_info_updated.connect(self.registry.handle_agent_info_updated)

        self._master_candidates = []
        self.agent_checker_worker.signals.master_candidate_add.connect(self.handle_master_candidate_add)
        self.agent_checker_worker.signals.master_candidate_remove.connect(self.handle_master_candidate_remove)
        # connect UI signals and worker signals before starting agent checker thread
        self._agent_checker_thread.start()

        self._state = DirectorState.IDLE
        self.state_machine_timer = QTimer()
        self.state_machine_timer.timeout.connect(self.run_state_machine)
        self.state_machine_timer.start(10000)

        self.registry.signals.registry_updated.connect(self.update_agent_view)
        self.signals.agent_custom_settings_updated.connect(self.registry.handle_agent_custom_settings_updated)

        self._scenario_file_path = None
        self._scenario_changed = False
        self._ai_scenarios = []

        self._selected_master = None
        self._cancel_requested = None
        self._selected_slaves = None

    def _handle_exit(self):
        self._agent_checker_thread.exit()
        QApplication.exit(0)

    def _set_defaults(self):
        # Basics tab
        self.leAircraft.setText('c172p')
        self.cbTimeOfDay.setCurrentIndex(0)
        self.cbMasterAgent.setCurrentIndex(-1)
        self.cbAutoCoordination.setChecked(True)
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

    @pyqtSlot()
    def update_agent_view(self):
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
        host_index = self.registry_model.createIndex(row, 1)
        uuid_index = self.registry_model.createIndex(row, 4)
        self._selected_agent = {
            'host': self.registry_model.data(host_index, Qt.DisplayRole),
            'uuid': self.registry_model.data(uuid_index, Qt.DisplayRole)
        }
        logging.debug(f"self._selected_agent={self._selected_agent}")

    def handle_agents_context_menu_requested(self, position):
        menu = QMenu()
        customise_host_action = menu.addAction("Custom Host Settings")
        menu.addSeparator()
        rescan_environment_action = menu.addAction("Rescan environment")
        rescan_environment_action.setEnabled(False)
        reset_fail_count_action = menu.addAction("Reset fail count")
        reset_fail_count_action.setEnabled(False)
        menu.addSeparator()
        remove_host_action = menu.addAction("Remove Host")

        if not self._selected_agent:
            customise_host_action.setEnabled(False)
            remove_host_action.setEnabled(False)
        else:
            hostname = self._selected_agent['host']

            if self.registry.is_agent_failed(hostname):
                reset_fail_count_action.setEnabled(True)

            if self.registry.is_agent_online(hostname):
                rescan_environment_action.setEnabled(True)

        res = menu.exec_(self.tvAgents.mapToGlobal(position))

        if res == remove_host_action:
            self.signals.agent_manually_removed.emit(
                self._selected_agent.get('host', None),
                self._selected_agent.get('uuid', None)
            )
            self._selected_agent = None
            self.registry_model.updateModel()

        if res == reset_fail_count_action:
            self.registry.reset_failed_count(hostname)
            self.agent_checker_worker.registry.reset_failed_count(hostname)

        if res == rescan_environment_action:
            self.registry.rescan_environment(hostname)

        if res == customise_host_action:
            custom_settings = self.registry.get_custom_settings_for_agent(hostname)

            if custom_settings:
                updated_custom_settings, okPressed = CustomSettingsDialog.getValues(custom_settings)

                if okPressed:
                    self.signals.agent_custom_settings_updated.emit(
                        hostname,
                        updated_custom_settings.to_update_dict()
                    )

        self.update_agent_view()

    @pyqtSlot()
    def on_actionAddHost_triggered(self):
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

    @pyqtSlot(int)
    def on_cbMasterAgent_currentIndexChanged(self, index: int):
        if index == -1:
            self._selected_master = None
            self._set_master_dependent_button_enabled_state(False)
            self.signals.master_deselected.emit()
            self.pbManageAIScenarios.setEnabled(False)
            self.pbLaunch.setEnabled(False)
        else:
            self._selected_master = self.cbMasterAgent.itemText(index)
            logging.info(f"selected master is {self._selected_master}")
            self.pbLaunch.setEnabled(True)
            self.pbManageAIScenarios.setEnabled(True)
            self.signals.master_selected.emit(self._selected_master)


    @pyqtSlot()
    def on_pbManageAIScenarios_clicked(self):
        current_master = self._selected_master
        current_ai_scenarios = self._ai_scenarios or []
        all_ai_scenarios = self.registry.get_ai_scenarios_from_host(current_master)

        selected_scenarios, okPressed = AiScenariosDialog.getValues(all_ai_scenarios, current_ai_scenarios)

        if okPressed:
            self._ai_scenarios = selected_scenarios
    
    @pyqtSlot()
    def on_pbLaunch_click(self):
        master_hostname = self._selected_master

        selected_agents = [agent for agent in self.registry.all_agents if agent.selected]

        # add master to selected_agents if it's not in the collection
        if master_hostname not in [agent.host for agent in selected_agents]:
            selected_agents.append(self.registry.get_agent(master_hostname))
        
        self._selected_hosts = [agent.host for agent in selected_agents]
        self._wait_list = [agent.host for agent in selected_agents]

        self._selected_slaves = [host for host in self._selected_hosts if host != master_hostname]
        self._number_of_stages = 2 + 2 * len(self._selected_slaves)
        # do pre-checks here!
        # status check
        failed = any([agent.status != 'READY' for agent in selected_agents])

        if failed:
            # TODO: message box
            return
        # version check
        versions = set([agent.version for agent in selected_agents])
        if len(versions) > 0:
            # TODO: y/n continue dialog box
            return

        self._state = DirectorState.START_SEQUENCE_REQUESTED
        self._cancel_requested = False
        self.pbStop.setEnabled(True)
        self.pbLaunch.setEnabled(False)
        self.pbManageAIScenarios.setEnabled(False)
        self.rbAirport.setEnabled(False)
        self.leAirport.setEnabled(False)
        self.rbRunway.setEnabled(False)
        self.leRunway.setEnabled(False)


class DirectorRunner():
    def run(self):
        app = QApplication([])
        w = MainWindow()
        app.exec_()
