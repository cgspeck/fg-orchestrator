import time

import graphene

from . import types

class Query(graphene.ObjectType):
    info = graphene.Field(types.Info)

    def resolve_info(self, ctx):
        return ctx.context['info']

Schema = graphene.Schema(query=Query)
