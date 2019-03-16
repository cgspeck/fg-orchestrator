from PyQt5.QtCore import QObject, pyqtSignal

class Signals(QObject):
    agent_manually_added = pyqtSignal(str,
        name='agentManuallyAdded',
        arguments=['IP address or hostname']
    )

    agent_manually_removed = pyqtSignal(
        str, str,
        name='agentManuallyRemoved',
        arguments=['IP address or hostname', 'Agent UUID']
    )

    master_candidate_add = pyqtSignal(
        str,
        name='masterCandidateAdd',
        arguments=['host']
    )

    master_candidate_remove = pyqtSignal(
        str,
        name='masterCandidateRemove',
        arguments=['host']
    )

    zeroconf_agent_found = pyqtSignal(
        str, str, str, str,
        name='zeroconfAgentFound',
        arguments=['zeroconf name', 'ip address', 'port', 'uuid']
    )

    zeroconf_agent_removed = pyqtSignal(
        str,
        name='zeroconfAgentRemoved',
        arguments=['zeroconf name']
    )
