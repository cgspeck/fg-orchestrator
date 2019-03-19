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
from fgo.director.signals import RegistrySignals

@dataclass
class CustomAgentSettings:
    # visible
    additional_args: typing.List[str] = field(default_factory=list)
    disable_panel: bool = False
    disable_hud: bool = False
    disable_anti_alias_hud: bool = False
    enable_clouds: bool = False
    enable_clouds3d: bool = False
    enable_fullscreen: bool = True
    enable_terrasync: bool = True
    enable_real_weather_fetch: bool = True
    fov: typing.Union[int, None] = None
    view_offset: typing.Union[int, None] = 0
    # hidden
    role: int = None  # 0 or 1
    master_ip_address: str = None
    client_ip_addresses: typing.List[str] = field(default_factory=list)

    def to_update_dict(self) -> typing.Dict[str, typing.Union[str, list, None]]:
        '''Distill only the properties we want to update into a dict for checker thread'''
        memo = {}
        memo['additional_args'] = self.additional_args
        memo['disable_panel'] = self.disable_panel
        memo['disable_hud'] = self.disable_hud
        memo['disable_anti_alias_hud'] = self.disable_anti_alias_hud
        memo['enable_clouds'] = self.enable_clouds
        memo['enable_clouds3d'] = self.enable_clouds3d
        memo['enable_fullscreen'] = self.enable_fullscreen
        memo['enable_terrasync'] = self.enable_terrasync
        memo['enable_real_weather_fetch'] = self.enable_real_weather_fetch
        memo['fov'] = self.fov
        memo['view_offset'] = self.view_offset
        return memo

    def apply_update_dict(self, update_dictionary: typing.Dict[str, typing.Union[str, list, None]]):
        '''Merge current values with an update message from the checker thread'''
        logging.info(f"CustomAgentSettings applying update dict: {update_dictionary}")
        self.additional_args = update_dictionary['additional_args']
        self.disable_panel = update_dictionary['disable_panel']
        self.disable_hud = update_dictionary['disable_hud']
        self.disable_anti_alias_hud = update_dictionary['disable_anti_alias_hud']
        self.enable_clouds = update_dictionary['enable_clouds']
        self.enable_clouds3d = update_dictionary['enable_clouds3d']
        self.enable_fullscreen = update_dictionary['enable_fullscreen']
        self.enable_terrasync = update_dictionary['enable_terrasync']
        self.enable_real_weather_fetch = update_dictionary['enable_real_weather_fetch']
        self.fov = update_dictionary['fov']
        self.view_offset = update_dictionary['view_offset']

        return self


@dataclass
class RegisteredAgent:
    FAIL_LIMIT = 3

    host: str
    info_hash: dict = field(default_factory=dict)
    port: str = None
    online: bool = False
    uuid: str = None
    zeroconf_name: str = None
    custom_settings: CustomAgentSettings = field(default_factory=CustomAgentSettings)
    fail_count: int = 0
    selected: bool = True
    ai_scenarios: typing.List[str] = field(default_factory=list)

    @property
    def status(self) -> typing.Union[str, None]:
        res = self.info_hash.get('info', {}).get('status')
        logging.debug(f"Status for Registered agent {self.host}: {res}")
        return res

    def _update_info_hash(self, key, value):
        current_info_value = self.info_hash.get('info', { key : None })
        current_info_value[key] = value
        self.info_hash['info'] = current_info_value

    @status.setter
    def status(self, new_status):
        self._update_info_hash('status', new_status)

    @property
    def os(self) -> typing.Union[str, None]:
        return self.info_hash.get('info', {}).get('os')

    @os.setter
    def os(self, new_os):
        self._update_info_hash('os', new_os)

    @property
    def failed(self) -> bool:
        return self.fail_count >= self.FAIL_LIMIT

    @property
    def errors(self) -> typing.Union[list, None]:
        ''' Returns list of errors '''
        res = self.info_hash.get('info', {}).get('errors', None)

        return res

    def rescan_environment(self):
        ''' Ask a client to rescan its environment '''
        client = self.client()

        if client:
            client.execute(queries.RESCAN_ENVIRONMENT)

    @errors.setter
    def errors(self, new_errors):
        self._update_info_hash('errors', new_errors)

    def set_defaults(self):
        self.custom_settings = CustomAgentSettings()

    def to_update_dict(self) -> typing.Dict[str, typing.Union[str, list, None]]:
        '''Distill only the properties we want to update into a dict for checker thread'''
        memo = {}
        memo['status'] = self.status
        memo['fail_count'] = self.fail_count
        memo['online'] = self.online
        memo['uuid'] = self.uuid
        memo['zeroconf_name'] = self.zeroconf_name
        memo['port'] = self.port
        memo['errors'] = self.errors
        memo['os'] = self.os
        memo['ai_scenarios'] = self.ai_scenarios
        return memo

    def apply_update_dict(self, update_dictionary: typing.Dict[str, typing.Union[str, list, None]]):
        '''Merge current values with an update message from the checker thread'''
        logging.debug(f"Applying update dict: {update_dictionary}")
        self.status = update_dictionary['status']
        self.fail_count = update_dictionary['fail_count']
        self.online = update_dictionary['online']
        self.os = update_dictionary['os']
        self.uuid = update_dictionary['uuid']
        self.zeroconf_name = update_dictionary['zeroconf_name']
        self.port = update_dictionary['port']
        self.errors = update_dictionary['errors']
        self.ai_scenarios = update_dictionary['ai_scenarios']
        return self

    def client(self):
        url = f"http://{self.host}:{self.port}/graphql"
        headers = {
            'Accept': 'text/html'
        }

        if self.fail_count == self.FAIL_LIMIT:
            return None

        try:
            request = requests.get(
                url,
                headers=headers
            )
            request.raise_for_status()
        except (ConnectionRefusedError, urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError, requests.exceptions.ConnectionError) as e:
            logging.debug(f"Could not connect to {self.host}:{e}")
            self.fail_count += 1
            return None

        return Client(
            transport=RequestsHTTPTransport(
                url=url,
                headers=headers
            )
        )



class Registry(QObject):
    def __init__(self):
        super(Registry, self).__init__()
        self.signals = RegistrySignals()
        self._alive_agents: typing.Dict[str, RegisteredAgent] = {}
        self._dead_agents: typing.Dict[str, RegisteredAgent] = {}
        self._unknown_agents: typing.List[RegisteredAgent] = []

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
        memo = [agent for agent in self._dead_agents.values() if agent.uuid == uuid]

        if memo:
            memo = memo[0]
            memo.online = True
            logging.debug(f"found agent matches a dead agent")
            self._alive_agents[uuid] = memo
            del self._dead_agents[uuid]
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
