import logging
import typing
from pathlib import Path

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSlot, QModelIndex, QAbstractItemModel, Qt
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlRelationalTableModel, QSqlRelation, QSqlQueryModel

from fgo.ui.SelectAircraftDialog import Ui_SelectAircraftDialog

class SelectAircraftDialog(QDialog):

    STATUSES = [
        'Advanced Production',
        'Production',
        'Early Production',
        'Beta',
        'Alpha',
        'Development'
    ]

    STATUS_TO_I = {
        'Alpha': 1,
        'Beta': 2,
        'Development': 0,
        'Early Production': 3,
        'Production': 4,
        'Advanced Production': 5,
    }

    def __init__(self, db_path: Path):
        super(QDialog, self).__init__()
        self.ui = Ui_SelectAircraftDialog()
        self.ui.setupUi(self)

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(str(db_path))

        assert self.db.open()
        self.selected_status = self.STATUSES[0]
        self.ui.cbStatus.addItems(self.STATUSES)

        self.selected_aircraft = None

        # self.first_run = True
        # self.first_run = False

    def do_search(self):
        # if self.first_run:
        #     return
        print("do_search")
        model = QSqlQueryModel()

        filterStr = ""

        current_status_int = self.STATUS_TO_I[self.selected_status]

        filterStr = f"WHERE status_id  >= '{current_status_int}'"

        search_text = self.ui.leNameDescription.text().strip()

        if len(search_text) > 0:
            filterStr = f"{filterStr} AND (aircraft.name LIKE '%{search_text}%' OR aircraft.description LIKE '%{search_text}%')"

        sql = f'''
        SELECT
            aircraft.name as name,
            aircraft.description as description,
            status.name as status
        FROM aircraft
        INNER JOIN status
        ON aircraft.status_id == status.id
        {filterStr}
        ORDER BY aircraft.status_id DESC, aircraft.name ASC;
        '''
        print(sql)
        model.setQuery(sql)

        self.ui.tableView.setModel(model)

    @pyqtSlot()
    def on_pbSearch_clicked(self):
        self.do_search()

    @pyqtSlot(str)
    def on_cbStatus_currentIndexChanged(self, item):
        self.selected_status = item
        print('status changed')
        print(self.selected_status)
        self.do_search()

    @pyqtSlot(QModelIndex)
    def on_tableView_clicked(self, index):
        self.selected_aircraft = index.siblingAtColumn(0).data()
        logging.info(f"aircraft selected {self.selected_aircraft}")

    # returns 'aircraft_name, success'
    def exec_(self) -> typing.Union[str, bool]:
        button_res = super(SelectAircraftDialog, self).exec_()
        logging.info("closing db")
        self.db.close()

        return self.selected_aircraft, button_res

    @staticmethod
    def getValues(db_path: Path):
        dialog = SelectAircraftDialog(db_path)
        return dialog.exec_()
