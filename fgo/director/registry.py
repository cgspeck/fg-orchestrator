from dataclasses import dataclass
import logging
import typing

from PyQt5.QtCore import QObject, pyqtSlot
from zeroconf import ServiceInfo, ServiceBrowser, Zeroconf

from fgo.director.signals import Signals

@dataclass
class RegisteredAgent:
    host: str
    port: str = None
    online: bool = False
    uuid: str = None
    zeroconf_name: str = None


class Registry(QObject):
    def __init__(self):
        super(Registry, self).__init__()
        self.signals = Signals()
        self._alive_agents: typing.Dict[str, RegisteredAgent] = {}
        self._dead_agents: typing.Dict[str, RegisteredAgent] = {}
        self._unknown_agents: typing.List[RegisteredAgent] = []

    def get_agents(self) -> typing.List[RegisteredAgent]:
        return list(self._alive_agents.values()) + list(self._dead_agents.values()) + self._unknown_agents
    
    def check_agent_status(self):
        logging.debug('Checking agent status')

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
