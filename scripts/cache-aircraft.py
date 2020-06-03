#! /usr/bin/env python
import ipdb
from datapackage import Package
import pycountry
import pycountry_convert as pc

from yoyo import read_migrations
from yoyo import get_backend
import requests
from bs4 import BeautifulSoup

from pathlib import Path
import sqlite3
import time
import bz2
import sys
import os

database_fn = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '..',
    'fgo',
    'director',
    'data',
    'aircraft.sqlite'
)

database_fn_compressed = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '..',
    'fgo',
    'director',
    'data',
    'aircraft.sqlite.bz2',
)

database_version_fn = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '..',
    'fgo',
    'director',
    'data',
    'aircraft.version',
)

print(f"Using {database_fn}")

if os.path.exists(database_fn):
    print("Deleting existing database")
    os.remove(database_fn)


backend = get_backend('sqlite:///' + database_fn)
migrations = read_migrations('scripts/aircraft-migrations/')

print("Start migrations")
with backend.lock():
    # Apply any outstanding migrations
    backend.apply_migrations(backend.to_apply(migrations))

print("Start caching")
conn = sqlite3.connect(database_fn)

def LoadData(rows, sql, conn):
    for row in rows:
        print(f"Inserting {row}")
        conn.execute(sql, row)
    conn.commit()

# def GetSource(package_uri):
#     source = Package(package_uri)
#     res = None
#     for resource in source.resources:
#         if resource.descriptor['datahub']['type'] == 'derived/csv':
#             res = resource.read()
#             break

#     assert res is not None

#     return res





# def ReloadContinents(conn):
#     '''
#     Intentionally not called, the continents are created as part of the migration
#     '''
#     print("Loading continents")
#     continent_insert_sql = 'INSERT INTO continents VALUES (?, ?)'
#     continent_data = GetSource(
#         'https://datahub.io/core/continent-codes/datapackage.json')
#     LoadData(continent_data, continent_insert_sql, conn)


# print("Loading countries")
# country_insert_sql = 'INSERT INTO countries (code, name, continent_code) VALUES (?, ?, ?)'
# country_data_with_continents = []
# excluded_country_codes = ['TF', 'EH', 'PN', 'SX', 'TL', 'UM', 'VA']

# for country in pycountry.countries:
#     continent_code = ''
#     code = country.alpha_2

#     if code in excluded_country_codes:
#         continue
#     elif country.alpha_2 == 'AQ':
#         continent_code = 'AN'
#     else:
#         continent_code = pc.country_alpha2_to_continent_code(country.alpha_2)

#     country_data_with_continents.append(
#         (
#             country.alpha_2,
#             country.name,
#             continent_code
#         )
#     )

# LoadData(country_data_with_continents, country_insert_sql, conn)

# print('Loading regions')
# region_insert_sql = 'INSERT INTO regions (code, name, country_code) VALUES (?, ?, ?)'

# region_data = []
# for region in pycountry.subdivisions:
#     region_data.append((
#         region.code,
#         region.name,
#         region.country_code
#     ))

# LoadData(region_data, region_insert_sql, conn)

# print('Loading all airports')
# airport_insert_sql = 'INSERT INTO all_airports (code, type, municipality, region_code) VALUES (?, ?, ?, ?)'
# airport_raw_data = GetSource(
#     'https://datahub.io/core/airport-codes/datapackage.json'
# )

# airport_data = []

# for record in airport_raw_data:
#     airport_data.append((
#         record[0],
#         record[1],
#         record[7],
#         record[6]
#     ))

# LoadData(airport_data, airport_insert_sql, conn)

# print("Finding FGFS last committed version")
# history_url = 'https://sourceforge.net/p/flightgear/fgdata/ci/next/log/?path=/Airports/apt.dat.gz'
# page = requests.get(history_url)
# assert page.status_code == 200
# soup = BeautifulSoup(page.text, 'html.parser')
# fgfs_revision = soup.find('a', class_='rev').text.strip('[').strip(']')
# LoadData(
#     [('fgfs_revision', fgfs_revision)],
#     'INSERT INTO meta (key, value) VALUES (?, ?)',
#     conn
# )

# #
# # Now load the FGFS airports
# #
# def GetAirportDetails(code, conn):
#     # returns None or tuple of (airport_code, municipality, region_code, country_code, continent_code)
#     #
#     sql = '''
# SELECT
# 	all_airports.code as airport_code,
#     all_airports.municipality as municipality,
# 	regions.code as region_code,
# 	countries.code as country_code,
# 	continents.code as continent_code
# FROM all_airports
# INNER JOIN regions
# ON all_airports.region_code = regions.code
# INNER JOIN countries
# ON countries.code = regions.country_code
# INNER JOIN continents
# ON continents.code = countries.continent_code
# WHERE all_airports.code = ?;
#     '''
#     return conn.execute(sql, code).fetchone()

