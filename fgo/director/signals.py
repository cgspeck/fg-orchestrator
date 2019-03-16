from PyQt5.QtCore import QObject, pyqtSignal

class Signals(QObject):
    zeroconf_agent_found = pyqtSignal(
        str, str, str,
        name='zeroconfAgentFound',
        arguments=['zeroconf name', 'ip address', 'uuid']
    )

    zeroconf_agent_removed = pyqtSignal(
        str,
        name='zeroconfAgentRemoved',
        arguments=['zeroconf name']
    )

    # ip address or hostname
    agent_manually_added = pyqtSignal(str,
        name='agentManuallyAdded',
        arguments=['IP address or hostname']
    )
