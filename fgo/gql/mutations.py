import graphene

from . import types

from fgo import util

class RescanEnvironment(graphene.Mutation):
    ok = graphene.Boolean()

    def mutate(self, ctx):
        app_context = ctx.context

        if app_context['info'].status != types.Status.SCANNING:
            with app_context['context_lock']:
                app_context['info'].status = types.Status.SCANNING
                app_context['info'].errors = None

        return RescanEnvironment(ok=True)

class InstallOrUpdateAircraft(graphene.Mutation):
    class Arguments:
        svn_name = graphene.String()

    ok = graphene.Boolean()
    error = graphene.String()

    def mutate(self, ctx, svn_name):
        ok = True
        error = None
        #
        # if app is in state ready, change state to aircraft install requested
        # change state_meta to be the svn_name
        # 
        app_context = ctx.context
        current_status = app_context['info'].status
        if current_status != types.Status.READY:
            ok = False
            error = f"Unable to install/update aircraft, current state is {current_status}"

        if ok:
            with app_context['context_lock']:
                app_context['info'].status = types.Status.INSTALLING_AIRCRAFT
                app_context['state_meta'] = svn_name

        return InstallOrUpdateAircraft(ok=ok, error=error)

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
