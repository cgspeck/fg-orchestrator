import pathlib
import platform
import string
import time

import graphene

from . import types

def get_windows_drives():
    from ctypes import windll
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(f"{letter}:")
        bitmask >>= 1

    return drives


class Query(graphene.ObjectType):
    info = graphene.Field(types.Info)
    directory_list = graphene.Field(types.DirectoryList, base_path=graphene.String(default_value="/"))

    def resolve_info(self, ctx):
        return ctx.context['info']

    def resolve_directory_list(self, ctx, base_path):
        if base_path == "/" and platform.system() == 'Windows':
            dirs = get_windows_drives()
            return types.DirectoryList(base_path="/", directories=dirs)

        dirs = []
        files = []
        wd = pathlib.Path(base_path)
        for obj in wd.glob("*"):
            if obj.is_dir():
                dirs.append(obj)
            else:
                files.append(obj)

        return types.DirectoryList(base_path=wd.absolute(), directories=dirs, files=files)


Schema = graphene.Schema(query=Query)
