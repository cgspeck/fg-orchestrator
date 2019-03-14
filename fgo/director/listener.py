import socket
import logging

from time import sleep

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable
from zeroconf import ServiceInfo, ServiceBrowser, Zeroconf

class ListenerSignals(QObject):
    zeroconf_agent_found = pyqtSignal(str, ServiceInfo, name='zeroconfAgentFound')
    zeroconf_agent_removed = pyqtSignal(str, name='zeroconfAgentRemoved')


class Listener(QObject):
    def __init__(self):
        super(Listener, self).__init__()
        self.zeroconf = Zeroconf()
        self.signals = ListenerSignals()

    def remove_service(self, zeroconf, type, name):
        logging.info("Service %s removed" % (name,))
        self.signals.zeroconf_agent_removed.emit(name)

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        logging.info("Service %s added, service info: %s" % (name, info))
        #
        # TODO: resolve info.server into an IP address and pass to signal
        #       this might only be possible on linux?
        #
        #
        # In [37]: socket.gethostbyname('npib2f8cd.local.')
        # Out[37]: '192.168.1.100'
        #
        logging.info(f"Found service at {socket.gethostbyname(info.server)}")
        self.signals.zeroconf_agent_found.emit(name, info)

    def run(self):
        ServiceBrowser(self.zeroconf, "_http._tcp.local.", self)

    def stop(self):
        logging.info('Stopping zeroconf')
        self.zeroconf.close()
