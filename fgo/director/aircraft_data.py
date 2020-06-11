import logging
import typing
from pathlib import Path

from PyQt5.QtSql import QSqlDatabase, QSqlQuery

from fgo.director.web_panel_record import WebPanelRecord

def get_variants(aircraft_db: Path, aircraft_name: str) -> typing.List[str]:
    records = []
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(str(aircraft_db))
    assert db.open()

    select_query = QSqlQuery(db)
    select_query.setForwardOnly(True)
    select_query.prepare('''
        SELECT name
        FROM variants
        WHERE aircraft_id = (
            SELECT id FROM aircraft WHERE name = ?
        )
        ORDER BY base DESC, name ASC;
    ''')

    select_query.addBindValue(aircraft_name)
    select_query.exec_()
    if select_query.lastError().type() > 0:
        assert False, select_query.lastError().text()

    fieldNo_name = select_query.record().indexOf("name")

    while select_query.next():
        name = select_query.value(fieldNo_name)
        records.append(name)

    db.close()

    return records


def get_web_panels(aircraft_db: Path, aircraft_name: str) -> typing.List[str]:
    records = []
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(str(aircraft_db))
    assert db.open()

    sql = '''
SELECT name, path
FROM web_panels
WHERE aircraft_id = (
    SELECT id FROM aircraft WHERE name = ?
)
ORDER BY name ASC;
    '''
    select_query = QSqlQuery(db)
    select_query.setForwardOnly(True)
    select_query.prepare(sql)

    select_query.addBindValue(aircraft_name)
    select_query.exec_()
    if select_query.lastError().type() > 0:
        assert False, select_query.lastError().text()

    fieldNo_name = select_query.record().indexOf("name")
    fieldNo_path = select_query.record().indexOf("path")

    while select_query.next():
        name = select_query.value(fieldNo_name)
        file_name = select_query.value(fieldNo_path)
        records.append(WebPanelRecord(name=name, file_name=file_name))

    db.close()

    return records


def do_web_panel_report(aircraft_db: Path) -> typing.List[str]:
    records = []
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(str(aircraft_db))
    assert db.open()

    sql = '''
SELECT
    aircraft.name as name,
    count(*) as count
FROM
    aircraft
INNER JOIN
    web_panels
ON aircraft.id = web_panels.aircraft_id
GROUP BY aircraft.name
ORDER BY aircraft.name
    '''
    select_query = QSqlQuery(db)
    select_query.setForwardOnly(True)
    select_query.prepare(sql)
    select_query.exec_()
    if select_query.lastError().type() > 0:
        assert False, select_query.lastError().text()

    fieldNo_name = select_query.record().indexOf("name")
    fieldNo_count = select_query.record().indexOf("count")

    logging.info("The following aircraft have web panels:")

    while select_query.next():
        name = select_query.value(fieldNo_name)
        count = select_query.value(fieldNo_count)
        logging.info(f"    {name} ({count} panels)")

    logging.info("End of report")

    db.close()
