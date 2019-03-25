import typing

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSlot, QModelIndex

from fgo.ui.AiScenariosDialog import Ui_AiScenarioDialog

class AiScenariosDialog(QDialog):
    def __init__(self, all_scenarios: typing.List[str], selected_scenarios: typing.List[str]):
        super(QDialog, self).__init__()
        self.ui = Ui_AiScenarioDialog()
        self.ui.setupUi(self)
        self.populate_lists(all_scenarios, selected_scenarios)
        self._selected_active_item = None
        self._selected_available_item = None

    def populate_lists(self, all_scenarios: typing.List[str], selected_scenarios: typing.List[str]):
        for item in selected_scenarios:
            self.ui.lwActive.addItem(item)

        not_selected = [x for x in all_scenarios if x not in selected_scenarios]

        for item in not_selected:
            self.ui.lwAvailable.addItem(item)

    @pyqtSlot(QModelIndex)
    def on_lwAvailable_clicked(self, index):
        self._selected_available_item = index.row()
        self.ui.pbAdd.setEnabled(True)

    @pyqtSlot()
    def on_pbAdd_clicked(self):
        index = self._selected_available_item
        item = self.ui.lwAvailable.takeItem(index)
        self.ui.lwActive.addItem(item)
        self._selected_available_item = None
        self.ui.pbAdd.setEnabled(False)

    @pyqtSlot(QModelIndex)
    def on_lwActive_clicked(self, index):
        self._selected_active_item = index.row()
        self.ui.pbRemove.setEnabled(True)

    @pyqtSlot()
    def on_pbRemove_clicked(self):
        index = self._selected_active_item
        item = self.ui.lwActive.takeItem(index)
        self.ui.lwAvailable.addItem(item)
        self._selected_active_item = None
        self.ui.pbRemove.setEnabled(False)

    def _get_selected_scenarios(self) -> typing.List[str]:
        res = []
        for item in [self.ui.lwActive.item(i).text() for i in range(0, self.ui.lwActive.count(), 1)]:
            res.append(item)
        return res

    def exec_(self) -> typing.Union[list, bool]:
        button_res = super(AiScenariosDialog, self).exec_()
        selection = self._get_selected_scenarios()
        return selection, button_res

    @staticmethod
    def getValues(all_scenarios: list, selected_scenarios: list):
        dialog = AiScenariosDialog(all_scenarios, selected_scenarios)
        return dialog.exec_()
