import time
import logging
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from PyQt5.QtCore import QRunnable

from fgo.director import signals
from fgo.director.parking_record import ParkingRecord


class ParkingCacheUpdaterWorker(QRunnable):

    def __init__(self, airport_code, cache_dir):
        super(ParkingCacheUpdaterWorker, self).__init__()
        self.airport_code = airport_code
        self.cache_dir = cache_dir
        self.signals = signals.ParkingCacheUpdaterSignals()

    def run(self):
        needs_download = False
        threshold = time.time() - (60 * 24 * 60 * 60)
        filename = f"{self.airport_code}.groundnet.xml"
        records = []

        cache_file = Path(
            self.cache_dir,
            filename
        )

        needs_download = (not cache_file.exists()) or (cache_file.stat().st_mtime < threshold)

        if needs_download:
            url = f"http://flightgear.sourceforge.net/scenery/Airports/{self.airport_code[0]}/{self.airport_code[1]}/{self.airport_code[2]}/{self.airport_code}.groundnet.xml"

            if len(self.airport_code) == 3:
                url = f"http://flightgear.sourceforge.net/scenery/Airports/{self.airport_code[0]}/{self.airport_code[1]}/{self.airport_code}.groundnet.xml"

            logging.info(f"Downloading from {url} to {cache_file}")

            r = requests.get(url)

            if r.status_code != 200:
                logging.info(f"Error downloading groundnet, http status code {r.status_code}")
            else:
                with cache_file.open("wt") as fw:
                    fw.write(r.text)

                soup = BeautifulSoup(r.text, 'lxml-xml')

                for xml_record in soup.groundnet.parkingList.find_all('Parking'):
                    stripped_airline_codes = xml_record['airlineCodes'].strip()

                    number = ''
                    try:
                        number = xml_record['number'].strip()
                    except KeyError:
                        pass

                    records.append(
                        ParkingRecord(
                            self.airport_code,
                            int(xml_record['index']),
                            xml_record['type'],
                            xml_record['name'],
                            number,
                            stripped_airline_codes,
                            len(stripped_airline_codes) > 0
                        )
                    )

        self.signals.parking_cache_ready.emit(
            self.airport_code,
            records
        )

