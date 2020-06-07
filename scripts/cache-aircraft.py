#! /usr/bin/env python
import ipdb
from datapackage import Package
import pycountry
import pycountry_convert as pc

from yoyo import read_migrations
from yoyo import get_backend
import requests
from bs4 import BeautifulSoup

from collections import defaultdict
from typing import Tuple, List
from pathlib import Path
import sqlite3
import time
import bz2
import sys
import io
import os

search_paths=[
    Path('/home/chris/src/c172p'),
    Path('/run/user/1000/gvfs/smb-share:server=kittycat,share=flightgear/2019.1.1/Aircraft')
]

fg_data_path=Path('/usr/share/games/flightgear')

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
    '''
    Loads a bunch of rows into the database
    '''
    for row in rows:
        print(f"Inserting {row}")
        if not (isinstance(row, list) or isinstance(row, tuple)):
            row = (row, )
        conn.execute(sql, row)
    conn.commit()

def LoadRow(row, sql, conn):
    print(f"Inserting {row}")
    conn.execute(sql, row)
    conn.commit()

def LoadAndRowAndGetId(row, sql, conn) -> int:
    '''
    Loads a single row into the database and returns its ID
    '''
    LoadRow(row, sql, conn)
    return conn.execute('SELECT last_insert_rowid()').fetchone()[0]

def GetAircraftId(aircraft_name, conn)  -> int:
    sql = '''
    SELECT id
    FROM aircraft
    WHERE name = ?
    '''
    return conn.execute(sql, (aircraft_name, )).fetchone()[0]


TAG_UPSERT_SQL = '''
INSERT INTO tags(name, count)
VALUES (?, 1)
ON CONFLICT(name) DO UPDATE SET
    count = count + 1;
'''

AIRCRAFT_INSERT_SQL = '''
INSERT INTO aircraft(name, description, directory, status_id, rating_fdm, rating_systems, rating_model, rating_cockpit)
VALUES (?, ?, ?, ?, ?, ?, ?, ?);
'''

AIRCRAFT_TAG_ASSOCIATE_SQL='''
INSERT INTO aircraft_tags(aircraft_id, tag_id)
SELECT ?, id
FROM tags WHERE name = ?;
'''

VARIANT_INSERT_SQL = '''
INSERT INTO variants(aircraft_id, name, base)
VALUES (?, ?, ?);
'''

STATUS_TO_I = defaultdict(lambda: 0, {
    '0.4.6': 0,
    '1.4.0': 1,
    '1.4.3': 1,
    'Alpha': 1,
    'Alpha development': 0,
    'advanced production': 5,
    'alpha': 1,
    'alpha, "GPL Copyright"': 1,
    'beta': 2,
    'Beta': 2,
    'developement': 0,
    'development': 0,
    'early production': 3,
    'early-production': 3,
    'production': 4,
})
class FileSystemXMLWalker(object):
    FG_DATA_PATH = None

    def __init__(self, search_path: Path, fg_data_path: Path, recurse_depth: int=1):
        super(FileSystemXMLWalker, self).__init__()
        FileSystemXMLWalker.FG_DATA_PATH = fg_data_path
        self.search_path = search_path
        self._found_dirs: List[Path] = None
        self._base_depth = len(search_path.parts)
        self._analysed_depth: int = 0
        self._recurse_depth = recurse_depth
        self._dir_index: int = None

        self._found_xmls: List[Path] = []
        self._xml_index: int = None

    def __iter__(self):
        return self

    def analyse_dirs(self, target_depth: int):
        target_depth = self._base_depth + target_depth

        for found_dir in self._found_dirs:
            if len(found_dir.parts) >= target_depth:
                continue

            for new_dir in found_dir.iterdir():
                if new_dir.is_dir():
                    self._found_dirs.append(new_dir)

        if target_depth > self._analysed_depth:
            self._analysed_depth = target_depth

    def find_xmls_in_dir(self, index):
        wd = self._found_dirs[index]
        self._found_xmls = [Path(wd, r) for r in wd.glob("*set.xml")]

    def __next__(self) -> Tuple[Path, BeautifulSoup]:
        if self._found_dirs is None:
            self._found_dirs = [self.search_path]

            if self._recurse_depth > 0:
                self.analyse_dirs(1)

        if self._dir_index is None:
            self.find_xmls_in_dir(0)
            self._dir_index = 0
            self._xml_index = 0

        xml_index = self._xml_index
        dir_index = self._dir_index

        if self._xml_index is None:
            self.find_xmls_in_dir(dir_index)
            self._xml_index = xml_index = 0

        if (xml_index + 1) > len(self._found_xmls) and (dir_index + 1) == len(self._found_dirs):
            if self._analysed_depth >= self._recurse_depth:
                raise StopIteration()
            else:
                self.analyse_dirs(self._analysed_depth + 1)
                self._xml_index = None
                self._dir_index += 1
                return self.__next__()

        if (xml_index + 1) > len(self._found_xmls):
            self._xml_index = None
            self._dir_index += 1
            return self.__next__()

        v = self._found_xmls[xml_index]
        soup = BeautifulSoup(v.read_bytes(), 'lxml-xml')
        self._xml_index += 1
        return v, soup


    @classmethod
    def getRelated(cls, current_xml_path: Path, include_path: str) -> BeautifulSoup:
        dst = Path(current_xml_path.parent, include_path)

        if include_path.startswith('Aircraft'):
            print(cls.FG_DATA_PATH)
            print(include_path)
            dst = Path(cls.FG_DATA_PATH, include_path)

        print(f"seeking {dst}")
        return BeautifulSoup(dst.read_bytes(), 'lxml-xml')

