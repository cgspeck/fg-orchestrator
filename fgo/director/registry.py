from dataclasses import dataclass
import logging
import typing

from PyQt5.QtCore import QObject, pyqtSlot
from zeroconf import ServiceInfo, ServiceBrowser, Zeroconf

from fgo.director.signals import Signals

@dataclass
class RegisteredAgent:
    host: str
    uuid: str = None
    zeroconf_name: str = None

class Registry(QObject):
    def __init__(self):
        super(Registry, self).__init__()
        self.signals = Signals()
        self._alive_agents: typing.Dict[str, RegisteredAgent] = {}
        self._dead_agents: typing.Dict[str, RegisteredAgent] = {}
        self._unknown_agents: typing.List[str] = []

    @pyqtSlot(str, str, str)
    def handle_zeroconf_agent_found(self, zeroconf_name: str, host: str, uuid: str):
        logging.debug(f"handle_zeroconf_agent_found with name: {zeroconf_name}, host: {host}, uuid: {uuid}")
        # check if we have an existing dead agent, if so move it to the alive collection
        memo = [agent for agent in self._dead_agents.values() if agent.uuid == uuid]

        if memo:
            logging.debug(f"found agent matches a dead agent")
            self._alive_agents[uuid] = memo[0]
            del self._dead_agents[uuid]
            return

        new_agent = RegisteredAgent(host, uuid=uuid, zeroconf_name=zeroconf_name)
        self._alive_agents[uuid] = new_agent

        # check that we have a manually added agent with the same host name
        # TODO: make this a fuzzier test
        memo = [agent for agent in self._unknown_agents if agent == host]
        if memo:
            logging.debug(f"found agent matches an unknown agent")
            self._unknown_agents.remove(host)

    @pyqtSlot(str)
    def handle_zeroconf_agent_removed(self, zeroconf_name: str):
        logging.debug(f"handle_zeroconf_agent_removed with name: {zeroconf_name}")
        memo = [agent for agent in self._alive_agents.values() if agent.zeroconf_name == zeroconf_name]

        if memo:
            logging.debug("moving agent to the dead list")
            memo = memo[0]
            uuid = memo.uuid
            self._dead_agents[uuid] = memo
            del self._alive_agents[uuid]
        else:
            logging.debug(f"could not locate existing alive agent!")

    @pyqtSlot(str)
    def handle_agent_manually_added(self, host: str):
        logging.debug(f"handle_agent_manually_added with host: {host}")
        self._unknown_agents.append(host)

    @pyqtSlot(str)
    def handle_agent_manually_removed(self, host: str):
        logging.debug(f"handle_agent_manually_removed with host: {host}")
        # check unknown list first
        if host in self._unknown_agents:
            logging.debug(f"removed host from unknown list")
            self._unknown_agents.remove(host)
            return

        # check known lists
        target_uuid = None
        for uuid, registered_agent in {**self._alive_agents, **self._dead_agents}:
            if registered_agent.host == host:
                target_uuid = uuid

        if target_uuid:
            if target_uuid in self._dead_agents.keys():
                logging.debug(f"found agent in dead list")
                del self._dead_agents[target_uuid]
            elif target_uuid in self._alive_agents.keys():
                logging.debug(f"found agent in dead list")
                del self._alive_agents[target_uuid]
            return

        logging.debug("could not find an agent to remove")

