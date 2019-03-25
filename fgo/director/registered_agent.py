from dataclasses import dataclass, field
import logging
import typing
import urllib3

import requests
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from fgo.director import queries
from fgo.director.scenario_settings import ScenarioSettings
from fgo.director.custom_agent_settings import CustomAgentSettings
from fgo.director.agent_directory_settings import AgentDirectorySettings


@dataclass
class RegisteredAgent:
    FAIL_LIMIT = 3

    host: str
    info_hash: dict = field(default_factory=dict)
    status: str = None
    port: str = None
    online: bool = False
    uuid: str = None
    zeroconf_name: str = None
    custom_settings: CustomAgentSettings = field(default_factory=CustomAgentSettings)
    fail_count: int = 0
    selected: bool = True
    ai_scenarios: typing.List[str] = field(default_factory=list)
    version: typing.Union[str, None] = None
    directories: AgentDirectorySettings = None

    def _update_info_hash(self, key, value):
        current_info_value = self.info_hash.get('info', { key : None })
        current_info_value[key] = value
        self.info_hash['info'] = current_info_value

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
    def errors(self) -> typing.List[typing.Dict[str, str]]:
        ''' Returns list of errors '''
        res = self.info_hash.get('info', {}).get('errors', [])

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
        memo['host'] = self.host
        memo['zeroconf_name'] = self.zeroconf_name
        memo['port'] = self.port
        memo['errors'] = self.errors
        memo['os'] = self.os
        memo['ai_scenarios'] = self.ai_scenarios
        memo['version'] = self.version
        memo['directories'] = self.directories
        return memo

    def apply_update_dict(self, update_dictionary: typing.Dict[str, typing.Union[str, list, None]]):
        '''Merge current values with an update message from the checker thread'''
        logging.debug(f"Applying update dict: {update_dictionary}")
        self.status = update_dictionary['status']
        self.fail_count = update_dictionary['fail_count']
        self.online = update_dictionary['online']
        self.os = update_dictionary['os']
        self.uuid = update_dictionary['uuid']
        self.host = update_dictionary['host']
        self.zeroconf_name = update_dictionary['zeroconf_name']
        self.port = update_dictionary['port']
        self.errors = update_dictionary['errors']
        self.ai_scenarios = update_dictionary['ai_scenarios']
        self.version = update_dictionary['version']
        self.directories = update_dictionary['directories']
        return self

    def to_dict(self) -> dict:
        ''' Returns dictionary representation of this agent for saving '''
        res = {}
        res = self.to_update_dict()
        # remove runtime data
        res.pop('fail_count', None)
        res.pop('status', None)
        res.pop('online', None)
        res.pop('errors', None)
        res.pop('ai_scenarios', None)
        res.pop('directories', None)
        # add persistable selection/config not part of update packet
        res['hostname'] = self.host
        res['selected'] = self.selected
        res['custom_settings'] = self.custom_settings.to_update_dict()
        return res

    @staticmethod
    def from_dict(dictionary):
        ''' Instantiates an agent based on a saved dictionary '''
        res = RegisteredAgent(dictionary['hostname'])
        res.selected = dictionary['selected']
        res.uuid = dictionary['uuid']
        res.zeroconf_name = dictionary['zeroconf_name']
        res.port = dictionary['port']
        res.os = dictionary['os']
        res.custom_settings = res.custom_settings.apply_update_dict(dictionary['custom_settings'])
        return res

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

    def install_aircraft(self, aircraft) -> typing.Tuple[bool, str]:
        ''' Instruct this agent to install/update an aircraft'''
        client = self.client()
        res = client.execute(queries.AircraftInstallQuery(aircraft))

        return res['installOrUpdateAircraft']['ok'], res['installOrUpdateAircraft']['error']

    def apply_directory_changes(self, updated_directories: AgentDirectorySettings):
        client = self.client()
        res = client.execute(queries.SetDirectoriesQuery(updated_directories))
        ok = True
        error_str = ""

        if res['flightgear_executable'] is None:
            ok = False
            error_str += "Unable to set flightgear_executable\n"

        if res['fgroot_path'] is None:
            ok = False
            error_str += "Unable to set fgroot_path\n"

        if res['fghome_path'] is None:
            ok = False
            error_str += "Unable to set fghome_path\n"

        if res['terrasync_path'] is None:
            ok = False
            error_str += "Unable to set terrasync_path\n"

        if res['aircraft_path'] is None:
            ok = False
            error_str += "Unable to set aircraft_path\n"

        return ok, error_str

    def fetch_remote_directory_list(self, remote_path):
        """ Ask this agent for a directory listing """
        client = self.client()
        res = client.execute(queries.RemoteDirectoryListingQuery(remote_path))
        return res['directoryList']['directories'], res['directoryList']['files']

    def start_fgfs(self, scenario_settings: ScenarioSettings) -> typing.Tuple[bool, str]:
        '''Instruct FGFS to start up'''
        client = self.client()
        res = client.execute(queries.StartFlightGear(
            self.host,
            scenario_settings,
            self.custom_settings,
        ))
        logging.info(f"start_fgfs hostname {self.host} assembled args {res['startFlightGear']['assembledArgs']}")
        return res['startFlightGear']['ok'], res['startFlightGear']['error']

    def stop_fgfs(self) -> typing.Tuple[bool, str]:
        ''' Instruct this agent to stop FGFS'''
        client = self.client()
        res = client.execute(queries.STOP_FLIGHTGEAR)

        return res['stopFlightGear']['ok'], res['stopFlightGear']['error']
