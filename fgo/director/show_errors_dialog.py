import logging
import typing

from PyQt5.QtWidgets import QDialog, QInputDialog, QLineEdit
from PyQt5.QtCore import pyqtSlot, QModelIndex

from fgo.ui.ShowErrorsDialog import Ui_ShowErrorsDialog

class ShowErrorsDialog(QDialog):
    def __init__(self, hostname: str, error_list: typing.List[typing.Dict[str, str]]):
        super(QDialog, self).__init__()
        self.ui = Ui_ShowErrorsDialog()
        self.ui.setupUi(self)
        logging.debug(f"ShowErrorsDialog init with hostname: {hostname}, error_list: {error_list}")
        res = f"Errors on {hostname}:"

        for error_dict in error_list:
            res += "\n\n"
            res += error_dict['code']
            res += "\n"
            res += error_dict['description']
        
        self.ui.pteErrors.setPlainText(res)
