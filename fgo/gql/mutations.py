import graphene

from . import types

from fgo import util

class InstallOrUpdateAircraftRequest(graphene.Mutation):
    class Arguments(graphene.Mutation):
        svn_name = graphene.String()

    ok = graphene.Boolean()
    error = graphene.String()

    def mutate(self, ctx, svn_name):
        ok = True
        error = None
        #
        # TODO: if app is in state ready, change state to aircraft install requested
        #       change state_meta to be the svn_name
        #
        #       the giant state machine will:
        #           - check if the aircraft has already been cloned
        #           - change current state to AIRCRAFT_INSTALLING
        #               - in a background thread
        #                   - do an svn up on it if it already exists
        #                   - or a fresh check out
        #                   - progress state to READY or ERROR when done
        #
        return InstallOrUpdateAircraftRequest(ok=ok, error=error)

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
        keys_whitelist = ["fgfs_path", "fgroot_path", "aircraft_path", "terrasync_path"]

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
