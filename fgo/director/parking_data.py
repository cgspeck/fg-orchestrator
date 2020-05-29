import logging
import typing
from pathlib import Path

from PyQt5.QtSql import QSqlDatabase, QSqlQuery

from fgo.director.parking_record import ParkingRecord

def save_parking_records(nav_db: Path, airport_code: str, parking_records: typing.List[ParkingRecord]):
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(str(nav_db))
    assert db.open()

    delete_query = QSqlQuery(db)
    delete_query.prepare('''
    DELETE FROM parking
    WHERE airport_code = ?
    ''')
    delete_query.addBindValue(airport_code)
    delete_query.exec_()
    if delete_query.lastError().type() > 0:
        assert False, delete_query.lastError().text()

    insert_query = QSqlQuery(db)

    for record in parking_records:
        insert_query.prepare('''
            INSERT INTO parking ("airport_code", "index", "type", "name", "number", "airline_codes", "has_airline_codes")
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''')

        insert_query.addBindValue(airport_code)
        insert_query.addBindValue(record.index)
        insert_query.addBindValue(record.parking_type)
        insert_query.addBindValue(record.name)
        insert_query.addBindValue(record.number)
        insert_query.addBindValue(record.airline_codes)
        insert_query.addBindValue(record.has_airline_codes)
        insert_query.exec_()

        if insert_query.lastError().type() > 0:
            logging.error(f"Unable to insert {record}")
            assert False, insert_query.lastError().text()

    db.close()


def get_parking_records(nav_db: Path, airport_code: str) -> typing.List[ParkingRecord]:
    records = []
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(str(nav_db))
    assert db.open()

    select_query = QSqlQuery(db)
    select_query.setForwardOnly(True)
    select_query.prepare('''
        SELECT *
        FROM parking
        WHERE airport_code = ?
        AND has_airline_codes = 0
    ''')

    select_query.addBindValue(airport_code)
    select_query.exec_()
    if select_query.lastError().type() > 0:
        assert False, select_query.lastError().text()

    fieldNo_airport_code = select_query.record().indexOf("airport_code")
    fieldNo_index = select_query.record().indexOf("index")
    fieldNo_parking_type = select_query.record().indexOf("type")
    fieldNo_name = select_query.record().indexOf("name")
    fieldNo_number = select_query.record().indexOf("number")
    fieldNo_airline_codes = select_query.record().indexOf("airline_codes")
    fieldNo_has_airline_codes = select_query.record().indexOf("has_airline_codes")

    while select_query.next():
        airport_code = select_query.value(fieldNo_airport_code)
        index = select_query.value(fieldNo_index)
        parking_type = select_query.value(fieldNo_parking_type)
        name = select_query.value(fieldNo_name)
        number = select_query.value(fieldNo_number)
        airline_codes = select_query.value(fieldNo_airline_codes)
        has_airline_codes = select_query.value(fieldNo_has_airline_codes)

        records.append(
            ParkingRecord(
                airport_code,
                index,
                parking_type,
                name,
                number,
                airline_codes,
                has_airline_codes
            )
        )

    db.close()

    return records
