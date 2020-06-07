from datetime import datetime
from pathlib import Path
from enum import Enum, unique
import webbrowser
import typing
import logging
import atexit
import copy
import bz2
import os

import yaml

from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QLineEdit, QMenu, QMessageBox, QLabel, QProgressBar, QFileDialog, QCheckBox
from PyQt5.QtCore import pyqtSlot, Qt, QTimer, QThread, QModelIndex, QPoint, QThreadPool

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
from fgo.director.select_airport_dialog import SelectAirportDialog
from fgo.director.show_errors_dialog import ShowErrorsDialog
from fgo.director.configure_agent_paths_dialog import ConfigureAgentPathsDialog
from fgo.director.parking_cache_updater_worker import ParkingCacheUpdaterWorker
from fgo.director import parking_record
from fgo.director import parking_data
from fgo.director.select_parking_location_dialog import SelectParkingLocationDialog
from fgo.director import aircraft_data
from fgo.director.select_aircraft_dialog import SelectAircraftDialog


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
        self._selected_agent_hostnames = None
        self._selected_master = None
        self._selected_slave_hostnames = None
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
        self._selected_aircraft_directory = None
        self._last_session_path = Path(config.director_dir, 'last_session.yml')

        if self._last_session_path.exists():
            self.load_scenario(self._last_session_path)

        self.controls_enabled = True
        self.parking_cache_loaded = True
        self.parking_cache_threadpool = QThreadPool()

    def load_scenario(self, path: Path):
        memo = yaml.load(path.read_text(), Loader=yaml.UnsafeLoader)
        logging.info(f"Loading {path}")
        scenario_settings = ScenarioSettings.from_dict(memo['scenario'])
        self.cbAircraftVariant.clear()
        self._map_scenario_settings_to_form(scenario_settings)
        self._retrieve_aircraft_variants()
        self.registry.load_dict(memo['agents'])
        self.agent_checker_worker.load_registry_from_save(memo['agents'])
        self.update_agent_view()

    def _retrieve_aircraft_variants(self):
        aircraft_name = self.pbAircraft.text()
        variants = aircraft_data.get_variants(self._config.aircraft_db, aircraft_name)
        current = self.cbAircraftVariant.currentText()
        if current in variants:
            variants.remove(current)

        self.cbAircraftVariant.addItems(variants)

    @pyqtSlot()
    def on_pbAircraft_clicked(self):
        selected_aircraft, selected_aircraft_directory, okPressed = SelectAircraftDialog.getValues(self._config.aircraft_db)
        if okPressed:
            self.pbAircraft.setText(selected_aircraft)
            self._selected_aircraft_directory = selected_aircraft_directory
            self.cbAircraftVariant.clear()
            self._retrieve_aircraft_variants()

    def save_scenario(self, path: Path):
        master_hostname, selected_agent_hostnames, selected_slave_hostnames = self._figure_out_master_and_slaves()
        scenario = self._map_form_to_scenario_settings()
        scenario.master = master_hostname
        scenario.slaves = selected_slave_hostnames
        memo = {'scenario': scenario.to_dict(), 'agents': self.registry.to_dict()}
        memo_yaml = yaml.dump(memo)
        logging.info(f"Writing {path}")
        logging.debug(f"save_scenario: data to save:\n\n {memo}\n\n")
        logging.debug(f"save_scenario: yaml serialisation: {memo_yaml}")
        path.write_text(memo_yaml)

    def _set_defaults(self):
        # Basics tab
        default_aircraft = 'c172p'
        self.pbAircraft.setText(default_aircraft)
        self._selected_aircraft_directory = 'c172p'
        self.cbAircraftVariant.clear()
        self._retrieve_aircraft_variants()
        self.cbTimeOfDay.setCurrentIndex(0)

        if self.cbMasterAgent.count() > 0:
            self.cbMasterAgent.setCurrentIndex(0)
        else:
            self.cbMasterAgent.setCurrentIndex(-1)

        self.cbAutoCoordination.setChecked(True)
        self.rbDefaultAirport.setChecked(True)
        self.leAirport.setText('YMML')
        self.leCarrier.clear()
        self.rbDefaultRunway.setChecked(True)
        self.leRunway.setText('09')
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
    def on_pbSelectAirport_clicked(self):
        selected_airport, selected_runway, okPressed = SelectAirportDialog.getValues(self._config.nav_db)

        if okPressed:
            if selected_airport:
                self.leAirport.setText(selected_airport)

                worker = ParkingCacheUpdaterWorker(selected_airport, self._config.parking_cache_dir)
                worker.signals.parking_cache_ready.connect(self.process_parking_cache)
                self.parking_cache_threadpool.start(worker)

            if selected_runway:
                self.leRunway.setText(selected_runway)
                self.rbAirport.setChecked(True)
                self.rbRunway.setChecked(True)
                self.leParking.setText("")

    def process_parking_cache(self, airport_code: str, records: typing.List[parking_record.ParkingRecord]):
        logging.info(f"Processing {len(records)} parking records for {airport_code}")

        if len(records) > 0:
            parking_data.save_parking_records(
                self._config.nav_db,
                airport_code,
                records
            )

        current_airport_code = self.leAirport.text()
        if current_airport_code == airport_code:
            self.parking_cache_loaded = True

            if self.controls_enabled:
                self.pbSelectParking.setEnabled(True)

    @pyqtSlot()
    def on_pbSelectParking_clicked(self):
        current_airport_code = self.leAirport.text()
        records = parking_data.get_parking_records(self._config.nav_db, current_airport_code)
        logging.info(f"{len(records)} parking records for {current_airport_code}")
        selected_parking, okPressed = SelectParkingLocationDialog.getValues(records)

        if okPressed and selected_parking:
            self.leParking.setText(selected_parking)
            self.rbParking.setChecked(True)

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

            if not file_path.suffix == '.yml':
                file_path = Path(f'{file_name}.yml')

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
        logging.debug("update_agent_view called")
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

    @pyqtSlot(QModelIndex)
    def on_tvAgents_clicked(self, index):
        logging.debug(f"agent selected {index}")
        row = index.row()
        host_index = self.registry_model.createIndex(row, 1)
        uuid_index = self.registry_model.createIndex(row, 4)
        self._selected_agent = {
            'host': self.registry_model.data(host_index, Qt.DisplayRole),
            'uuid': self.registry_model.data(uuid_index, Qt.DisplayRole)
        }
        logging.debug(f"self._selected_agent={self._selected_agent}")

    @pyqtSlot(QModelIndex)
    def on_tvAgents_doubleClicked(self, index):
        self.on_tvAgents_clicked(index)
        self._show_custom_agent_settings(self._selected_agent['host'])
        return

    @pyqtSlot(QPoint)
    def on_tvAgents_customContextMenuRequested(self, position: QPoint):
        menu = QMenu()
        customise_host_action = menu.addAction("Custom Host Settings")
        manage_directories_action = menu.addAction("Manage Directories")
        menu.addSeparator()
        open_webserver_action = menu.addAction("Open Web server")
        open_webserver_action.setEnabled(False)
        open_telnet_action = menu.addAction("Open Telnet")
        open_telnet_action.setEnabled(False)
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
            open_webserver_action.setEnabled(False)
            open_telnet_action.setEnabled(False)
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

            if self.registry.is_web_server_available(hostname) or \
                    (self._state in [DirectorState.WAITING_FOR_SLAVES, DirectorState.IN_SESSION] and hostname == self._selected_master):
                open_webserver_action.setEnabled(True)

            if self.registry.is_telnet_available(hostname):
                open_telnet_action.setEnabled(True)

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
            self._show_custom_agent_settings(hostname)
            return

        if res == show_errors_action:
            ShowErrorsDialog(hostname, self.registry.get_errors_for_agent(hostname)).exec_()

        if res == manage_directories_action:
            original_directories = self.registry.get_directories_for_agent(hostname)
            if original_directories is None:
                return

            updated_directories, ok_pressed = ConfigureAgentPathsDialog.getValues(original_directories, self.registry, hostname)

            if ok_pressed and updated_directories != original_directories:
                logging.info(f'Main.handle_agents_context_menu_requested applying updated directories for {hostname}: {updated_directories}')
                ok, error_str = self.registry.apply_directory_changes_to_agent(hostname, updated_directories)
                self.registry.rescan_environment(hostname)
                if ok:
                    QMessageBox.information(
                        self,
                        "Settings applied",
                        "Agent updated successfully",
                        buttons=QMessageBox.Ok
                    )
                else:
                    ShowErrorsDialog(hostname, error_str).exec_()

        if res == open_telnet_action:
            webbrowser.open(f"telnet://{hostname}:8081")

        if res == open_webserver_action:
            webbrowser.open(f"http://{hostname}:8080")

        self.update_agent_view()

    def _show_custom_agent_settings(self, hostname: str):
        custom_settings = self.registry.get_custom_settings_for_agent(hostname)
        if custom_settings:
            updated_custom_settings, ok_pressed = CustomSettingsDialog.getValues(custom_settings)

            if ok_pressed:
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
            self.pbLaunch.setEnabled(False)
            self.pbManageAIScenarios.setEnabled(False)
            self.pbLaunch.setEnabled(False)
        else:
            self.pbLaunch.setEnabled(True)
            self.pbManageAIScenarios.setEnabled(True)

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
        master_hostname, selected_agent_hostnames, selected_slave_hostnames = self._figure_out_master_and_slaves()

        self._selected_agent_hostnames = copy.copy(selected_agent_hostnames)
        self._wait_list = copy.copy(selected_agent_hostnames)
        self._selected_master = master_hostname
        self._selected_slave_hostnames = selected_slave_hostnames
        # do pre-checks here!
        failed = False
        msg = ''

        if master_hostname == '':
            failed = True
            msg = "Please select a master"
        else:
            # status check
            selected_agents = [agent for agent in self.registry.all_agents if agent.host in selected_agent_hostnames]
            failed = any([agent.status != 'READY' for agent in selected_agents])
            if failed:
                msg = "One or more agents are not ready and we cannot launch a session"

        if failed:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText(msg)
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
        scenario_settings.master = master_hostname
        scenario_settings.slaves = selected_slave_hostnames
        self.registry.scenario_settings = scenario_settings
        self.save_scenario(self._last_session_path)

        self._stage_started_datetime = datetime.now()
        self._status_timer_label.setText(f"{self.STAGE_TIMEOUT}")
        self._start_stage_timeout_watchdog()
        self._stages_passed = 0
        self._status_progress_bar.setValue(0)
        self._cancel_requested = False

        if scenario_settings.skip_aircraft_install or scenario_settings.aircraft in [None, "c172p"]:
            self._stage_count = 1 + len(self._selected_slave_hostnames)
            self._wait_list = [master_hostname]
            self._state = DirectorState.WAITING_FOR_MASTER
            self.registry.start_master()
        else:
            self._stage_count = 2 + 2 * len(self._selected_slave_hostnames)
            self._wait_list = copy.deepcopy(selected_agent_hostnames)
            self._state = DirectorState.INSTALLING_AIRCRAFT
            self.registry.install_aircraft()

        self._status_label.setText(self._state.name)

    def _figure_out_master_and_slaves(self):
        master_hostname = self.cbMasterAgent.currentText()
        logging.info(f"Master is: {master_hostname}")
        selected_agent_hostnames = [agent.host for agent in self.registry.all_agents if agent.selected]
        # add master to selected_agents if it's not in the collection
        if master_hostname not in selected_agent_hostnames:
            selected_agent_hostnames.append(master_hostname)
        logging.info(f"Selected agent hostnames are: {selected_agent_hostnames}")
        selected_slave_hostnames = [hostname for hostname in selected_agent_hostnames if hostname != master_hostname]
        logging.debug(f"Selected slaves are:{selected_slave_hostnames}")
        return master_hostname, selected_agent_hostnames, selected_slave_hostnames

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
                    self.labelPhiLink.setText('<a href="http://%s:8080/">Open Phi Web Interface on %s</a>' % (hostname_, hostname_))
                    if len(self._selected_slave_hostnames) > 0:
                        self._wait_list = copy.deepcopy(self._selected_slave_hostnames)
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
        self.labelPhiLink.clear()
        self.pbLaunch.setEnabled(enabled)
        self.pbAircraft.setEnabled(enabled)
        self.cbAircraftVariant.setEnabled(enabled)
        self.cbTimeOfDay.setEnabled(enabled)
        self.cbMasterAgent.setEnabled(enabled)

        self.rbDefaultAirport.setEnabled(enabled)
        self.rbAirport.setEnabled(enabled)
        self.pbSelectAirport.setEnabled(enabled)
        self.leAirport.setEnabled(enabled)
        self.rbCarrier.setEnabled(enabled)
        self.leCarrier.setEnabled(enabled)

        self.rbDefaultRunway.setEnabled(enabled)
        self.rbRunway.setEnabled(enabled)
        self.leRunway.setEnabled(enabled)
        self.rbParking.setEnabled(enabled)
        self.leParking.setEnabled(enabled)

        self.leTSEndpoint.setEnabled(enabled)
        self.leCeiling.setEnabled(enabled)
        self.cbAutoCoordination.setEnabled(enabled)
        self.leVisibilityMeters.setEnabled(enabled)
        self.pbManageAIScenarios.setEnabled(enabled)

        if not enabled:
            self.pbSelectParking.setEnabled(enabled)
        elif self.parking_cache_loaded:
            self.pbSelectParking.setEnabled(enabled)

        self.controls_enabled = enabled


    def _map_form_to_scenario_settings(self):
        ''' reads form values and returns a Registry.ScenarioSettings object '''
        s = ScenarioSettings()

        s.time_of_day = self.cbTimeOfDay.currentText()
        # s.aircraft = self.pbAircraft.text()

        self._apply_text_input_if_set(self.pbAircraft, s, 'aircraft')
        s.aircraft_directory = self._selected_aircraft_directory
        s.aircraft_variant = self.cbAircraftVariant.currentText()
        # self._apply_text_input_if_set(self.cbAircraftVariant, s, 'aircraft_variant')
        self._apply_text_input_if_set(self.leAirport, s, 'airport')
        self._apply_text_input_if_set(self.leCarrier, s, 'carrier')

        self._apply_text_input_if_set(self.leRunway, s, 'runway')
        self._apply_text_input_if_set(self.leParking, s, 'parking')

        self._apply_text_input_if_set(self.leTSEndpoint, s, 'terra_sync_endpoint')
        self._apply_text_input_if_set(self.leCeiling, s, 'ceiling')
        s.enable_auto_coordination = self.cbAutoCoordination.isChecked()
        s.skip_aircraft_install = self.cbSkipAircraftInstall.isChecked()
        self._apply_integer_input_if_set(self.leVisibilityMeters, s, 'visibility_in_meters')
        s.ai_scenarios = self._ai_scenarios

        selected_airport_option = 0
        if self.rbAirport.isChecked():
            selected_airport_option = 1
        elif self.rbCarrier.isChecked():
            selected_airport_option = 2

        s.selected_airport_option = selected_airport_option

        selected_runway_option = 0
        if self.rbRunway.isChecked():
            selected_runway_option = 1
        elif self.rbParking.isChecked():
            selected_runway_option = 2

        s.selected_runway_option = selected_runway_option

        logging.info(f"Constructed scenario settings {s}")
        return s

    def _map_scenario_settings_to_form(self, scenario_settings: ScenarioSettings):
        ''' Loads given ScenarioSettings into the presently displayed form '''

        idx = self.cbTimeOfDay.findText(scenario_settings.time_of_day, Qt.MatchFixedString)
        self.cbTimeOfDay.setCurrentIndex(idx)

        self._selected_master = scenario_settings.master
        self._set_text_field_safe(self.pbAircraft, scenario_settings.aircraft)

        if scenario_settings.aircraft_directory is None:
            logging.warn("Scenario Settings missing aircraft_directory key!")
            self._selected_aircraft_directory = scenario_settings.aircraft
        else:
            self._selected_aircraft_directory = scenario_settings.aircraft_directory
        # self._set_text_field_safe(self.cbAircraftVariant, scenario_settings.aircraft_variant)

        if scenario_settings.aircraft_variant is not None:
            self.cbAircraftVariant.addItem(scenario_settings.aircraft_variant)
            self.cbAircraftVariant.setCurrentText(scenario_settings.aircraft_variant)

        self._set_text_field_safe(self.leAirport, scenario_settings.airport)
        self._set_text_field_safe(self.leCarrier, scenario_settings.carrier)
        self._set_text_field_safe(self.leRunway, scenario_settings.runway)
        self._set_text_field_safe(self.leParking, scenario_settings.parking)
        self._set_text_field_safe(self.leTSEndpoint, scenario_settings.terra_sync_endpoint)
        self._set_text_field_safe(self.leCeiling, scenario_settings.ceiling)

        self._set_boolean_safe(self.cbAutoCoordination, scenario_settings.enable_auto_coordination)
        self._set_boolean_safe(self.cbSkipAircraftInstall, scenario_settings.skip_aircraft_install)

        if scenario_settings.visibility_in_meters is not None:
            self._set_text_field_safe(self.leVisibilityMeters, f"{scenario_settings.visibility_in_meters}")

        self._ai_scenarios = scenario_settings.ai_scenarios

        selected_airport_option = scenario_settings.selected_airport_option
        if selected_airport_option == 2:
            self.rbCarrier.setChecked(True)
        elif selected_airport_option == 1:
            self.rbAirport.setChecked(True)
        else:
            self.rbDefaultAirport.setChecked(True)

        selected_runway_option = scenario_settings.selected_runway_option
        if selected_runway_option == 2:
            self.rbParking.setChecked(True)
        elif selected_runway_option == 1:
            self.rbRunway.setChecked(True)
        else:
            self.rbDefaultRunway.setChecked(True)

        logging.info(f"Loaded scenario settings {scenario_settings}")

    @staticmethod
    def _set_boolean_safe(widget: QCheckBox, val):
        if val is not None:
            widget.setChecked(val)

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
        DirectorRunner.prepare_nav_db(config.nav_db)
        DirectorRunner.prepare_aircraft_db(config.aircraft_db)
        app = QApplication([])
        _ = MainWindow(config)
        app.exec_()

    @staticmethod
    def prepare_nav_db(dst: str):
        # decompress the db
        src = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'data',
            'nav_db.sqlite.bz2'
        )
        DirectorRunner.decompress_db(src, dst)

    @staticmethod
    def prepare_aircraft_db(dst: str):
        # decompress the db
        src = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'data',
            'aircraft.sqlite.bz2'
        )
        DirectorRunner.decompress_db(src, dst)

    @staticmethod
    def decompress_db(src: str, dst: str):
        if not os.path.exists(dst):
            logging.info(f"Decompressing database from {src} to {dst}")
            with bz2.open(src, "rb") as fr:
                with open(dst, "wb") as fw:
                    fw.write(fr.read())
