from datetime import datetime
from pathlib import Path
from enum import Enum, unique
import logging
import atexit
import copy

import yaml

from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QLineEdit, QMenu, QMessageBox, QLabel, QProgressBar, QFileDialog
from PyQt5.QtCore import pyqtSlot, Qt, QTimer, QThread

from fgo.config import Config
from fgo.gql.types import TimeOfDay
from fgo.ui.MainWindow import Ui_MainWindow
from fgo.director.registry import Registry
from fgo.director.registry_model import RegistryModel
from fgo.director.listener import Listener
from fgo.director.signals import MainUISignals
from fgo.director.scenario_settings import ScenarioSettings
from fgo.director.agent_checker import AgentCheckerWorker
from fgo.director.checkbox_delegate import CheckBoxDelegate
from fgo.director.custom_settings_dialog import CustomSettingsDialog
from fgo.director.ai_scenarios_dialog import AiScenariosDialog
from fgo.director.show_errors_dialog import ShowErrorsDialog
from fgo.director.configure_agent_paths_dialog import ConfigureAgentPathsDialog

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
    STAGE_TIMEOUT = 300

    def __init__(self, config: Config, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self._config = config

        self.tvAgents.setItemDelegateForColumn(0, CheckBoxDelegate(None))

        self._selected_agent = None

        self.registry = Registry()
        self.registry_model = RegistryModel(self, self.registry)

        self.tvAgents.setModel(self.registry_model)
        self.tvAgents.customContextMenuRequested.connect(self.handle_agents_context_menu_requested)
        self.tvAgents.clicked.connect(self.handle_agent_selected)

        # file menu
        self._current_session_file_path = None
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
        self.agent_checker_worker.signals.agent_status_changed.connect(self.handle_agent_state_changed)
        # connect UI signals and worker signals before starting agent checker thread
        self._agent_checker_thread.start()

        self._state = DirectorState.IDLE

        self.registry.signals.registry_updated.connect(self.update_agent_view)
        self.registry.signals.taint_agent_status.connect(self.agent_checker_worker.handle_taint_agent_status)
        self.signals.agent_custom_settings_updated.connect(self.registry.handle_agent_custom_settings_updated)

        self._ai_scenarios = []

        self._cancel_requested = None
        self._stage_watchdog_timer = None

        # hostnames / strings only
        self._selected_hosts = None
        self._selected_master = None
        self._selected_slaves = None
        self._wait_list = []
        self._stage_started_datetime = None
        self._stage_count = None
        self._stages_passed = None

        # statusbar
        self._status_label = QLabel()
        self._status_progress_bar = QProgressBar()
        self._status_timer_label = QLabel()
        self.statusbar.addPermanentWidget(self._status_label)
        self.statusbar.addPermanentWidget(self._status_progress_bar)
        self.statusbar.addPermanentWidget(self._status_timer_label)
        self._last_session_path = Path(config.director_dir, 'last_session.yml')

        if self._last_session_path.exists():
            self.load_scenario(self._last_session_path)

    def load_scenario(self, path: Path):
        memo = yaml.load(path.read_text())
        logging.info(f"Loading {path}")
        scenario_settings = ScenarioSettings.from_dict(memo['scenario'])
        self._map_scenario_settings_to_form(scenario_settings)
        self.registry.load_dict(memo['agents'])
        self.agent_checker_worker.load_registry_from_save(memo['agents'])
        self.update_agent_view()
    
    def save_scenario(self, path: Path):
        memo = {'scenario': self._map_form_to_scenario_settings().to_dict(), 'agents': self.registry.to_dict()}
        memo_yaml = yaml.dump(memo)
        logging.info(f"Writing {path}")
        logging.debug(f"save_scenario: data to save:\n\n {memo}\n\n")
        logging.debug(f"save_scenario: yaml serialisation: {memo_yaml}")
        path.write_text(memo_yaml)

    def _set_defaults(self):
        # Basics tab
        self.leAircraft.setText('CRJ700-family')
        self.leAircraftVariant.setText('CRJ700')
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

    @pyqtSlot()
    def on_actionNew_Scenario_triggered(self):
        # reset the state
        self._set_defaults()
        self.setWindowTitle("FlightGear Orchestrator")
        self._current_session_file_path = None
        self.actionSave_As.setEnabled(False)
        self.pbLaunch.setEnabled(True)
    
    @pyqtSlot()
    def on_actionSave_As_triggered(self):
        file_name, _filter_type = QFileDialog.getSaveFileName(
            self,
            'Save Scenario',
            str(self._config.director_dir),
            "Scenario Files (*.yml);;All Files (*.*)"
        )
        logging.debug(f"on_actionSave_As_triggered QFileDialog result {file_name}")

        if file_name != "":
            file_path = Path(file_name)
            self._current_session_file_path = file_path
            self.save_scenario(file_path)
            self.setWindowTitle(f"FlightGear Orchestrator {file_path.name}")
            self.actionSave_As.setEnabled(True)
    
    @pyqtSlot()
    def on_actionSave_Scenario_triggered(self):
        if self._current_session_file_path is None:
            return self.on_actionSave_As_triggered()
        
        self.save_scenario(self._current_session_file_path)
        self.statusbar.showMessage("File saved")
    
    @pyqtSlot()
    def on_actionLoad_Secnario_triggered(self):
        file_name, _filter_type = QFileDialog.getOpenFileName(
            self,
            'Load Scenario',
            str(self._config.director_dir),
            "Scenario Files (*.yml);;All Files (*.*)"
        )
        logging.debug(f"on_actionLoad_Secnario_triggered QFileDialog result {file_name}")

        if file_name != "":
            file_path = Path(file_name)
            self._current_session_file_path = file_path
            self.load_scenario(file_path)
            self.setWindowTitle(f"FlightGear Orchestrator {file_path.name}")
            self.actionSave_As.setEnabled(True)


    @pyqtSlot()
    def on_actionExit_triggered(self):
        self._agent_checker_thread.exit()
        QApplication.exit(0)

    @pyqtSlot()
    def update_agent_view(self):
        logging.info("update_agent_view called")
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
        manage_directories_action = menu.addAction("Manage Directories")
        menu.addSeparator()
        rescan_environment_action = menu.addAction("Rescan environment")
        rescan_environment_action.setEnabled(False)
        reset_fail_count_action = menu.addAction("Reset fail count")
        reset_fail_count_action.setEnabled(False)
        show_errors_action = menu.addAction("Show errors")
        show_errors_action.setEnabled(False)
        menu.addSeparator()
        stop_flightgear_action = menu.addAction("Stop Flightgear")
        stop_flightgear_action.setEnabled(False)
        menu.addSeparator()
        remove_host_action = menu.addAction("Remove Host")

        if not self._selected_agent:
            customise_host_action.setEnabled(False)
            manage_directories_action.setEnabled(False)
            remove_host_action.setEnabled(False)
        else:
            hostname = self._selected_agent['host']

            if self.registry.is_agent_failed(hostname):
                reset_fail_count_action.setEnabled(True)

            if self.registry.is_agent_online(hostname):
                rescan_environment_action.setEnabled(True)
                manage_directories_action.setEnabled(True)

            if self.registry.agent_has_errors(hostname):
                show_errors_action.setEnabled(True)

            if self.registry.is_agent_running_fgfs(hostname):
                stop_flightgear_action.setEnabled(True)

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

        if res == stop_flightgear_action:
            self.registry.stop_fgfs(hostname)
            self.registry_model.updateModel()

        if res == rescan_environment_action:
            self.registry.rescan_environment(hostname)

        if res == customise_host_action:
            custom_settings = self.registry.get_custom_settings_for_agent(hostname)

            if custom_settings:
                updated_custom_settings, ok_pressed = CustomSettingsDialog.getValues(custom_settings)

                if ok_pressed:
                    self.signals.agent_custom_settings_updated.emit(
                        hostname,
                        updated_custom_settings.to_update_dict()
                    )

        if res == show_errors_action:
            ShowErrorsDialog(hostname, self.registry.get_errors_for_agent(hostname)).exec_()

        if res == manage_directories_action:
            original_directories = self.registry.get_directories_for_agent(hostname)
            if original_directories is None:
                return

            updated_directories, ok_pressed = ConfigureAgentPathsDialog.getValues(original_directories, self.registry)

            if ok_pressed and updated_directories != original_directories:
                # Update each changed directory in turn
                # Build up and present an errors hash
                # otherwise show a confirmation dialog
                pass


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
            self.pbLaunch.setEnabled(False)
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
    def on_pbLaunch_clicked(self):
        logging.info("Preparing to launch a session")
        master_hostname = self._selected_master
        logging.info(f"Master is: {master_hostname}")
        selected_agents = [agent for agent in self.registry.all_agents if agent.selected]

        # add master to selected_agents if it's not in the collection
        if master_hostname not in [agent.host for agent in selected_agents]:
            selected_agents.append(self.registry.get_agent(master_hostname))

        selected_agent_hostnames = [agent.host for agent in selected_agents]
        logging.info(f"Selected agent hostnames are: {selected_agent_hostnames}")
        logging.debug(f"Contents of agent list:{selected_agents}")

        self._selected_hosts = copy.copy(selected_agent_hostnames)
        self._wait_list = copy.copy(selected_agent_hostnames)
        self._selected_slaves = [host for host in self._selected_hosts if host != master_hostname]
        # do pre-checks here!
        # status check
        failed = any([agent.status != 'READY' for agent in selected_agents])

        if failed:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText("One or more agents are not ready and we cannot launch a session")
            msg_box.setWindowTitle("Agents not ready")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setDefaultButton(QMessageBox.Ok)
            msg_box.setEscapeButton(QMessageBox.Ok)
            msg_box.exec_()
            return
        # version mismatch check
        versions = set([agent.version for agent in selected_agents])
        if len(versions) > 1:
            # yes/no continue dialog box
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setText("A mix of different versions of FlightGear was detected. Continuing may lead to unexpected behaviour.\n\nAre you sure you wish to continue?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.Yes)
            msg_box.setEscapeButton(QMessageBox.No)
            msg_box.setWindowTitle("Conflicting FlightGear versions")
            res = msg_box.exec_()

            if res == QMessageBox.No:
                logging.info('User abort at version notification')
                return

        logging.info('Preparing UI for launch')
        self._state = DirectorState.START_SEQUENCE_REQUESTED
        self._cancel_requested = False
        self.pbStop.setEnabled(True)
        self._lock_scenario_controls()

        logging.info('Constructing a scenario settings object')

        scenario_settings = self._map_form_to_scenario_settings()
        self.registry.scenario_settings = scenario_settings
        self.save_scenario(self._last_session_path)

        self._stage_started_datetime = datetime.now()
        self._status_timer_label.setText(f"{self.STAGE_TIMEOUT}")
        self._start_stage_timeout_watchdog()
        self._stages_passed = 0
        self._status_progress_bar.setValue(0)
        self._cancel_requested = False

        if scenario_settings.aircraft not in [None, "c172p"]:
            self._stage_count = 2 + 2 * len(self._selected_slaves)
            self._wait_list = copy.deepcopy(selected_agent_hostnames)
            self._state = DirectorState.INSTALLING_AIRCRAFT
            self.registry.install_aircraft()
        else:
            self._stage_count = 1 + len(self._selected_slaves)
            self._wait_list = [master_hostname]
            self._state = DirectorState.WAITING_FOR_MASTER
            self.registry.start_master()

        self._status_label.setText(self._state.name)

    def _start_stage_timeout_watchdog(self):
        if self._stage_watchdog_timer is not None:
            self._stage_watchdog_timer.stop()

        self._stage_watchdog_timer = QTimer()
        self._stage_watchdog_timer.timeout.connect(self._check_stage_timeout)
        self._stage_watchdog_timer.start(1000)

    def _check_stage_timeout(self):
        seconds_run = (datetime.now() - self._stage_started_datetime).seconds
        seconds_remaining = self.STAGE_TIMEOUT - seconds_run
        if seconds_remaining <= 0:
            seconds_remaining = 0
            self.on_pbStop_clicked()
            QMessageBox.critical(
                self,
                "Timeout",
                "One or more agents timed out while launching a session",
                buttons=QMessageBox.Close
            )

        self._status_timer_label.setText(f"{seconds_remaining}")

    @pyqtSlot()
    def on_pbStop_clicked(self):
        self._cancel_requested = True
        self.pbStop.setEnabled(False)
        if self._stage_watchdog_timer is not None:
            self._stage_watchdog_timer.stop()

        current_state = self._state

        if current_state in [
            DirectorState.IN_SESSION,
            DirectorState.WAITING_FOR_SLAVES,
            DirectorState.WAITING_FOR_MASTER
            ]:
            self.registry.stop_fgfs()

        self._state = DirectorState.IDLE
        self._status_label.setText(self._state.name)
        self._unlock_scenario_controls()

    def handle_agent_state_changed(self, hostname, agent_previous_state, agent_next_state):
        logging.info(f"handle_agent_state_changed {hostname}, next: {agent_next_state}, prev: {agent_previous_state}")
        self.registry.set_agent_state(hostname, agent_next_state)

        if self._cancel_requested:
            return

        current_state = self._state

        def state_transition(prev, next_):
            logging.debug(f"handle_agent_state_changed.state_transition prev: {prev}, next: {next_}")
            logging.debug(f"first test: {(agent_previous_state in prev or agent_previous_state == 'PENDING')}")
            logging.debug(f"second test {next_ == agent_next_state}")
            return (agent_previous_state in prev or agent_previous_state == 'PENDING') and next_ == agent_next_state

        def advance_stage(hostname_):
            logging.debug(f"handle_agent_state_changed.advance_stage hostname: {hostname_}")
            self._stages_passed += 1
            self._wait_list.remove(hostname_)
            self._status_progress_bar.setValue(int((self._stages_passed / self._stage_count) * 100))
            next_state = copy.copy(self._state)

            if len(self._wait_list) == 0:
                logging.debug(f"handle_agent_state_changed.advance_stage wait list drained")
                self._stage_started_datetime = datetime.now()
                self._status_timer_label.setText(f"{self.STAGE_TIMEOUT}")
                if current_state == DirectorState.INSTALLING_AIRCRAFT:
                    self._wait_list = [self._selected_master]
                    self.registry.start_master()
                    next_state = DirectorState.WAITING_FOR_MASTER

                if current_state == DirectorState.WAITING_FOR_MASTER:
                    if len(self._selected_slaves) > 0:
                        self._wait_list = copy.deepcopy(self._selected_slaves)
                        self.registry.start_slaves()
                        next_state = DirectorState.WAITING_FOR_SLAVES
                    else:
                        next_state = DirectorState.IN_SESSION
                        if self._stage_watchdog_timer is not None:
                            self._stage_watchdog_timer.stop()
                        self._status_progress_bar.setValue(100)

                if current_state == DirectorState.WAITING_FOR_SLAVES:
                    self._stage_watchdog_timer.stop()
                    next_state = DirectorState.IN_SESSION
                    self._status_progress_bar.setValue(100)

                self._status_label.setText(next_state.name)
                self._state = next_state

        if hostname in self._wait_list:
            if agent_next_state == 'ERROR':
                QMessageBox.critical(
                    self,
                    "Agent state transition error",
                    f"The agent {hostname} entered error state while {current_state.name.lower()}.\n\nPlease check its errors, rescan the environment, modify your settings and try again",
                    QMessageBox.Close
                )
                self._stage_watchdog_timer.stop()
                agent_next_state = DirectorState.IDLE
                self._status_progress_bar.setValue(0)
                self.on_pbStop_clicked()

            if current_state == DirectorState.INSTALLING_AIRCRAFT and state_transition(['INSTALLING_AIRCRAFT', 'PENDING'], 'READY'):
                advance_stage(hostname)
            if current_state == DirectorState.WAITING_FOR_MASTER and state_transition(['FGFS_START_REQUESTED', 'FGFS_STARTING', 'PENDING'], 'FGFS_RUNNING'):
                advance_stage(hostname)
            if current_state == DirectorState.WAITING_FOR_SLAVES and state_transition(['FGFS_START_REQUESTED', 'FGFS_STARTING', 'PENDING'], 'FGFS_RUNNING'):
                advance_stage(hostname)

    def _lock_scenario_controls(self):
        self._set_scenario_controls_enabled_state(False)

    def _unlock_scenario_controls(self):
        self._set_scenario_controls_enabled_state(True)

    def _set_scenario_controls_enabled_state(self, enabled: bool):
        self.pbLaunch.setEnabled(enabled)

        self.leAircraft.setEnabled(enabled)
        self.leAircraftVariant.setEnabled(enabled)
        self.cbTimeOfDay.setEnabled(enabled)
        self.cbMasterAgent.setEnabled(enabled)

        self.rbAirport.setEnabled(enabled)
        self.leAirport.setEnabled(enabled)
        self.rbCarrier.setEnabled(enabled)
        self.leCarrier.setEnabled(enabled)

        self.rbRunway.setEnabled(enabled)
        self.leRunway.setEnabled(enabled)
        self.rbParking.setEnabled(enabled)
        self.leParking.setEnabled(enabled)

        self.leTSEndpoint.setEnabled(enabled)
        self.leCeiling.setEnabled(enabled)
        self.cbAutoCoordination.setEnabled(enabled)
        self.leVisibilityMeters.setEnabled(enabled)
        self.pbManageAIScenarios.setEnabled(enabled)

    def _map_form_to_scenario_settings(self):
        ''' reads form values and returns a Registry.ScenarioSettings object '''
        s = ScenarioSettings()

        s.time_of_day = self.cbTimeOfDay.currentText()
        s.master = self._selected_master
        self._apply_text_input_if_set(self.leAircraft, s, 'aircraft')
        self._apply_text_input_if_set(self.leAircraftVariant, s, 'aircraft_variant')
        self._apply_text_input_if_set(self.leAirport, s, 'airport')
        self._apply_text_input_if_set(self.leCarrier, s, 'carrier')

        self._apply_text_input_if_set(self.leRunway, s, 'runway')
        self._apply_text_input_if_set(self.leParking, s, 'parking')

        self._apply_text_input_if_set(self.leTSEndpoint, s, 'terra_sync_endpoint')
        self._apply_text_input_if_set(self.leCeiling, s, 'ceiling')
        s.enable_auto_coordination = self.cbAutoCoordination.isChecked()
        self._apply_integer_input_if_set(self.leVisibilityMeters, s, 'visibility_in_meters')
        s.ai_scenarios = self._ai_scenarios
        logging.info(f"Constructed scenario settings {s}")
        return s

    def _map_scenario_settings_to_form(self, scenario_settings: ScenarioSettings):
        ''' Loads given ScenarioSettings into the presently displayed form '''

        idx = self.cbTimeOfDay.findText(scenario_settings.time_of_day, Qt.MatchFixedString)
        self.cbTimeOfDay.setCurrentIndex(idx)

        self._selected_master = scenario_settings.master
        self._set_text_field_safe(self.leAircraft, scenario_settings.aircraft)
        self._set_text_field_safe(self.leAircraftVariant, scenario_settings.aircraft_variant)
        self._set_text_field_safe(self.leAirport, scenario_settings.airport)
        self._set_text_field_safe(self.leCarrier, scenario_settings.carrier)
        self._set_text_field_safe(self.leRunway, scenario_settings.runway)
        self._set_text_field_safe(self.leParking, scenario_settings.parking)
        self._set_text_field_safe(self.leTSEndpoint, scenario_settings.terra_sync_endpoint)
        self._set_text_field_safe(self.leCeiling, scenario_settings.ceiling)

        if scenario_settings.enable_auto_coordination:
            self.cbAutoCoordination.setChecked(True)
        else:
            self.cbAutoCoordination.setChecked(False)

        self._set_text_field_safe(self.leVisibilityMeters, f"{scenario_settings.visibility_in_meters}")
        self._ai_scenarios = scenario_settings.ai_scenarios
        logging.info(f"Loaded scenario settings {scenario_settings}")

    @staticmethod
    def _set_text_field_safe(widget: QLineEdit, val, fallback=""):
        if val is None:
            val = fallback
        widget.setText(val)

    @staticmethod
    def _apply_text_input_if_set(widget: QLineEdit, s: ScenarioSettings, prop: str):
        val = widget.text().strip()
        if val != "":
            setattr(s, prop, val)

    @staticmethod
    def _apply_integer_input_if_set(widget: QLineEdit, s: ScenarioSettings, prop: str):
        val = widget.text().strip()
        logging.debug(f"_apply_integer_input_if_set widget: {widget}, \ns: {s}, \nprop: {prop}\nval: {val}")
        if val is not None and val != "":
            try:
                setattr(s, prop, int(val))
            except ValueError as _:
                pass


class DirectorRunner():
    @staticmethod
    def run(config):
        app = QApplication([])
        _ = MainWindow(config)
        app.exec_()