variant_kv_map = defaultdict(list)

for search_path in search_paths:
    variant_list: List[str] = []
    cur_dir: str = None
    aircraft_id: int = None

    for pth, soup in FileSystemXMLWalker(search_path, fg_data_path):

        print(f"Processing {pth}")
        aircraft_name = pth.stem.split('-set')[0]
        if soup.PropertyList.find('sim') is None:
            print("Skipping, no sim tag")
            continue
        # check for first level includes
        if soup.PropertyList.has_attr('include'):
            include_fn = soup.PropertyList['include']
            incl_xml = FileSystemXMLWalker.getRelated(pth, include_fn)
            soup.PropertyList.append(incl_xml.PropertyList)

        excl_tag = soup.PropertyList.find('exclude-from-gui')

        if excl_tag is not None and excl_tag.text == 'true':
            print('Skip GUI unselectable aircraft')
            continue

        excl_tag = soup.PropertyList.find('exclude-from-catalog')

        if excl_tag is not None and excl_tag.text == 'true':
            print('Skip aircraft excluded from catalog')
            continue

        variant_tag = soup.PropertyList.sim.find('variant-of')
        if variant_tag is not None:
            base = variant_tag.text
            print(f"Caching variant {aircraft_name}")
            variant_kv_map[base].append(aircraft_name)
            # add variants to a list, to be added after we have finished with the current dir
            # process as a variant
        else:
            # not a variant
            print(f"Processing base aircraft {aircraft_name}")

            directory = pth.parent.parts[-1]

            tags = []

            if soup.PropertyList.tags is not None:
                tags = [t.text for t in soup.PropertyList.tags.find_all('tag')]
            else:
                print("No tags found!")

            LoadData(tags, TAG_UPSERT_SQL, conn)

            description = ""

            if soup.description is not None:
                description = soup.description.text

            status = "development"

            if soup.status is not None:
                status = soup.status.text

            rating_fdm = rating_systems = rating_model = rating_cockpit = 0

            if soup.rating is not None:
                rating_fdm = int(soup.rating.FDM.text)
                rating_systems = int(soup.rating.systems.text)
                rating_model = int(soup.rating.model.text)
                rating_cockpit = int(soup.rating.cockpit.text)

            aircraft_id = LoadAndRowAndGetId([aircraft_name, description, directory, STATUS_TO_I[status], rating_fdm, rating_systems, rating_model, rating_cockpit], AIRCRAFT_INSERT_SQL, conn)


            for tag in tags:
                LoadRow([aircraft_id, tag], AIRCRAFT_TAG_ASSOCIATE_SQL, conn)

            LoadRow([aircraft_id, aircraft_name, True], VARIANT_INSERT_SQL, conn)

BASES_WHICH_DONT_EXIST=[
    'Rascal10-JSBsim'
]

# process the variants
for base, variant_list in variant_kv_map.items():
    print(f"Processing base: {base}")
    if base in BASES_WHICH_DONT_EXIST:
        print(f"Skip bad base: {base}")
        continue

    aircraft_id = GetAircraftId(base, conn)

    for variant in variant_list:
        LoadRow([aircraft_id, variant, False], VARIANT_INSERT_SQL, conn)


build_timestamp = int(time.time())

LoadRow(
    ['build_timestamp', f'{build_timestamp}'],
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
