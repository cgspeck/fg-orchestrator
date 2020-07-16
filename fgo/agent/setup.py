import logging
import shutil
import sys
import os

from pathlib import Path

from fgo.config import Config
from fgo.agent import util


class Setup:
    def __init__(self, config: Config):
        self._config = config

    def run(self):
        logging.info("Setting up this agent...")
        self._copyProtocolFile()

    def _copyProtocolFile(self):
        src = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'data',
            'fgo.xml'
        )
        dst_fgroot = self._config.fgroot_path

        if dst_fgroot is None or not dst_fgroot.exists():
            logging.info(f"{dst_fgroot} does not exist! Searching for $FG_ROOT...")
            discovered_os, discovered_os_str = util.discover_os()
            logging.info(f"This agent appears to be running {discovered_os_str}")
            dst_fgroot = Path(getattr(util, f"{discovered_os.lower_name}_find_fgroot")())

        if not dst_fgroot.exists():
            logging.info(f"Fall-back path {dst_fgroot} does not exist!")
            sys.exit(1)

        dst_protocol_file = Path(
            dst_fgroot,
            "Protocol",
            "fgo.xml"
        )
        logging.info(f"Copying {src} to {dst_protocol_file}")

        try:
            shutil.copyfile(src, dst_protocol_file)
        except PermissionError as e:
            logging.error(e)
            logging.info("Try running `sudo ./venv/bin/fgo setup` (Linux/OSX) or in an administrator level console (Windows).")
            sys.exit(2)

