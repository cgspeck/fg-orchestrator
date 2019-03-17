from PyQt5.QtCore import QObject, pyqtSignal

from fgo.director.registry import RegisteredAgent

class AgentCheckerSignals(QObject):
    agent_info_updated = pyqtSignal(
        RegisteredAgent,
        name='agentInfoUpdated',
        arguments=['Updated Registered Agent']
    )

    agent_gone_online = pyqtSignal(
        str,
        name='agentGoneOnline',
        arguments=['Hostname or IP Address']
    )

    agent_gone_offline = pyqtSignal(
        str,
        name='agentGoneOffline',
        arguments=['Hostname or IP Address']
    )

    agent_gone_ready = pyqtSignal(
        str,
        name='agentGoneReady',
        arguments=['Hostname or IP Address']
    )

    agent_gone_not_ready = pyqtSignal(
        str, str,
        name='agentGoneReady',
        arguments=['Hostname or IP Address', r'Agents state']
    )

    agent_gone_error = pyqtSignal(
        str, list,
        name='agentGoneError',
        arguments=['Hostname or IP Address', 'List of error codes and descriptions']
    )

    stop_checker = pyqtSignal(name='stopChecker', arguments='Signal the checker to stop running')


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
