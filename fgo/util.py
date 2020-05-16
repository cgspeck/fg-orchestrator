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
