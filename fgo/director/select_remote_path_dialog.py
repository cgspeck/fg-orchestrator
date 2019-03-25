import typing
from pathlib import Path

from PyQt5.QtWidgets import QDialog, QListWidgetItem
from PyQt5.QtCore import pyqtSlot, QModelIndex, Qt

from fgo.director.registry import Registry
from fgo.ui.SelectRemotePathDialog import Ui_SelectRemotePathDialog

class SelectRemotePathDialog(QDialog):
    def __init__(self, current_selection: typing.Union[None, str], hostname: str, registry: Registry, select_file=True, allow_none=False):
        super(QDialog, self).__init__()
        self.ui = Ui_SelectRemotePathDialog()
        self.ui.setupUi(self)
        self.setWindowTitle(f"Remote system browser - {hostname}")

        if not allow_none:
            self.ui.pbSelectNone.setEnabled(False)

        self.ui.pbSelect.setEnabled(False)
        self._hostname = hostname

        self._registry = registry
        self._select_file = select_file
        self._result = None

        if current_selection is None or current_selection == "":
            self._pwd = "/"
        else:
            path = Path(current_selection)
            self._pwd = Path(path.parent).as_posix()

        self._fetch_remote_listing(self._pwd)

    @pyqtSlot()
    def on_pbCancel_clicked(self):
        self.reject()

    @pyqtSlot()
    def on_pbSelectNone_clicked(self):
        self._result = None
        self.accept()

    @pyqtSlot()
    def on_pbSelect_clicked(self):
        self.accept()

    @pyqtSlot(QListWidgetItem)
    def on_listWidget_itemDoubleClicked(self, item: QListWidgetItem):
        self.ui.pbSelect.setEnabled(False)
        if item.text().endswith('/'):
            self._fetch_remote_listing(item)

    @pyqtSlot(QListWidgetItem)
    def on_listWidget_itemClicked(self, item: QListWidgetItem):
        if self._select_file and not item.text().endswith('/'):
            self._result = item
            self.ui.pbSelect.setEnabled(True)
        elif not self._select_file and item.text().endswith('/') and not item.text() == '../':
            self._result = item
            self.ui.pbSelect.setEnabled(True)
        else:
            self._result = None
            self.ui.pbSelect.setEnabled(False)

    def _fetch_remote_listing(self, remote_path: typing.Union[str, QListWidgetItem]):
        if remote_path == "":
            next_path = Path("/")
        elif isinstance(remote_path, Path):
            next_path = remote_path
        elif isinstance(remote_path, str):
            next_path = Path(remote_path)
        else:
            # handle list items with data in the form of
            # /FULL/PATH/TO/THINGY/
            # or '../'
            if remote_path.text() == "../":
                next_path = self._pwd.parent
            else:
                # full path stored in itemdata
                next_path = Path(remote_path.data(Qt.UserRole))

        self._pwd = next_path
        directory_list, files_list = self._registry.get_directory_listing_for_agent(
            self._hostname,
            next_path.as_posix()
        )

        self.ui.labelCurrentPath.setText(f"{next_path}")

        self.ui.listWidget.clear()
        if next_path.as_posix() != "/":
            item = QListWidgetItem()
            item.setText('../')
            self.ui.listWidget.addItem(item)

        for dir_entry in directory_list:
            item = QListWidgetItem()
            text_val = Path(dir_entry).name

            if text_val == '':  # handle case where we are dealing with the root
                text_val = dir_entry.replace("\\", "/")

            if not text_val.endswith("/"):
                text_val += "/"

            item.setText(text_val)
            item.setData(Qt.UserRole, dir_entry)
            self.ui.listWidget.addItem(item)

        if files_list is None:
            return
        
        for file_entry in files_list:
            item = QListWidgetItem()
            text_val = Path(file_entry).name
            item.setText(text_val)
            item.setData(Qt.UserRole, file_entry)
            self.ui.listWidget.addItem(item)

    def exec_(self) -> typing.Tuple[typing.Union[str, None], bool]:
        button_res = super(SelectRemotePathDialog, self).exec_()

        if button_res == QDialog.Accepted:
            if self._result is None:
                return True, None

            return True, self._result.data(Qt.UserRole)

        return False, None

    @staticmethod
    def getValue(current_selection: typing.Union[None, str], hostname: str, registry: Registry, select_file=True, allow_none=False):
        dialog = SelectRemotePathDialog(current_selection, hostname, registry=registry, select_file=select_file, allow_none=allow_none)
        return dialog.exec_()
