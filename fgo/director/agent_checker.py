import logging
from time import sleep

from PyQt5.QtCore import pyqtSlot, QRunnable, QTimer, QObject

from fgo.director.registry import Registry, RegisteredAgent

from fgo.director.signals import AgentCheckerSignals

class AgentCheckerWorker(QObject):
    def __init__(self):
        super(AgentCheckerWorker, self).__init__()
        self.signals = AgentCheckerSignals()
        self._registry = Registry()
        self._running = True
        # self.signals.stop_checker.connect(self.handle_stop_checker)
        logging.debug('done agent checker init')
    
    @pyqtSlot()
    def run(self):
        self._counter_timer = QTimer()
        self._counter_timer.timeout.connect(self.check)
        self._counter_timer.start(1000)

    def check(self):
        logging.info('check')
