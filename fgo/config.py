#
# I think a dataclass with validators and a loader/saver
# would be a more sustainable approach
#
# see https://stackoverflow.com/a/54489602/806799
#
import yaml
import logging
from pathlib import Path
from dataclasses import dataclass

from sentinels import NOTHING

class GenericAttr:
    def __init__(self, type, validators=(), allow_none=False, default_value=NOTHING):
        logging.debug("genericattr init")
        self.type = type
        self.validators = validators
        self.allow_none = allow_none
        self.default_value = default_value
        logging.debug(f"#{self.validators}")

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if not instance: return self
        return instance.__dict__[self.name]

    def __delete__(self, instance):
        del instance.__dict__[self.name]

    def __set__(self, instance, value):
        logging.debug(f"set generic {self.name}={value}")
        # import ipdb; ipdb.set_trace()
        if isinstance(value, self.__class__) and ((self.allow_none is not NOTHING) or self.default_value):
            if self.default_value is not NOTHING:
                value = self.default_value
            else:
                value = None

        if self.allow_none and value is None:
            instance.__dict__[self.name] = value
            return

        if not isinstance(value, self.type):
            raise TypeError(f"{self.name!r} values must be of type {self.type!r}, got {value.__class__}")

        for validator in self.validators:
            validator(self.name, value)

        instance.__dict__[self.name] = value

def must_be_log_level(name, value):
    if value not in [0, 10, 20, 30, 40, 50]:
        raise ValueError(f"values for {name!r}  have to be a valid log level")


class PathAttr(GenericAttr):
    def __init__(self, validators=(), allow_none=False, default_value=NOTHING):
        logging.debug("pathattr init")
        self.validators = validators
        self.allow_none = allow_none
        self.default_value = default_value
        logging.debug(f"#{self.validators}")

    def __set__(self, instance, value):
        logging.debug(f"set path {self.name}={value}")

        if isinstance(value, self.__class__) and ((self.allow_none is not NOTHING) or self.default_value):
            if self.default_value is not NOTHING:
                value = self.default_value
            else:
                value = None

        if self.allow_none and value is None:
            instance.__dict__[self.name] = value
            return

        if isinstance(value, str):
            value = Path(value)

        if not isinstance(value, Path):
            raise TypeError(f"{self.name!r} values must be of type str or Path")

        for validator in self.validators:
            validator(self.name, value)

        instance.__dict__[self.name] = value

def must_exist(name: str, value: Path):
    if not value.exists():
        raise ValueError(f"values for {name!r} must exist")

def must_be_file(name: str, value: Path):
    if not value.is_file():
        raise ValueError(f"values for {name!r} must be files")

def must_be_directory(name: str, value: Path):
    if not value.is_dir():
        raise ValueError(f"values for {name!r} must be directories")

def must_be_writable(name: str, value: Path):
    logging.warning("#must_be_writable not implemented")

@dataclass
class Config():
    aircraft_path: Path = PathAttr(
        validators=[must_exist, must_be_directory, must_be_writable, ],
        allow_none=True
    )

    config_path: Path = PathAttr(
        allow_none=True
    )

    fgfs_path: Path = PathAttr(
        validators=[must_exist, must_be_file, ],
        allow_none=True
    )
    fgroot_path: Path = PathAttr(
        validators=[must_exist, must_be_directory, must_be_writable, ],
        allow_none=True
    )
    terrasync_path: Path = PathAttr(
        validators=[must_exist, must_be_directory, must_be_writable, ],
        allow_none=True
    )

    uuid: str = GenericAttr(
        str,
        allow_none=True
    )

    log_level: int = GenericAttr(
        int,
        validators=[must_be_log_level, ],
        default_value=logging.INFO
    )

    zeroconf_log_level: int = GenericAttr(
        int,
        validators=[must_be_log_level, ],
        default_value=logging.INFO
    )

    disable_zeroconf: bool = GenericAttr(bool, default_value=False)

    my_fqdn: str = GenericAttr(
        str,
        allow_none=True
    )
    my_hostname: str = GenericAttr(
        str,
        allow_none=True
    )
    my_ip: str = GenericAttr(
        str,
        allow_none=True
    )

    _PERSISTABLE_KEYS = [
        'aircraft_path',
        'fgfs_path',
        'fgroot_path',
        'terrasync_path',
        'uuid'
    ]

    _INSTANCE_KEYS = [

    ]

    _ALL_KEYS = _PERSISTABLE_KEYS + _INSTANCE_KEYS

    @classmethod
    def load(cls, base_dir, args = None):
        config_path = Path(base_dir, "config.yml")
        res = cls(config_path=config_path)
        memo = None

        if config_path.exists():
            logging.info('Loading config')
            with open(config_path, 'rt') as fh:
                memo = yaml.load(fh.read())

        if memo:
            res.merge_dictionary(memo)

        if args:
            res.merge_namespace(args)

        return res

    def save(self):
        res = {}

        for k in self._PERSISTABLE_KEYS:
            v = getattr(self, k)

            res[k] = v

        with open(self.config_path, 'wt') as fh:
            logging.info('Saving config')
            fh.write(yaml.dump(res))

    def merge_namespace(self, namespace):
        for key in self._ALL_KEYS:
            val = getattr(namespace, key)

            if val is not None:
                setattr(self, key, val)

    def merge_dictionary(self, dictionary):
        for key in self._PERSISTABLE_KEYS:
            setattr(self, key, dictionary[key])
