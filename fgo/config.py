import os
import yaml
import typing
import logging

from pathlib import Path
from dataclasses import dataclass

from sentinels import NOTHING


class PathNotExistError(Exception):
    pass


class PathNotDirectoryError(Exception):
    pass


class GenericAttr:
    def __init__(self, type_, validators=(), allow_none=False, default_value=NOTHING):
        self.type = type_
        self.validators = validators
        self.allow_none = allow_none
        self.default_value = default_value

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if not instance:
            return self

        return instance.__dict__[self.name]

    def __delete__(self, instance):
        del instance.__dict__[self.name]

    def __set__(self, instance, value):
        logging.debug(f"set generic {self.name}={value}")
        if isinstance(value, self.__class__) and ((self.allow_none is not NOTHING) or self.default_value):
            if self.default_value is not NOTHING:
                value = self.default_value
            else:
                value = None

        if self.allow_none and value is None:
            instance.__dict__[self.name] = value
            return

        if not isinstance(value, self.type):
            raise TypeError(
                f"{self.name!r} values must be of type {self.type!r}, got {value.__class__}")

        for validator in self.validators:
            validator(self.name, value)

        instance.__dict__[self.name] = value


def must_be_log_level(name, value):
    if value not in ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL']:
        raise ValueError(f"values for {name!r}  have to be a valid log level")


class PathAttr(GenericAttr):
    def __init__(self, validators=(), allow_none=False, default_value=NOTHING):
        super().__init__(None, validators, allow_none, default_value)

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
            raise TypeError(
                f"{self.name!r} values must be of type str or Path")

        for validator in self.validators:
            validator(self.name, value)

        instance.__dict__[self.name] = value


def must_exist(name: str, value: Path):
    if not value.exists():
        raise PathNotExistError(f"{name!r} does not exist")


def must_be_file(name: str, value: Path):
    if not value.is_file():
        raise ValueError(f"values for {name!r} must be files")


def must_be_directory(name: str, value: Path):
    if not value.is_dir():
        raise PathNotDirectoryError(f"{name!r} must be a directory")


def must_be_writable(name: str, value: Path):
    logging.warning(
        f"must_be_writable not implemented, called with {name}={value}")


@dataclass
class Config:
    base_dir: Path = PathAttr(
        validators=[must_exist, must_be_directory, must_be_writable],
        allow_none=True
    )
    config_path: Path = PathAttr(
        allow_none=True
    )
    logs_dir: Path = PathAttr(
        validators=[must_exist, must_be_directory, must_be_writable],
        allow_none=True
    )
    director_dir: Path = PathAttr(
        validators=[must_exist, must_be_directory, must_be_writable],
        allow_none=True
    )
    nav_db: Path = PathAttr(
        allow_none=True
    )
    parking_cache_dir: Path = PathAttr(
        validators=[must_exist, must_be_directory, must_be_writable],
        allow_none=True
    )

    fgfs_path: Path = PathAttr(
        validators=[must_exist, must_be_file, ],
        allow_none=True
    )
    # http://wiki.flightgear.org/$FG_ROOT - RO
    fgroot_path: Path = PathAttr(
        validators=[must_exist, must_be_directory, ],
        allow_none=True
    )
    # http://wiki.flightgear.org/$FG_HOME - RW
    fghome_path: Path = PathAttr(
        validators=[must_exist, must_be_directory, must_be_writable, ],
        allow_none=True
    )
    # usually lives under fghome
    terrasync_path: Path = PathAttr(
        validators=[must_exist, must_be_directory, must_be_writable, ],
        allow_none=True
    )
    # usually lives under fghome
    aircraft_path: Path = PathAttr(
        validators=[must_exist, must_be_directory, must_be_writable, ],
        allow_none=True
    )

    uuid: str = GenericAttr(
        str,
        allow_none=True
    )

    log_level: str = GenericAttr(
        str,
        validators=[must_be_log_level, ],
        default_value='INFO'
    )

    zeroconf_log_level: str = GenericAttr(
        str,
        validators=[must_be_log_level, ],
        default_value='INFO'
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
    agent_service_name: str = GenericAttr(
        str,
        allow_none=True
    )
    fgfs_startup_time: int = GenericAttr(
        int,
        default_value=60
    )

    _PERSISTABLE_KEYS = [
        'aircraft_path',
        'fgfs_path',
        'fgroot_path',
        'fghome_path',
        'terrasync_path',
        'fgfs_startup_time',
        'uuid'
    ]

    _INSTANCE_KEYS = [
        'base_dir',
        'logs_dir',
        'director_dir',
        'nav_db',
        'parking_cache_dir'
    ]

    _ALL_KEYS = _PERSISTABLE_KEYS + _INSTANCE_KEYS

    @classmethod
    def load(cls, base_dir, args=None):
        config_path = Path(base_dir, "config.yml")
        logging.info(f"Loading config from {config_path}")
        res = cls(config_path=config_path)
        memo = None

        if config_path.exists():
            with config_path.open('rt') as fh:
                memo = yaml.load(fh.read(), Loader=yaml.UnsafeLoader)

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

        self.config_path.write_text(yaml.dump(res))

    def merge_namespace(self, namespace):
        for key in self._ALL_KEYS:
            val = getattr(namespace, key)

            if val is not None:
                setattr(self, key, val)

    def merge_dictionary(self, dictionary):
        for key in self._ALL_KEYS:
            if key in dictionary.keys():
                try:
                    setattr(self, key, dictionary[key])
                except PathNotExistError as e:
                    logging.error(
                        f"Unable to set {key} to {dictionary[key]}: {e}")

    def assemble_fgfs_env_vars(self) -> typing.Tuple[dict, dict]:
        '''
        Returns a tuple of:
            - dictionary with custom args only
            - dictionary with all args
        '''
        custom_vars = {}
        system_vars = os.environ

        key_var = {
            'fgroot_path': 'FG_ROOT',
            'fghome_path': 'FG_HOME'
        }

        if self.fgroot_path:
            custom_vars['FG_ROOT'] = self.fgroot_path

        if self.fghome_path:
            custom_vars['FG_HOME'] = self.fghome_path

        for k, env_k in key_var.items():
            v = getattr(self, k)

            if v is not None:
                custom_vars[env_k] = f"{v}"

        logging.debug(f"assemble_fgfs_env_vars custom vars: {custom_vars}")
        return {**custom_vars}, {**system_vars, **custom_vars}
