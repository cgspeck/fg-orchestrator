import platform
import logging
import hashlib

import graphene


class ErrorCode(graphene.Enum):
    UNKNOWN = 0
    FGFS_PATH_NOT_SET = 1
    FGFS_PATH_NOT_EXIST = 2
    TERRASYNC_PATH_NOT_EXIST = 4
    AIRCRAFT_PATH_NOT_SET = 5
    AIRCRAFT_PATH_NOT_EXIST = 6
    FGROOT_PATH_NOT_SET = 7
    FGROOT_PATH_NOT_EXIST = 8
    AIRCRAFT_NOT_IN_VERSION_CONTROL = 9
    FGFS_ABNORMAL_EXIT = 10
    FGHOME_PATH_NOT_SET = 11
    FGHOME_PATH_NOT_EXIST = 12
    FG_VERSION_CHECK_FAILED = 13
    AIRCRAFT_INSTALL_FAILED = 14
    SVN_NOT_INSTALLED = 15


class OS(graphene.Enum):
    UNKNOWN = 0
    LINUX = 1
    DARWIN = 2
    WINDOWS = 3

    @property
    def lower_name(self):
        return self.name.lower()


class Role(graphene.Enum):
    MASTER = 0
    SLAVE = 1


class Status(graphene.Enum):
    SCANNING = 0
    READY = 1
    ERROR = 2
    FGFS_START_REQUESTED = 3
    FGFS_STARTING = 4
    FGFS_RUNNING = 5
    FGFS_STOP_REQUESTED = 6
    INSTALLING_AIRCRAFT = 8


class TimeOfDay(graphene.Enum):
    """Represents a selectable time of day for a scenario"""
    MORNING = 2
    REAL = 0
    DAWN = 1
    NOON = 3
    AFTERNOON = 4
    DUSK = 5
    EVENING = 6
    MIDNIGHT = 7

    @property
    def lower_name(self):
        return self.name.lower()


