import platform

import hashlib

import graphene

class ConfigEntry(graphene.ObjectType):
    id = graphene.ID()
    key = graphene.String()
    value = graphene.String()

    def resolve_id(self, info):
        return hashlib.md5(f"{self.key}.{self.value}".encode()).hexdigest()

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

class DirectoryList(graphene.ObjectType):
    id = graphene.ID()
    base_path = graphene.String()
    files = graphene.List(graphene.String)
    directories = graphene.List(graphene.String)

    def resolve_id(self, info):
        return hashlib.md5(f"{self.base_path}".encode()).hexdigest()

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

class Error(graphene.ObjectType):
    id = graphene.ID()
    code = graphene.Field(ErrorCode)
    description = graphene.String()

    def resolve_id(self, info):
        return hashlib.md5(f"{self.code}".encode()).hexdigest()

class OS(graphene.Enum):
    UNKNOWN = 0
    LINUX = 1
    DARWIN = 2
    WINDOWS = 3

    @property
    def lower_name(self):
        return self.name.lower()

class Aircraft(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    version = graphene.String()

class Status(graphene.Enum):
    SCANNING = 0
    READY = 1
    ERROR = 2
    FGFS_STARTING = 3
    FGFS_RUNNING = 4
    FGFS_STOPPING = 5
    INSTALLING_AIRCRAFT = 6

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
