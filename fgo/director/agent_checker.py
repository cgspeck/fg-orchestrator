from time import sleep

from PyQt5.QtCore import pyqtSlot, QRunnable

from fgo.director.registry import Registry, RegisteredAgent

from fgo.director.signals import AgentCheckerSignals

class AgentCheckerWorker(QRunnable):
    def __init__(self):
        super(AgentCheckerWorker, self).__init__()
        self.signals = AgentCheckerSignals()
        self._registry = Registry()
        self._running = True
        # TODO: figure why this doesn't work!
        # self.signals.stop_checker.connect(self.handle_stop_checker)
    
    @pyqtSlot()
    def run(self):
        while self._running:
            print('Hello world!')
            sleep(1)
    
    @pyqtSlot()
    def handle_stop_checker(self):
        self._running = False
