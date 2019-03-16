import socket
import logging

from time import sleep

from PyQt5.QtCore import QObject, QRunnable
from zeroconf import ServiceInfo, ServiceBrowser, Zeroconf

from fgo.director.signals import Signals

class Listener(QObject):
    def __init__(self):
        super(Listener, self).__init__()
        self.zeroconf = Zeroconf()
        self.signals = Signals()

    def remove_service(self, zeroconf, type, name):
        logging.info("Service %s removed" % (name,))
        self.signals.zeroconf_agent_removed.emit(name)

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        logging.debug("Zeroconf service %s detected, service info: %s" % (name, info))
        if name.startswith('FGO Agent'):
            uuid = info.properties[b'uuid'].decode()
            ip_address = info.properties[b'ipaddress'].decode()
            logging.info(f"It is an FGO Agent with ip address {ip_address} and uuid {uuid}")
            self.signals.zeroconf_agent_found.emit(name, ip_address, str(info.port), uuid)

    def run(self):
        ServiceBrowser(self.zeroconf, "_http._tcp.local.", self)

    def stop(self):
        logging.info('Stopping zeroconf')
        self.zeroconf.close()
