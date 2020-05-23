import socket
import logging
from pathlib import Path

import yaml


def check_folders():
    base_dir = Path(Path.home(), "fgo")
    logs_dir = Path(base_dir, "logs")
    director_dir = Path(base_dir, "director")

    for directory in [base_dir, logs_dir, director_dir]:
        if not directory.exists():
            logging.info(f'Creating directory {directory}')
            directory.mkdir()

    return {
        'base_dir': base_dir,
        'logs_dir': logs_dir,
        'director_dir': director_dir
    }

def get_ip_address() -> str:
    # https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip_address = s.getsockname()[0]
    except:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

def load_config(base_dir):
    config_file = Path(base_dir, "config.yml")
    res = None

    if config_file.exists():
        logging.info('Loading config')
        with open(config_file, 'rt') as fh:
            res = yaml.load(fh.read(), Loader=yaml.UnsafeLoader)

    return res if res else {}


def save_config(base_dir, settings):
    config_file = Path(base_dir, "config.yml")

    whitelist_keys = [
        'aircraft_path',
        'fgfs_path',
        'fgroot_path',
        'terrasync_path',
        'uuid'
    ]

    res = {}

    for k in whitelist_keys:
        v = settings.get(k)

        if v is not None:
            res[k] = v

    with open(config_file, 'wt') as fh:
        logging.info('Saving config')
        fh.write(yaml.dump(res))
