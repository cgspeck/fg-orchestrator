from pathlib import Path
import platform
import string
import time

import graphene

from . import types, mutations

def get_windows_drives():
    from ctypes import windll
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(f"{letter}:")
        bitmask >>= 1

    return drives

class Mutations(graphene.ObjectType):
    install_or_update_aircraft = mutations.InstallOrUpdateAircraft.Field()
    rescan_environment = mutations.RescanEnvironment.Field()
    set_config = mutations.SetConfig.Field()
    start_flight_gear = mutations.StartFlightGear.Field()
    stop_flight_gear = mutations.StopFlightGear.Field()

class Query(graphene.ObjectType):
    ai_scenarios = graphene.List(types.AIScenario)
    config = graphene.List(types.ConfigEntry)
    directory_list = graphene.Field(types.DirectoryList, base_path=graphene.String(default_value="/"))
    info = graphene.Field(types.Info)
    version = graphene.Field(types.Version)

    def resolve_ai_scenarios(self, ctx):
        config = ctx.context['config']
        fgroot_path = config.fgroot_path
        if fgroot_path:
            scenarios = []
            for scenario_path in fgroot_path.glob(f"{Path('AI', '*.xml')}"):
                scenarios.append(
                    types.AIScenario(
                        name=scenario_path.stem
                    )
                )

        return scenarios

    def resolve_info(self, ctx):
        return ctx.context['info']

    def resolve_directory_list(self, ctx, base_path):
        if base_path == "/" and platform.system() == 'Windows':
            dirs = get_windows_drives()
            return types.DirectoryList(base_path="/", directories=dirs)

        dirs = []
        files = []
        wd = Path(base_path)
        for obj in wd.glob("*"):
            if obj.is_dir():
                dirs.append(obj)
            else:
                files.append(obj)

        return types.DirectoryList(base_path=wd.absolute(), directories=dirs, files=files)

    def resolve_version(self, ctx):
        return ctx.context['version']

    def resolve_config(self, ctx):
        res = []

        config = ctx.context['config']
        lst = [x for x in vars(config) if not x.startswith('_')]

        for k in lst:
            res.append(types.ConfigEntry(
                key=k,
                value=getattr(config, k)
            ))

        return res


Schema = graphene.Schema(query=Query, mutation=Mutations)