# apt_url = 'https://sourceforge.net/p/flightgear/fgdata/ci/next/tree/Airports/apt.dat.gz?format=raw'
# page = requests.get(apt_url)
# assert page.status_code == 200

# page.encoding = 'unicode_escape'  # or `iso-8859-1`
# x = list(page.iter_lines(decode_unicode=True))

# current_airport_code = None
# current_airport_name = None
# current_airport_municipality = ''
# current_airport_region_code = ''
# current_airport_country_code = ''
# current_airport_continent_code = ''

# # list of tuples
# # tuple: (airport_code, airport_name, location, fg_entry_code, lat, lon, municipality, region_code, country_code, continent_code)
# memo = []
# active_count = 0
# skipped_count = 0

# airport_codewords = [
#     '1',  # airports
#     '16',  # heliports
#     '17'  # seabases
# ]

# for line in x:
#     words = line.split()

#     if len(words) < 1:
#         continue

#     if words[0] in airport_codewords:
#         current_airport_code = words[4]
#         current_airport_name = ' '.join(words[5:])

#         print(f"\nFound airport {current_airport_code} {current_airport_name}")
#         details = GetAirportDetails((current_airport_code,), conn)
#         if details is None:
#             current_airport_code = None
#             print("Not active, skipping")
#             skipped_count += 1
#             continue

#         active_count += 1
#         current_airport_municipality = details[1]
#         current_airport_region_code = details[2]
#         current_airport_country_code = details[3]
#         current_airport_continent_code = details[4]
#         print(f"Airport details {details}")

#     if current_airport_code is not None:
#         if words[0] == '100':
#             # found a runway pair
#             fg_entry_code = words[0]
#             location = words[8]
#             lat = words[9]
#             lon = words[10]
#             memo.append((
#                 current_airport_code,
#                 current_airport_name,
#                 location,
#                 fg_entry_code,
#                 lat,
#                 lon,
#                 current_airport_municipality,
#                 current_airport_region_code,
#                 current_airport_country_code,
#                 current_airport_continent_code
#             ))
#             # do the rcp
#             location = words[17]
#             lat = words[18]
#             lon = words[19]
#             memo.append((
#                 current_airport_code,
#                 current_airport_name,
#                 location,
#                 fg_entry_code,
#                 lat,
#                 lon,
#                 current_airport_municipality,
#                 current_airport_region_code,
#                 current_airport_country_code,
#                 current_airport_continent_code
#             ))

#         if words[0] == '101':
#             # found a water runway
#             fg_entry_code = words[0]
#             location = words[3]
#             lat = words[4]
#             lon = words[5]
#             memo.append((
#                 current_airport_code,
#                 current_airport_name,
#                 location,
#                 fg_entry_code,
#                 lat,
#                 lon,
#                 current_airport_municipality,
#                 current_airport_region_code,
#                 current_airport_country_code,
#                 current_airport_continent_code
#             ))
#             # do the rcp
#             location = words[6]
#             lat = words[7]
#             lon = words[8]
#             memo.append((
#                 current_airport_code,
#                 current_airport_name,
#                 location,
#                 fg_entry_code,
#                 lat,
#                 lon,
#                 current_airport_municipality,
#                 current_airport_region_code,
#                 current_airport_country_code,
#                 current_airport_continent_code
#             ))

#         if words[0] == '102':
#             # found a helipad
#             fg_entry_code = words[0]
#             location = words[1]
#             lat = words[2]
#             lon = words[3]
#             memo.append((
#                 current_airport_code,
#                 current_airport_name,
#                 location,
#                 fg_entry_code,
#                 lat,
#                 lon,
#                 current_airport_municipality,
#                 current_airport_region_code,
#                 current_airport_country_code,
#                 current_airport_continent_code
#             ))

# LoadData(
#     memo,
#     'INSERT INTO runways (airport_code, airport_name, location, fg_type_code, lat, lon, municipality, region_code, country_code, continent_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
#     conn
# )

# print(f"Found {active_count} active airports and {skipped_count} inactive airports.")
# print(f"Loaded {len(memo)} runways and helipads")

build_timestamp = int(time.time())

LoadData(
    [('build_timestamp', f'{build_timestamp}')],
    'INSERT INTO meta (key, value) VALUES (?, ?)',
    conn
)
conn.close()

with open(database_version_fn, 'wt') as vh:
    vh.write(f'{build_timestamp}')

before_size=Path(database_fn).stat().st_size

print("Compressing database")

if os.path.exists(database_fn_compressed):
    print("Deleting existing compressed database")
    os.remove(database_fn_compressed)

with bz2.open(database_fn_compressed, "wb") as fw:
    with open(database_fn, "rb") as fr:
        fw.write(fr.read())

after_size=Path(database_fn_compressed).stat().st_size

print(f"Compressed size: {after_size}, uncompressed size: {before_size} ({after_size/before_size}%)")
