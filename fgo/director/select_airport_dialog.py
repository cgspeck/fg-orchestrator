import logging
import typing
from pathlib import Path

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSlot, QModelIndex, QAbstractItemModel, Qt
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlRelationalTableModel, QSqlRelation, QSqlQueryModel

from fgo.ui.SelectAirportDialog import Ui_SelectAirportDialog

class SelectAirportDialog(QDialog):
    def __init__(self, db_path: Path):
        super(QDialog, self).__init__()
        self.ui = Ui_SelectAirportDialog()
        self.ui.setupUi(self)

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(str(db_path))

        assert self.db.open()

        self.browsed_continent_code = None
        self.browsed_country_code = None
        self.browsed_region_code = None

        self.selected_airport = None
        self.selected_runway = None

        self.first_run = True
        continent_model = QSqlTableModel()
        continent_model.setTable('continents')
        continent_model.setSort(1, Qt.AscendingOrder)
        continent_model.select()
        self.ui.cbContinent.setModel(continent_model)
        self.ui.cbContinent.setModelColumn(1)
        self.first_run = False

    def do_browse(self):
        if self.first_run:
            return

        model = QSqlQueryModel()

        filterStr = ""
        if not self.first_run and self.browsed_continent_code is not None:
            filterStr = f"WHERE countries.continent_code = '{self.browsed_continent_code}'"

            if self.browsed_country_code is not None:
                filterStr = f"{filterStr} AND runways.country_code = '{self.browsed_country_code}'"

                if self.browsed_region_code is not None:
                    filterStr = f"{filterStr} AND runways.region_code = '{self.browsed_region_code}'"

        sql = f'''
        SELECT
            runways.airport_code as airport_code,
            runways.location as location,
            runways.airport_name as airport_name,
            all_airports.municipality as municipality,
            regions.name as region_name,
            countries.name as country_name
        FROM runways
        INNER JOIN all_airports
        ON all_airports.code = runways.airport_code
        INNER JOIN regions
        ON all_airports.region_code = regions.code
        INNER JOIN countries
        ON countries.code = regions.country_code
        INNER JOIN continents
        ON continents.code = countries.continent_code
        {filterStr}
        ORDER BY runways.airport_code, runways.location;
        '''
        model.setQuery(sql)

        self.ui.tableView.setModel(model)

    @pyqtSlot()
    def on_pbSearch_clicked(self):
        search_airport_code = self.ui.leAirportCode.text()
        search_name = self.ui.leName.text()

        model = QSqlQueryModel()

        filterStr = ""

        if search_airport_code != "":
            filterStr = f"runways.airport_code LIKE '%{search_airport_code}%'"

        if search_name != "":
            if len(filterStr) > 0:
                filterStr = f"{filterStr} AND "

            filterStr = f"{filterStr} runways.airport_name LIKE '%{search_name}%'"

        if len(filterStr) > 0:
            filterStr = f"WHERE {filterStr}"

        sql = f'''
        SELECT
            runways.airport_code as airport_code,
            runways.location as location,
            runways.airport_name as airport_name,
            all_airports.municipality as municipality,
            regions.name as region_name,
            countries.name as country_name
        FROM runways
        INNER JOIN all_airports
        ON all_airports.code = runways.airport_code
        INNER JOIN regions
        ON all_airports.region_code = regions.code
        INNER JOIN countries
        ON countries.code = regions.country_code
        INNER JOIN continents
        ON continents.code = countries.continent_code
        {filterStr}
        ORDER BY runways.airport_code, runways.location;
        '''
        model.setQuery(sql)

        self.ui.tableView.setModel(model)


    @pyqtSlot(int)
    def on_cbContinent_currentIndexChanged(self, index):
        continent_code = self.ui.cbContinent.model().record(index).field('code').value()
        logging.info(f"Continent {continent_code} selected")

        country_model = QSqlTableModel()
        country_model.setTable('countries')
        country_model.setSort(1, Qt.AscendingOrder)
        country_model.setFilter(f"continent_code = '{continent_code}'")
        country_model.select()
        self.ui.cbCountry.setModel(country_model)
        self.ui.cbCountry.setModelColumn(1)

        self.browsed_continent_code = continent_code
        self.browsed_country_code = None
        self.browsed_region_code = None

        self.do_browse()

    @pyqtSlot(int)
    def on_cbCountry_currentIndexChanged(self, index):
        country_code = self.ui.cbCountry.model().record(index).field('code').value()
        logging.info(f"Country {country_code} selected")

        region_model = QSqlTableModel()
        region_model.setTable('regions')
        region_model.setSort(1, Qt.AscendingOrder)
        region_model.setFilter(f"country_code = '{country_code}'")
        region_model.select()
        self.ui.cbRegion.setModel(region_model)
        self.ui.cbRegion.setModelColumn(1)
        self.browsed_country_code = country_code
        self.browsed_region_code = None
        self.do_browse()

    @pyqtSlot(int)
    def on_cbRegion_currentIndexChanged(self, index):
        region_code = self.ui.cbRegion.model().record(index).field('code').value()
        logging.info(f"Region {region_code} selected")
        self.browsed_region_code = region_code
        self.do_browse()

    @pyqtSlot(QModelIndex)
    def on_tableView_clicked(self, index):
        self.selected_airport = index.siblingAtColumn(0).data()
        self.selected_runway = index.siblingAtColumn(1).data()
        logging.info(f"runway selected {self.selected_airport} / {self.selected_runway}")

    # returns 'airport_code, runway, success'
    def exec_(self) -> typing.Union[str, str, bool]:
        button_res = super(SelectAirportDialog, self).exec_()
        logging.info("closing db")
        self.db.close()

        return self.selected_airport, self.selected_runway, button_res

    @staticmethod
    def getValues(db_path: Path):
        dialog = SelectAirportDialog(db_path)
        return dialog.exec_()
