import logging
import typing
from pathlib import Path

from PyQt5.QtSql import QSqlDatabase, QSqlQuery

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
