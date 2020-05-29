import logging
import typing
from pathlib import Path

from PyQt5.QtWidgets import QDialog, QListWidgetItem
from PyQt5.QtCore import pyqtSlot

from fgo.director.parking_record import ParkingRecord
from fgo.ui.SelectParkingLocationDialog import Ui_dlgSelectParkingLocation

class SelectParkingLocationDialog(QDialog):
    def __init__(self, parking_records: typing.List[ParkingRecord]):
        super(QDialog, self).__init__()
        self.ui = Ui_dlgSelectParkingLocation()
        self.ui.setupUi(self)

        for record in parking_records:
            item = QListWidgetItem(record.name)
            self.ui.listWidget.addItem(item)

        self.selected_parking = None

    @pyqtSlot(QListWidgetItem)
    def on_listWidget_itemClicked(self, item):
        self.selected_parking = item.text()
        logging.info(f"parking selected {self.selected_parking}")

    # returns 'parking_name, success'
    def exec_(self) -> typing.Union[str, bool]:
        button_res = super(SelectParkingLocationDialog, self).exec_()
        return self.selected_parking, button_res

    @staticmethod
    def getValues(parking_records: typing.List[ParkingRecord]):
        dialog = SelectParkingLocationDialog(parking_records)
        return dialog.exec_()
