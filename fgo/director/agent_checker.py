import logging
from time import sleep

from PyQt5.QtCore import pyqtSlot, QRunnable, QTimer, QObject

from fgo.director.registry import Registry, RegisteredAgent
from fgo.director.signals import AgentCheckerSignals
from fgo.gql import queries

class AgentCheckerWorker(QObject):
    def __init__(self):
        super(AgentCheckerWorker, self).__init__()
        self.signals = AgentCheckerSignals()
        self.registry = Registry()
        self._running = True
        self._previous_candidate_status = {}
        self._previous_agent_status = {}
        self._ai_scenarios_loaded = []

        logging.debug('done agent checker init')

    @pyqtSlot()
    def run(self):
        self._check_agents()
        self._counter_timer = QTimer()
        self._counter_timer.timeout.connect(self._check_agents)
        self._counter_timer.start(10000)
        logging.debug('started agent checker')

    def _check_agents(self):
        logging.debug('Checking agent status')
        something_changed = False

        for agent in self.registry.get_agents():
            hostname = agent.host
            logging.debug(f"Checking {hostname}")

            if agent.failed:
                logging.debug("Skipping because agent is failed")
                continue

            logging.debug("Agent is not failed")
            client = agent.client()

            agent_is_master_candidate = False
            agent_is_online = None

            this_agent_changed = False

            if client:
                agent_is_online = True
                info_res = client.execute(queries.INFO)
                logging.debug(f"Raw result: {info_res}")

                if agent.info_hash != info_res:
                    #  don't flag this as a `agent_changed` or `something_changed`
                    #  event because we want to ignore timestamp & id
                    this_agent_changed = True
                    agent.info_hash = info_res

                agent_info_status = info_res['info']['status']
                agent_is_master_candidate = agent_info_status == 'READY'

                if agent_is_master_candidate and hostname not in self._ai_scenarios_loaded:
                    logging.info(f"Asking {hostname} for its list of AI Scenarios")
                    ai_scenario_res = client.execute(queries.AI_SCENARIOS)
                    agent.ai_scenarios = [scenario['name'] for scenario in ai_scenario_res['aiScenarios']]
                    self._ai_scenarios_loaded.append(hostname)

                previous_status = self._previous_agent_status.get(hostname, "")

                if agent_info_status != previous_status:
                    this_agent_changed = True
                    self.signals.agent_status_changed.emit(
                        hostname,
                        previous_status,
                        agent_info_status
                    )
                    self._previous_agent_status[hostname] = agent_info_status
            else:
                agent_is_online = False
                agent.status = None

                if agent.failed:
                    # agent is now failed, emit agent just failed message
                    this_agent_changed = True
                    self.signals.agent_failed.emit(hostname)

            # send online / offline message once
            if agent_is_online != agent.online:
                this_agent_changed = True
                if agent_is_online:
                    self.signals.agent_gone_online.emit(hostname)
                else:
                    self.signals.agent_gone_offline.emit(hostname)

                agent.online = agent_is_online

            # send master candidate yes/no message once
            emit_candidate_message = False
            if hostname in self._previous_candidate_status.keys():
                if self._previous_candidate_status[hostname] != agent_is_master_candidate:
                    emit_candidate_message = True
                    self._previous_candidate_status[hostname] = agent_is_master_candidate
            else:
                emit_candidate_message = True
                self._previous_candidate_status[hostname] = agent_is_master_candidate

            if emit_candidate_message:
                this_agent_changed = True
                if agent_is_master_candidate:
                    self.signals.master_candidate_add.emit(hostname)
                else:
                    self.signals.master_candidate_remove.emit(hostname)

            if this_agent_changed:
                self.signals.agent_info_updated.emit(hostname, agent.to_update_dict())

            something_changed = something_changed or this_agent_changed

        if something_changed:
            self.signals.agents_changed.emit()
