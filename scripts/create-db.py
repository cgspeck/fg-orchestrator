#! /usr/bin/env python
import ipdb
from datapackage import Package
import pycountry
import pycountry_convert as pc

from yoyo import read_migrations
from yoyo import get_backend
import requests
from bs4 import BeautifulSoup
import sqlite3
import sys
import os


database_fn = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '..',
    'resources',
    'nav-seed.sqlite'
)

print(f"Using {database_fn}")

backend = get_backend('sqlite:///' + database_fn)
migrations = read_migrations('scripts/migrations/')

print("Start migrations")
with backend.lock():
    # Apply any outstanding migrations
    backend.apply_migrations(backend.to_apply(migrations))

print("Start dataload")
conn = sqlite3.connect(database_fn)


def GetSource(package_uri):
    source = Package(package_uri)
    res = None
    for resource in source.resources:
        if resource.descriptor['datahub']['type'] == 'derived/csv':
            res = resource.read()
            break

    assert res is not None

    return res


def LoadData(rows, sql, conn):
    for row in rows:
        print(f"Inserting {row}")
        conn.execute(sql, row)
    conn.commit()


def ReloadContinents(conn):
    '''
    Intentionally not called, the continents are created as part of the migration
    '''
    print("Loading continents")
    continent_insert_sql = 'INSERT INTO continents VALUES (?, ?)'
    continent_data = GetSource(
        'https://datahub.io/core/continent-codes/datapackage.json')
    LoadData(continent_data, continent_insert_sql, conn)


print("Loading countries")
country_insert_sql = 'INSERT INTO countries (code, name, continent_code) VALUES (?, ?, ?)'
country_data_with_continents = []
excluded_country_codes = ['TF', 'EH', 'PN', 'SX', 'TL', 'UM', 'VA']

for country in pycountry.countries:
    continent_code = ''
    code = country.alpha_2

    if code in excluded_country_codes:
        continue
    elif country.alpha_2 == 'AQ':
        continent_code = 'AN'
    else:
        continent_code = pc.country_alpha2_to_continent_code(country.alpha_2)

    country_data_with_continents.append(
        (
            country.alpha_2,
            country.name,
            continent_code
        )
    )

LoadData(country_data_with_continents, country_insert_sql, conn)

print('Loading regions')
region_insert_sql = 'INSERT INTO regions (code, name, country_code) VALUES (?, ?, ?)'

region_data = []
for region in pycountry.subdivisions:
    region_data.append((
        region.code,
        region.name,
        region.country_code
    ))

LoadData(region_data, region_insert_sql, conn)

print('Loading all airports')
airport_insert_sql = 'INSERT INTO all_airports (code, type, municipality, region_code) VALUES (?, ?, ?, ?)'
airport_raw_data = GetSource(
    'https://datahub.io/core/airport-codes/datapackage.json'
)

airport_data = []

for record in airport_raw_data:
    airport_data.append((
        record[0],
        record[1],
        record[7],
        record[6]
    ))

LoadData(airport_data, airport_insert_sql, conn)

print("Finding FGFS last committed version")
history_url = 'https://sourceforge.net/p/flightgear/fgdata/ci/next/log/?path=/Airports/apt.dat.gz'
page = requests.get(history_url)
assert page.status_code == 200
soup = BeautifulSoup(page.text, 'html.parser')
fgfs_revision = soup.find('a', class_='rev').text.strip('[').strip(']')
LoadData(
    [('fgfs_revision', fgfs_revision)],
    'INSERT INTO meta (key, value) VALUES (?, ?)',
    conn
)
apt_url = 'https://sourceforge.net/p/flightgear/fgdata/ci/next/tree/Airports/apt.dat.gz?format=raw'
page = requests.get(apt_url)
assert page.status_code == 200

for bytes_line in page.iter_lines():
    print(bytes_line)
    # str_line = bytes_line.decode('utf-8')
    str_line = str(bytes_line)
    print(str_line)
    words = str_line.split()
    print(words)
    if len(words) < 6:
        continue

    if words[0] == '1':
        name = words[5:].join(' ')
        print(f"Found airport {words[4]} {name}")
