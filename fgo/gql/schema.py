import graphene

class Status(graphene.Enum):
    BOOTING = 0
    READY = 1
    ERROR = 2
    RUNNING = 3
    UPDATING = 4

class Info(graphene.ObjectType):
    id = graphene.ID()
    status = graphene.List(Status)

    def resolve_status(self, ctx):
        pass

class Query(graphene.ObjectType):
    info = graphene.Field(Info)

    def resolve_info(self, ctx):
        pass

Schema = graphene.Schema(query=Query)
