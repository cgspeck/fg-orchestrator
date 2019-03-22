from dataclasses import dataclass, field
import typing

@dataclass
class ScenarioSettings:
    aircraft: str = None
    time_of_day: str = None
    master: str = None
    slaves: typing.List[str] = field(default_factory=list)
    airport: str = None
    carrier: str = None
    runway: str = None
    parking: str = None
    terra_sync_endpoint: str = None
    ceiling: str = None
    enable_auto_coordination: bool = None
    visibility_in_meters: int = None
    ai_scenarios: typing.List[str] = field(default_factory=list)

    def to_dict(self):
        ''' return a dictionary for serialisation'''
        pass

    def from_dict(self):
        ''' load scenario settings from dictionary'''
        pass
