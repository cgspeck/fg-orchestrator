#
# I think a dataclass with validators and a loader/saver
# would be a more sustainable approach
#
# see https://stackoverflow.com/a/54489602/806799
#
import yaml
import logging
from pathlib import Path

class Config():
    _SAVABLE_KEYS = [
        'aircraft_path',
        'fgfs_path',
        'fgroot_path',
        'terrasync_path',
        'uuid'
    ]
    _INMEMORY_KEYS = [
        'log_level',
        'zeroconf_log_level',
        'disable_zeroconf',
        'my_fqdn',
        'my_hostname',
        'my_ip'
    ]
    _WHITELIST = _SAVABLE_KEYS + _INMEMORY_KEYS

    @classmethod
    def load(cls, base_dir, args = None):
        res = cls()
        config_file = Path(base_dir, "config.yml")
        memo = None

        if config_file.exists():
            logging.info('Loading config')
            with open(config_file, 'rt') as fh:
                memo = yaml.load(fh.read())

        if memo:
            res.merge_dictionary(memo)

        if args:
            res.merge_namespace(args)

        return res

    def save(self):
        res = {}

        for k in self._SAVABLE_KEYS:
            v = self._data.get(k)

            res[k] = v

        with open(self._config_file_path, 'wt') as fh:
            logging.info('Saving config')
            fh.write(yaml.dump(res))

    def __init__(self, config_file_path):
        self._config_file_path = config_file_path
        self._data = {}

    def merge_namespace(self, namespace):
        pass

    def merge_dictionary(self, dictionary):
        for k, v in dictionary.items():
            self.set_value(k, v)

    def set_value(self, key, value):
        if key not in self._WHITELIST:
            raise ValueError(f"{key} is not on the whitelist")

        self._data[key] = value

    def get_value(self, key, value):
        if key not in self._WHITELIST:
            raise ValueError(f"{key} is not on the whitelist")

        return self._data.get(key)

    def valdate_value(self, key, value):
        pass
