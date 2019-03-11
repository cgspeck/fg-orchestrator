import logging

import graphene

from . import types

from fgo import util


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


class RescanEnvironment(graphene.Mutation):
    ok = graphene.Boolean()

    def mutate(self, ctx):
        app_context = ctx.context

        if app_context['info'].status != types.Status.SCANNING:
            with app_context['context_lock']:
                app_context['info'].status = types.Status.SCANNING
                app_context['info'].errors = None

        return RescanEnvironment(ok=True)


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
        keys_whitelist = ["fgfs_path", "fgroot_path", "fghome_path", "aircraft_path", "terrasync_path"]

        if key not in keys_whitelist:
            ok = False
            error = f"Unrecognised key {key}"

        if ok:
            with app_context['context_lock']:
                # update in-memory settings
                # update settings file on disk
                config = app_context['config']
                setattr(config, key, value)
                config.save()
                app_context['info'].status = types.Status.SCANNING
                app_context['info'].errors = None

        return SetConfig(ok=ok, error=error)


class StartFlightGear(graphene.Mutation):
    class Arguments:
        additional_args = graphene.List(graphene.String)
        aircraft = graphene.String(default_value='c172p')
        airport_code = graphene.String(default_value='YMML', description="Place aircraft at airport code")
        carrier = graphene.String(description="Place aircraft on aircraft carrier")
        ceiling = graphene.Int()
        client_ip_addresses = graphene.List(graphene.String)
        disable_fullscreen = graphene.Boolean(default_value=False)
        enable_clouds = graphene.Boolean()
        enable_clouds3d = graphene.Boolean()
        enable_fullscreen = graphene.Boolean(default_value=True)
        enable_real_weather_fetch = graphene.Boolean(default_value=True)
        fov = graphene.Int(description="Override the computed FOV")
        master_ip_address = graphene.String()
        role = graphene.String()  # make this an enum, MASTER || SLAVE
        time_of_day = graphene.String(default_value='noon')
        view_offset = graphene.Int(0)
        visibility_meters = graphene.Int()

    ok = graphene.Boolean()
    error = graphene.String()

    def assemble_args(self):
        '''
        Returns a list of arguments that should be passed to FGFS
        '''
        logging.debug("Assembling FGFS args")
        res = []

        attr_map = {
            "aircraft": [f"--aircraft={attr_val}"],
        }

        for attribute, tokens in attr_map.items():
            attr_val = getattr(self, attribute)

            if attr_val:
                for token in tokens:
                    logging.debug(f"Adding {token}")
                    res.append(token)
        
        for arg in getattr(self, 'additional_args'):
            logging.debug(f"Adding additional arg {arg}")
            res.append(arg)

        return res

    def mutate(self, ctx, **args):
        ok = True
        error = None

        app_context = ctx.context
        current_status = app_context['info'].status
        logging.info(self.assemble_args())

        # if current_status != types.Status.READY:
        #     ok = False
        #     error = f"Unable to start FlightGear, current state is {current_status}"

        # if ok:
        #     app_context['info'].status = types.Status.FGFS_START_REQUESTED
        #     app_context['state_meta'] = self.assemble_args()

        return StartFlightGear(ok=ok, error=error)


class StopFlightGear(graphene.Mutation):
    ok = graphene.Boolean()
    error = graphene.String()

    def mutate(self, ctx):
        ok = True
        error = None

        app_context = ctx.context
        current_status = app_context['info'].status

        if current_status != types.Status.FGFS_RUNNING:
            ok = False
            error = f"Unable to stop FlightGear, current state is {current_status}"

        if ok:
            app_context['info'].status = types.Status.FGFS_STOP_REQUESTED
            app_context['state_meta'] = None

        return StopFlightGear(ok=ok, error=error)
