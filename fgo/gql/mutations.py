import graphene

from . import types

from fgo import util

class SetConfig(graphene.Mutation):
    class Arguments:
        key = graphene.String()
        value = graphene.String()
    
    ok = graphene.Boolean()
    error = graphene.String()

    def mutate(self, ctx, key, value):
        ok = True
        error = None

        app_context = ctx.context
        keys_whitelist = ["fgfs_path", "aircraft_path", "terrasync_path"]

        if key not in keys_whitelist:
            ok = False
            error = f"Unrecognised key {key}"

        if ok:
            with app_context['context_lock']:
                # update in-memory settings
                # update settings file on disk
                settings = app_context['settings']
                settings[key] = value
                util.save_config(settings['base_dir'], settings)
                app_context['info'].status = types.Status.SCANNING
                app_context['info'].errors = None

        return SetConfig(ok=ok, error=error)