class Aircraft(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    version = graphene.String()


class AIScenario(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()

    def resolve_id(self, info):
        return hashlib.md5(f"{self.name}".encode()).hexdigest()


class ConfigEntry(graphene.ObjectType):
    id = graphene.ID()
    key = graphene.String()
    value = graphene.String()

    def resolve_id(self, info):
        return hashlib.md5(f"{self.key}.{self.value}".encode()).hexdigest()

class DirectoryList(graphene.ObjectType):
    id = graphene.ID()
    base_path = graphene.String()
    files = graphene.List(graphene.String)
    directories = graphene.List(graphene.String)

    def resolve_id(self, info):
        return hashlib.md5(f"{self.base_path}".encode()).hexdigest()


class Error(graphene.ObjectType):
    id = graphene.ID()
    code = graphene.Field(ErrorCode)
    description = graphene.String()

    def resolve_id(self, info):
        return hashlib.md5(f"{self.code}".encode()).hexdigest()


class Info(graphene.ObjectType):
    id = graphene.ID()
    os = graphene.Field(OS)
    os_string = graphene.String()
    status = graphene.Field(Status)
    timestamp = graphene.Int()
    errors = graphene.List(Error)
    aircraft = graphene.List(Aircraft)
    uuid = graphene.String()

    def resolve_id(self, info):
        return hashlib.md5(f"{self.status}_{self.timestamp}".encode()).hexdigest()


class FlightGearStartInput(graphene.InputObjectType):
    # common to all
    aircraft = graphene.String(default_value='c172p')
    aircraft_variant = graphene.String(default_value='c172p')
    # ai scenarios are linked to carriers
    ai_scenario = graphene.List(graphene.String, description="Add and enable a new scenario. Multiple options are allowed.")
    carrier = graphene.String(description="Place aircraft on aircraft carrier")
    # airport must come after carrier in order for carrier starts to work
    airport_code = graphene.String(description="Place aircraft at airport code")
    ceiling = graphene.String(description="Height and thickness of ceiling in feet, e.g 10000:2000")
    enable_auto_coordination = graphene.Boolean(description="Auto-cordination controls rudder and ailerons together", default_value=True)
    runway = graphene.String(description="Specify starting runway")
    terrasync_http_server = graphene.String(description="Specify a Terrasync endpoint to use")
    time_of_day = graphene.Field(TimeOfDay)
    visibility_meters = graphene.Int()

    # specific to this agent - shown
    additional_args = graphene.List(graphene.String)
    disable_panel = graphene.Boolean()
    disable_hud = graphene.Boolean()
    disable_anti_alias_hud = graphene.Boolean()
    enable_clouds = graphene.Boolean()
    enable_clouds3d = graphene.Boolean()
    enable_fullscreen = graphene.Boolean(default_value=True)
    enable_terrasync = graphene.Boolean(default_value=True)
    enable_real_weather_fetch = graphene.Boolean(default_value=True)

    fov = graphene.Int(description="Override the computed FOV")
    view_offset = graphene.Int(0, description="Specify the default forward view direction in degrees. Increments of 50-60 degrees are suggested.")

    # specific to this agent - hidden
    client_ip_addresses = graphene.List(graphene.String)
    role = graphene.Field(Role)

    # computed
    # assembled_args = graphene.List(graphene.String)

    def assemble_args(self):
        '''
        Returns a list of arguments that should be passed to FGFS

        See http://wiki.flightgear.org/Command_line_options
        '''
        logging.debug("Assembling FGFS args")
        res = []

        attr_map = {
            # defaults - common
            "aircraft_variant": ["--aircraft={attr_val}"],
            "airport_code": ["--airport={attr_val}", "--on-ground"],
            "runway": ["--runway={attr_val}"],
            "terrasync_http_server": ["--prop:/sim/terrasync/http-server={attr_val}"],
            # optionals - common
            "carrier": ["--carrier={attr_val}"],
            "ceiling": ["--ceiling={attr_val}"],
            "visibility_meters": ["--visibility={attr_val}"],
            # optionals - agent
            "fov": ["--fov={attr_val}"],
            "view_offset": ["--view-offset={attr_val}"]
        }

        for attr_key, attr_val in self.items():
            logging.debug(f"Processing {attr_key}:{attr_val}")

            if attr_key == 'aircraft':
                # aircraft is actually specified by the aircraft_variant
                continue

            if attr_key == 'ai_scenario':
                for arg in attr_val:
                    memo = f"--ai-scenario={arg}"
                    logging.debug(f"Adding arg: {memo}")
                    res.append(memo)
                continue

            if attr_key == 'additional_args':
                for arg in attr_val:
                    logging.debug(f"Adding arg: {arg}")
                    res.append(arg)
                continue

            if attr_key == 'time_of_day':
                memo = f"--timeofday={TimeOfDay.get(attr_val).lower_name}"
                logging.debug(f"Adding arg: {memo}")
                res.append(memo)
                continue

            if attr_key == 'client_ip_addresses':
                for arg in attr_val:
                    memo = f"--native=socket,out,60,{arg},5000,udp"
                    logging.debug(f"Adding arg: {memo}")
                    res.append(memo)
                continue

            if attr_key == 'enable_auto_coordination' and attr_val is not None:
                if attr_val:
                    res.append("--enable-auto-coordination")
                continue

            if attr_key == 'disable_panel' and attr_val is not None:
                if attr_val:
                   res.append("--disable-panel")
                continue

            if attr_key == 'disable_hud' and attr_val is not None:
                if attr_val:
                   res.append("--disable-hud")
                continue

            if attr_key == 'disable_anti_alias_hud' and attr_val is not None:
                if attr_val:
                   res.append("--disable-anti-alias-hud")
                continue

            if attr_key == 'enable_clouds' and attr_val is not None:
                if attr_val:
                   res.append("--enable-clouds")
                continue

            if attr_key == 'enable_clouds3d' and attr_val is not None:
                if attr_val:
                   res.append("--enable-clouds3d")
                continue

            if attr_key == 'enable_fullscreen' and attr_val is not None:
                if attr_val:
                   res.append("--enable-fullscreen")
                continue

            if attr_key == 'enable_real_weather_fetch' and attr_val is not None:
                if attr_val:
                   res.append("--enable-real-weather-fetch")
                continue

            if attr_key == 'enable_terrasync' and attr_val is not None:
                if attr_val:
                   res.append("--enable-terrasync")
                continue

            if attr_key == 'role':
                if Role.get(attr_val) == Role.MASTER:
                    # set up the Phi Webserver: http://wiki.flightgear.org/Phi
                    memo = "--httpd=8080"
                    logging.debug(f"Adding arg: {memo}")
                    res.append(memo)

                if Role.get(attr_val) == Role.SLAVE:
                    # disable the FDM
                    memo = "--fdm=external"
                    logging.debug(f"Adding arg: {memo}")
                    res.append(memo)
                    # tell it to receive data
                    memo = "--native=socket,in,60,,5000,udp"
                    logging.debug(f"Adding arg: {memo}")
                    res.append(memo)
                continue

            tokens = attr_map[attr_key]

            for token in tokens:
                token_res = token.format(attr_val=attr_val)
                logging.debug(f"Adding {token_res}")
                res.append(token_res)

        logging.debug(f"Assembled args: {res}")
        return res


class Version(graphene.ObjectType):
    id = graphene.ID()
    major = graphene.Int()
    minor = graphene.Int()
    patch = graphene.Int()
    version_string = graphene.String()

    def resolve_version_string(self, info):
        return f"{self.major}.{self.minor}.{self.patch}"

    def resolve_id(self, info):
        return hashlib.md5(f"{self.major}.{self.minor}.{self.patch}".encode()).hexdigest()
