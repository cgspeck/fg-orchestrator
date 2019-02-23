import platform

import hashlib

import graphene

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
    TERRASYNC_PATH_NOT_SET = 3
    TERRASYNC_PATH_EXIST = 4
    AIRCRAFT_PATH_NOT_SET = 5
    AIRCRAFT_PATH_NOT_EXIST = 6

class Error(graphene.ObjectType):
    id = graphene.ID()
    code = graphene.Field(ErrorCode)

    def resolve_id(self, info):
        return hashlib.md5(f"{self.code}".encode()).hexdigest()

class OS(graphene.Enum):
    UNKNOWN = 0
    LINUX = 1
    DARWIN = 2
    WINDOWS = 3

class Aircraft(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    version = graphene.String()

class Status(graphene.Enum):
    SCANNING = 0
    READY = 1
    ERROR = 2
    RUNNING = 3
    INSTALLING_AIRCRAFT = 4

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
