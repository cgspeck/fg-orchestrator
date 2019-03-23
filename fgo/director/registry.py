from dataclasses import dataclass, field
import logging
import typing
import urllib3

import requests
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from PyQt5.QtCore import QObject, pyqtSlot
from zeroconf import ServiceInfo, ServiceBrowser, Zeroconf

from fgo.director import queries
from fgo.director.registered_agent import RegisteredAgent
from fgo.director.signals import RegistrySignals
from fgo.director.scenario_settings import ScenarioSettings
from fgo.director.custom_agent_settings import CustomAgentSettings


class Registry(QObject):
    def __init__(self):
        super(Registry, self).__init__()
        self.signals = RegistrySignals()
        self._agents: typing.List[RegisteredAgent] = []
        self._scenario_settings: ScenarioSettings = None

    @property
    def scenario_settings(self) -> ScenarioSettings:
        return self._scenario_settings

    @scenario_settings.setter
    def scenario_settings(self, scenario_settings: ScenarioSettings):
        self._scenario_settings = scenario_settings

    def reset_all_custom_agent_settings_to_default(self):
        for agent in self._agents:
            self.reset_custom_agent_settings_to_default(agent)

    def reset_custom_agent_settings_to_default(self, host: typing.Union[RegisteredAgent, str]):
        if isinstance(host, str):
            memo = [ agent for agent in self._agents if agent.host == host ]

            if len(memo) > 0:
                host = memo[0]
            else:
                logging.error(f"Could not find agent to reset: {host}")
                return

        host.set_defaults()

    def get_agents(self) -> typing.List[RegisteredAgent]:
        ''' Return all agents '''
        return self._agents

    def get_agent(self, hostname) -> RegisteredAgent:
        ''' Return agent by hostname or IP address '''
        return [agent for agent in self._agents if agent.host == hostname][0]

    def find_agent_by_host(self, host: str) -> typing.Union[RegisteredAgent, None]:
        '''Returns the requested agent or None if not found'''
        agents = [agent for agent in self._agents if agent.host == host]

        if len(agents) == 0:
            return None

        return agents[0]

    def find_agent_by_uuid(self, uuid: str) -> typing.Union[RegisteredAgent, None]:
        '''Returns the requested agent or None if not found'''
        agents = [agent for agent in self._agents if agent.uuid == uuid]

        if len(agents) == 0:
            return None

        return agents[0]

    def is_agent_failed(self, host: str) -> bool:
        '''Returns True or False indicating if specified agent is in failed state'''
        agent = self.find_agent_by_host(host)

        if agent:
            return agent.failed

        return False

    def is_agent_online(self, host: str) -> bool:
        '''Returns True or False indicating if specified agent is Online'''
        agent = self.find_agent_by_host(host)

        if agent:
            return agent.online

        return False

    def is_agent_running_fgfs(self, host: str) -> bool:
        '''Returns True or False indicating if specified agent is running FGFS'''
        agent = self.find_agent_by_host(host)

        if agent:
            return agent.status == 'FGFS_RUNNING'

        return False

    def reset_failed_count(self, host: str):
        '''Resets the failed count on given agent'''
        agent = self.find_agent_by_host(host)

        if agent:
            agent.fail_count = 0

    def rescan_environment(self, host: str):
        '''Asks the specified host to rescan its environment'''
        self.get_agent(host).rescan_environment()
        self.signals.taint_agent_status.emit(host)

    def agent_has_errors(self, hostname: str) -> bool:
        '''Returns True or False indicating if specified agent has any errors'''
        agent = self.find_agent_by_host(hostname)

        if agent:
            return len(agent.errors) > 0

        return False

    def get_errors_for_agent(self, hostname: str):
        agent = self.find_agent_by_host(hostname)

        if agent:
            return agent.errors

        return []

    @property
    def all_agents(self):
        return self._agents

    @pyqtSlot(str, str, str, str)
    def handle_zeroconf_agent_found(self, zeroconf_name: str, hostname: str, port: str, uuid: str):
        logging.info(f"handle_zeroconf_agent_found with name: {zeroconf_name}, hostname: {hostname}, port: {port}, uuid: {uuid}")

        # search by uuid
        memo = [agent for agent in self._agents if agent.uuid == uuid]

        # search by hostname
        if not memo:
            memo = [agent for agent in self._agents if agent.host == hostname]

        if memo:
            memo = memo[0]
            memo.fail_count = 0
            memo.online = True
            memo.host = hostname
            logging.debug(f"found agent matches a known agent")
            self.signals.registry_updated.emit()
            return

        #  create a new agent
        new_agent = RegisteredAgent(hostname, port=port, uuid=uuid, zeroconf_name=zeroconf_name, online=True)
        self._agents.append(new_agent)
        self.signals.registry_updated.emit()

    @pyqtSlot(str)
    def handle_zeroconf_agent_removed(self, zeroconf_name: str):
        logging.debug(f"handle_zeroconf_agent_removed with name: {zeroconf_name}")
        memo = [agent for agent in self._agents if agent.zeroconf_name == zeroconf_name]

        if memo:
            logging.debug("marking agent as offline")
            memo = memo[0]
            memo.online = False
            self.signals.registry_updated.emit()
        else:
            logging.debug(f"could not locate existing alive agent!")

    @pyqtSlot(str)
    def handle_agent_manually_added(self, hostname: str):
        logging.debug(f"handle_agent_manually_added with hostname: {hostname}")

        frags = hostname.split(':')
        port = '5000'

        if len(frags) == 2:
            hostname = frags[0]
            port = frags[1]
        # only add unique hostnames
        if hostname in [x.host for x in self.get_agents()]:
            logging.debug(f"not adding duplicate hostname")
            return

        self._agents.append(
            RegisteredAgent(
                host=hostname,
                port=port
            )
        )
        self.signals.registry_updated.emit()

    @pyqtSlot(str, str)
    def handle_agent_manually_removed(self, hostname: str, target_uuid: str = None):
        logging.debug(f"handle_agent_manually_removed with hostname: {hostname}, target_uuid: {target_uuid}")
        # search by hostname
        memo = [agent for agent in self._agents if agent.host == hostname]
        if not memo and target_uuid:
            # search by uuid
            memo = [agent for agent in self._agents if agent.uuid == target_uuid]

        if memo:
            self._agents.remove(memo)
            logging.debug(f"Removed agent {memo} from dead list")

        self.signals.registry_updated.emit()

    @pyqtSlot(str, dict)
    def handle_agent_info_updated(self, hostname: str, update_dict: dict):
        '''
        Catch AgentCheckerSignals.agent_updated and apply it against
        the local copy of that agent.
        '''
        logging.debug(f"handle_agent_info_updated called with {hostname}, {update_dict}")
        target = self.find_agent_by_host(hostname)

        if target is None:
            uuid = update_dict['uuid']
            target = self.find_agent_by_uuid(uuid)
        
        if target is None:
            logging.warning(f"handle_agent_info_updated unable to find target with hostname '{hostname}' uuid : {uuid}")
            return

        logging.debug(f"handle_agent_info_updated target is: {target}")
        target.apply_update_dict(update_dict)
        logging.debug(f"handle_agent_info_updated target post update: {target}")
        self.signals.registry_updated.emit()

    @pyqtSlot(str, bool)
    def handle_agent_selected_status_changed(self, hostname, selected):
        target = self.find_agent_by_host(hostname)

        if target:
            logging.debug(f"Registry reports {hostname} selected set to {selected}")
            target.selected = selected

    @pyqtSlot(str)
    def get_custom_settings_for_agent(self, hostname):
        target = self.find_agent_by_host(hostname)

        if target:
            return target.custom_settings

    @pyqtSlot(str, dict)
    def handle_agent_custom_settings_updated(self, hostname: str, update_dict: dict):
        '''
        Catch AgentCheckerSignals.agent_updated and apply it against
        the local copy of that agent.
        '''
        target = self.get_agent(hostname)
        target.custom_settings.apply_update_dict(update_dict)
        # don't send an update message, none of the custom settings are displayed anyway!

    def get_ai_scenarios_from_host(self, hostname):
        target = self.find_agent_by_host(hostname)

        if target:
            return target.ai_scenarios

    def to_dict(self) -> list:
        '''Returns a dictionary containing serialisable agents in dictionary form'''
        return [agent.to_dict() for agent in self._agents]

    def load_dict(self, agents_list: typing.List):
        '''Loads a dictionart containing seralised agents into the registry'''
        self._agents.clear()
        for agent_hash in agents_list:
            self._agents.append(RegisteredAgent.from_dict(agent_hash))

    def install_aircraft(self) -> typing.Tuple[bool, str]:
        '''
        Instruct all selected agents to install aircraft

        Returns:
            - bool: ok
            - str: error message
        '''
        scenario_settings = self.scenario_settings
        aircraft = scenario_settings.aircraft
        all_scenario_selected_hostnames = ([scenario_settings.master] + scenario_settings.slaves)
        target_agents = [agent for agent in self.all_agents if agent.host in all_scenario_selected_hostnames]
        for agent in target_agents:
            logging.info(f"Instructing {agent.host} to install {aircraft}")
            ok, error = agent.install_aircraft(aircraft)

            if not ok:
                msg = f"Error installing aircraft on {agent.host}:{error}"
                return ok, msg

            self.signals.taint_agent_status.emit(agent.host)

        return ok, None

    def start_master(self) -> typing.Tuple[bool, str]:
        '''
        Instruct the master to start up

        Returns:
            - bool: ok
            - str: error message
        '''
        scenario_settings = self.scenario_settings
        master_hostname = scenario_settings.master
        target = self.get_agent(master_hostname)
        logging.info(f"Starting master {master_hostname}")
        ok, error = target.start_fgfs(scenario_settings)

        if ok:
            self.signals.taint_agent_status.emit(master_hostname)

        return ok, error

    def start_slaves(self) -> typing.Tuple[bool, str]:
        '''
        Instruct all slave agents to start up

        Returns:
            - bool: ok
            - str: error message
        '''
        scenario_settings = self.scenario_settings
        slave_hostnames = scenario_settings.slaves
        target_agents = [agent for agent in self._agents if agent.host in slave_hostnames]
        for agent in target_agents:
            logging.info(f"Instructing slave agent {agent.host} to start Flight Gear")
            ok, error = agent.start_fgfs(scenario_settings)

            if not ok:
                msg = f"Error starting FlightGear on {agent.host}:{error}"
                return ok, msg

            self.signals.taint_agent_status.emit(agent.host)

        return ok, None

    def stop_fgfs(self, target_hostname = None):
        stop_hostname_list = []

        if target_hostname:
            stop_hostname_list = [target_hostname]
        else:
            scenario_settings = self.scenario_settings
            stop_hostname_list = ([scenario_settings.master] + scenario_settings.slaves)

        target_agents = [agent for agent in self.all_agents if agent.host in stop_hostname_list]
        for agent in target_agents:
            logging.info(f"Instructing {agent.host} to stop Flight Gear")
            agent.stop_fgfs()

    def set_agent_state(self, hostname, state):
        self.get_agent(hostname).state = state
        self.signals.registry_updated.emit()
