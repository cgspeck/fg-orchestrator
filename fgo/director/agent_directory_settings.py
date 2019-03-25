import logging
import typing
from dataclasses import dataclass, field

@dataclass
class AgentDirectorySettings:
    flightgear_executable: str = None
    fgroot_path: str = None
    fghome_path: str = None
    terrasync_path: str = None
    aircraft_path: str = None

    @classmethod
    def from_gql_query(cls, gql_result: typing.List[typing.Dict[str, str]]):
        """ Return an instance of this class with its values loaded from the GQL query """
        logging.debug(f"AgentDirectorySettings.from_gql_query gql_result is {gql_result}")
        mapping = {
            'fgfs_path': 'flightgear_executable',
            'fgroot_path': 'fgroot_path',
            'fghome_path': 'fghome_path',
            'terrasync_path': 'terrasync_path',
            'aircraft_path': 'aircraft_path'
        }
        res = cls()

        for entry in gql_result:
            entry_key = entry['key']
            if entry_key in mapping.keys():
                setattr(res, mapping[entry_key], entry['value'])

        logging.debug(f"AgentDirectorySettings.from_gql_query res is {res}")

        return res
