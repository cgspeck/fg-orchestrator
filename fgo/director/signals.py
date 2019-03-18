from PyQt5.QtCore import QObject, pyqtSignal

class AgentCheckerSignals(QObject):
    # TODO: update the RegisteredAgent so that it can be turned into/created from a dict
    #       https://github.com/konradhalas/dacite ?
    # TODO: update the RegisteredAgent to have a handle_agent_updated that updates itself from said dictionary
    # TODO: update the agent checker to send a dictionary representation of the agent
    # TODO: connect this signal from `self.agent_checker_worker` to `self.registry.handle_agent_updated` in MainUI
    agent_updated = pyqtSignal(
        str, dict,
        name='agentUpdated',
        arguments=['Hostname / IP of Registered Agent', 'Dictionary Representation of Info']
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

    agent_status_changed = pyqtSignal(
        str, str, str,
        name='agentStatusChanged',
        arguments=['Hostname or IP Address', 'Previous Status', 'New Status']
    )

    agent_failed = pyqtSignal(
        str,
        name='agentFailed',
        arguments=['Hostname or IP Address']
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

    agents_changed = pyqtSignal(
        name='agentsChanged',
        arguments=['host']
    )


class RegistrySignals(QObject):
    registry_updated = pyqtSignal(
        name='registryUpdated'
    )


class MainUISignals(QObject):
    agent_manually_added = pyqtSignal(str,
        name='agentManuallyAdded',
        arguments=['IP address or hostname']
    )

    agent_manually_removed = pyqtSignal(
        str, str,
        name='agentManuallyRemoved',
        arguments=['IP address or hostname', 'Agent UUID']
    )


class ZeroConfSignals(QObject):
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
