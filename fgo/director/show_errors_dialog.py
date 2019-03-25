import logging
import typing

from PyQt5.QtWidgets import QDialog

from fgo.ui.ShowErrorsDialog import Ui_ShowErrorsDialog

class ShowErrorsDialog(QDialog):
    def __init__(self, hostname: str, errors: typing.List[typing.Dict[str, str]]):
        super(QDialog, self).__init__()
        self.ui = Ui_ShowErrorsDialog()
        self.ui.setupUi(self)
        logging.debug(f"ShowErrorsDialog init with hostname: {hostname}, errors: {errors}")
        res = f"Errors on {hostname}:"

        if isinstance(errors, list):
            for error_dict in errors:
                res += "\n\n"
                res += error_dict['code']

                if error_dict['description'] is not None:
                    res += "\n"
                    res += error_dict['description']
        elif isinstance(errors, str):
            res = errors

        self.ui.pteErrors.setPlainText(res)
