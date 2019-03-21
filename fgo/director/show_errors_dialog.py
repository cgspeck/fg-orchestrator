import typing

from PyQt5.QtWidgets import QDialog, QInputDialog, QLineEdit
from PyQt5.QtCore import pyqtSlot, QModelIndex

from fgo.ui.ShowErrorsDialog import Ui_ShowErrorsDialog

class ShowErrorsDialog(QDialog):
    def __init__(self, hostname: str, error_list: typing.List[typing.Dict[str, str]]):
        super(QDialog, self).__init__()
        self.ui = Ui_ShowErrorsDialog()
        self.ui.setupUi(self)
        res = f"Errors on {hostname}:"

        for code, description in error_list:
            res += "\n"
            res += code
            res += description
        
        self.ui.pteErrors.setPlainText(res)

    # @staticmethod
    # def showErrors(hostname: str, error_list: typing.List[typing.Dict[str, str]]):
    #     ShowErrorsDialog(hostname, error_list).exec_()
