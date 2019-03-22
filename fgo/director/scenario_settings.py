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
        res = {}
        for attr_key in [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self,a))]:
            res[attr_key] = getattr(self, attr_key)
        return res

    @staticmethod
    def from_dict(dictionary):
        ''' load scenario settings from dictionary'''
        s = ScenarioSettings()
        for attr_key, attr_val in dictionary.items():
            setattr(s, attr_key, attr_val)
        
        return s
