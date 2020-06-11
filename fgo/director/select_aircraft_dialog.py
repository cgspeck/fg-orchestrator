import logging
import typing
from pathlib import Path

from PyQt5.QtWidgets import QDialog, QHeaderView
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
        self.selected_directory = None

    def do_search(self):
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
            status.name as status,
            aircraft.directory as directory
        FROM aircraft
        INNER JOIN status
        ON aircraft.status_id == status.id
        {filterStr}
        ORDER BY aircraft.status_id DESC, aircraft.name ASC;
        '''
        model.setQuery(sql)

        self.ui.tableView.setModel(model)
        header = self.ui.tableView.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.ui.tableView.setColumnHidden(3, True)

    @pyqtSlot()
    def on_pbSearch_clicked(self):
        self.do_search()

    @pyqtSlot(str)
    def on_cbStatus_currentIndexChanged(self, item):
        self.selected_status = item
        self.do_search()

    @pyqtSlot(QModelIndex)
    def on_tableView_clicked(self, index):
        self.selected_aircraft = index.siblingAtColumn(0).data()
        self.selected_directory = index.siblingAtColumn(3).data()
        logging.info(f"aircraft selected {self.selected_aircraft} (directory {self.selected_directory})")

    # returns 'aircraft_name, directory, success'
    def exec_(self) -> typing.Union[str, bool]:
        button_res = super(SelectAircraftDialog, self).exec_()
        logging.info("closing db")
        self.db.close()

        return self.selected_aircraft, self.selected_directory, button_res

    @staticmethod
    def getValues(db_path: Path):
        dialog = SelectAircraftDialog(db_path)
        return dialog.exec_()
