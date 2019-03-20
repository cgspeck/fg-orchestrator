from dataclasses import dataclass, field
import logging
import typing
import urllib3

import requests
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from PyQt5.QtCore import QObject, pyqtSlot
from zeroconf import ServiceInfo, ServiceBrowser, Zeroconf

from fgo.gql import queries
from fgo.director.registered_agent import RegisteredAgent
from fgo.director.signals import RegistrySignals
from fgo.director.scenario_settings import ScenarioSettings
from fgo.director.custom_agent_settings import CustomAgentSettings


class Registry(QObject):
    def __init__(self):
        super(Registry, self).__init__()
        self.signals = RegistrySignals()
        self._alive_agents: typing.Dict[str, RegisteredAgent] = {}
        self._dead_agents: typing.Dict[str, RegisteredAgent] = {}
        self._unknown_agents: typing.List[RegisteredAgent] = []
        self._scenario_settings: ScenarioSettings = None
    
    @property
    def scenario_settings(self) -> ScenarioSettings:
        return self._scenario_settings
    
    @scenario_settings.setter
    def scenario_settings(self, scenario_settings: ScenarioSettings):
        self._scenario_settings = scenario_settings

    def reset_all_custom_agent_settings_to_default(self):
        for agent in self.known_agents.values():
            self.reset_custom_agent_settings_to_default(agent)

    def reset_custom_agent_settings_to_default(self, host: typing.Union[RegisteredAgent, str]):
        if isinstance(host, str):
            memo = [ agent for agent in self.known_agents.values() if agent.host == host ]

            if len(memo) > 0:
                host = memo[0]
            else:
                logging.error(f"Could not find agent to reset: {host}")
                return

        host.set_defaults()

    def get_agents(self) -> typing.List[RegisteredAgent]:
        ''' Return all agents '''
        return list(self._alive_agents.values()) + list(self._dead_agents.values()) + self._unknown_agents

    def get_agent(self, hostname) -> RegisteredAgent:
        ''' Return agent by hostname or IP address '''
        return [agent for agent in self.get_agents() if agent.host == hostname][0]

    def find_agent_by_host(self, host: str) -> typing.Union[RegisteredAgent, None]:
        '''Returns the requested agent or None if not found'''
        agents = [agent for agent in self.all_agents if agent.host == host]

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

    def reset_failed_count(self, host: str):
        '''Resets the failed count on given agent'''
        agent = self.find_agent_by_host(host)

        if agent:
            agent.fail_count = 0

    def rescan_environment(self, host: str):
        '''Asks the specified host to rescan its environment'''
        self.get_agent(host).rescan_environment()

    @property
    def all_agents(self):
        return self.get_agents()

    @property
    def known_agents(self) -> typing.Dict[str, RegisteredAgent]:
        '''Returns a dictionary of combined alive and dead agents'''
        return {**self._alive_agents, **self._dead_agents}

    @pyqtSlot(str, str, str, str)
    def handle_zeroconf_agent_found(self, zeroconf_name: str, host: str, port: str, uuid: str):
        logging.info(f"handle_zeroconf_agent_found with name: {zeroconf_name}, host: {host}, port: {port}, uuid: {uuid}")

        # search by uuid, check if we have an existing dead agent, if so move it to the alive collection
        memo = [agent for agent in self.known_agents.values() if agent.uuid == uuid]

        if memo:
            memo = memo[0]
            memo.online = True
            memo.host = host
            logging.debug(f"found agent matches a known agent")
            self._alive_agents[uuid] = memo
            self._dead_agents.pop(uuid)
            self.signals.registry_updated.emit()
            return

        # no uuid match, create a new agent
        new_agent = RegisteredAgent(host, port=port, uuid=uuid, zeroconf_name=zeroconf_name, online=True)
        self._alive_agents[uuid] = new_agent

        # check that we have a manually added agent with the same host name
        # TODO: make this a fuzzier test
        memo = [agent for agent in self._unknown_agents if agent.host == host]
        if memo:
            logging.debug(f"found agent matches an unknown agent")
            self._unknown_agents.remove(memo[0])
        self.signals.registry_updated.emit()

    @pyqtSlot(str)
    def handle_zeroconf_agent_removed(self, zeroconf_name: str):
        logging.debug(f"handle_zeroconf_agent_removed with name: {zeroconf_name}")
        memo = [agent for agent in self._alive_agents.values() if agent.zeroconf_name == zeroconf_name]

        if memo:
            logging.debug("moving agent to the dead list")
            memo = memo[0]
            memo.online = False
            uuid = memo.uuid
            self._dead_agents[uuid] = memo
            del self._alive_agents[uuid]
            self.signals.registry_updated.emit()
        else:
            logging.debug(f"could not locate existing alive agent!")

    @pyqtSlot(str)
    def handle_agent_manually_added(self, host: str):
        logging.debug(f"handle_agent_manually_added with host: {host}")

        frags = host.split(':')
        port = '5000'

        if len(frags) == 2:
            host = frags[0]
            port = frags[1]
        # only add unique hosts
        if host in [x.host for x in self.get_agents()]:
            logging.debug(f"not adding duplicate host")
            return

        self._unknown_agents.append(
            RegisteredAgent(
                host=host,
                port=port
            )
        )
        self.signals.registry_updated.emit()

    @pyqtSlot(str, str)
    def handle_agent_manually_removed(self, host: str, target_uuid: str = None):
        logging.debug(f"handle_agent_manually_removed with host: {host}, target_uuid: {target_uuid}")
        # check unknown list first
        memo = [agent for agent in self._unknown_agents if agent.host == host]
        if memo:
            logging.debug(f"removed host {memo[0]} from unknown list")
            self._unknown_agents.remove(memo[0])

        # check known lists
        if target_uuid:
            if target_uuid in self._dead_agents.keys():
                logging.debug(f"removing agent from dead list")
                del self._dead_agents[target_uuid]
            elif target_uuid in self._alive_agents.keys():
                logging.debug(f"removing agent from alive list")
                del self._alive_agents[target_uuid]

        self.signals.registry_updated.emit()

    @pyqtSlot(str, dict)
    def handle_agent_info_updated(self, hostname: str, update_dict: dict):
        '''
        Catch AgentCheckerSignals.agent_updated and apply it against
        the local copy of that agent.
        '''
        target = self.get_agent(hostname)
        target.apply_update_dict(update_dict)
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
        res = {}
        res['unknown'] = [agent.to_dict() for agent in self._unknown_agents]
        res['known'] = [agent.to_dict() for agent in self.known_agents.values()]
        return res

    def load_dict(self, dictionary):
        '''Loads a dictionart containing seralised agents into the registry'''
        for agent_hash in dictionary['unknown']:
            self._unknown_agents.append(RegisteredAgent.from_dict(agent_hash))

        self._alive_agents: typing.Dict[str, RegisteredAgent] = {}
        self._dead_agents: typing.Dict[str, RegisteredAgent] = {}
        self._unknown_agents: typing.List[RegisteredAgent] = []

        for agent_hash in dictionary['known']:
            uuid = agent_hash['uuid']

            self._alive_agents.pop(uuid, None)
            self._dead_agents.pop(uuid, None)

            self._dead_agents[uuid] = RegisteredAgent.from_dict(agent_hash)    

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
        target_agents = [agent for agent in self.all_agents if agent.host in slave_hostnames]
        for agent in target_agents:
            logging.info(f"Instructing slave agent {agent.host} to start Flight Gear")
            ok, error = agent.start_fgfs(scenario_settings)

            if not ok:
                msg = f"Error starting FlightGear on {agent.host}:{error}"
                return ok, msg
        
        return ok, None

    def stop_fgfs(self):
        for agent in self._get_scenario_selected_agents():
            logging.info(f"Instructing {agent.host} to stop Flight Gear")
            agent.stop_fgfs()
