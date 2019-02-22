import hashlib

import graphene

class Status(graphene.Enum):
    BOOTING = 0
    READY = 1
    ERROR = 2
    RUNNING = 3
    UPDATING = 4

class Info(graphene.ObjectType):
    id = graphene.ID()
    status = graphene.Field(Status)
    timestamp = graphene.Int()

    def resolve_id(self, info):
        return hashlib.md5(f"{self.status}_{self.timestamp}".encode()).hexdigest()
