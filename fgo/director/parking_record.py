from dataclasses import dataclass, field

@dataclass
class ParkingRecord:
    airport_code: str = None
    index: int = 0
    parking_type: str = None
    name: str = None
    number: str = None
    airline_codes: str = None
    has_airline_codes: bool = False

    def to_dict(self):
        res = {}
        for attr_key in [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self,a))]:
            res[attr_key] = getattr(self, attr_key)
        return res


    @staticmethod
    def from_dict(dictionary):
        """ load ParkingRecord from a dictionary """
        s = ParkingRecord()
        for attr_key, attr_val in dictionary.items():
            setattr(s, attr_key, attr_val)

        return s
