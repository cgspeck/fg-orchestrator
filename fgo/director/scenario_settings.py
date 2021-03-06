from dataclasses import dataclass, field
import typing

@dataclass
class ScenarioSettings:
    aircraft: str = None
    aircraft_directory: str = None
    aircraft_variant: str = None
    time_of_day: str = None
    primary: str = None
    secondaries: typing.List[str] = field(default_factory=list)
    airport: str = None
    carrier: str = None
    runway: str = None
    parking: str = None
    terra_sync_endpoint: str = None
    ceiling: str = None
    enable_auto_coordination: bool = None
    visibility_in_meters: int = None
    ai_scenarios: typing.List[str] = field(default_factory=list)
    skip_aircraft_install: bool = None
    selected_airport_option: int = 0
    selected_runway_option: int = 0

    def to_dict(self):
        """ return a dictionary for serialisation """
        res = {}
        for attr_key in [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self,a))]:
            res[attr_key] = getattr(self, attr_key)
        return res

    @staticmethod
    def from_dict(dictionary):
        """ load scenario settings from dictionary """
        s = ScenarioSettings()
        for attr_key, attr_val in dictionary.items():
            setattr(s, attr_key, attr_val)

        return s
