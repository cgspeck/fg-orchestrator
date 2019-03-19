from PyQt5.QtCore import QObject, pyqtSignal

class AgentCheckerSignals(QObject):
    agent_info_updated = pyqtSignal(
        str, dict,
        name='agentUpdated',
        arguments=['Hostname / IP of Registered Agent', 'Dictionary of values we want to keep in sync across threads']
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


class RegistryModelSignals(QObject):
    agent_selected_status_changed = pyqtSignal(
        str, bool,
        name='agentSelectedStatusChanged',
        arguments=['IP address or hostname', 'selected']
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

    agent_custom_settings_updated = pyqtSignal(
        str, dict,
        name='agentCustomSettingsUpdated',
        arguments=['IP address or hostname', 'Dictionary of updated custom settings']
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
