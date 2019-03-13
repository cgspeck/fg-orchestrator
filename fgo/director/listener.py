from PyQt5.QtCore import QObject, pyqtSignal, QRunnable
from zeroconf import ServiceBrowser, Zeroconf

from time import sleep

class ListenerSignals(QObject):
    zeroconf_agent_found = pyqtSignal(str, tuple, name='zeroconfAgentFound')
    zeroconf_agent_removed = pyqtSignal(str, name='zeroconfAgentRemoved')


class ListenerWorker(QRunnable):

    def __init__(self):
        super(ListenerWorker, self).__init__()
        self.signals = ListenerSignals()

    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))
        self.signals.zeroconf_agent_removed.emit(name)

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))
        from ipdb import set_trace; set_trace()
        self.signals.zeroconf_agent_found.emit(name, info)
    
    def run(self):
        zeroconf = Zeroconf()
        browser = ServiceBrowser(zeroconf, "_http._tcp.local.", self)
        try:
            # sleep(1) input("Press enter to exit...\n\n")
            sleep(1)
        finally:
            zeroconf.close()
