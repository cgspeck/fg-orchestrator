from pathlib import Path
import platform
import hashlib
import logging
import filecmp
import os

from fgo.gql import types


def check_protocol_file(dst: Path) -> bool:
    src = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'data',
        'fgo.xml'
    )
    return filecmp.cmp(src, dst)


def discover_os():
    os_string = platform.system()

    res = types.OS.UNKNOWN

    if os_string == 'Windows':
        res = types.OS.WINDOWS
    elif os_string == 'Linux':
        res = types.OS.LINUX
    elif os_string == 'Darwin':
        res = types.OS.DARWIN

    return res, os_string


def windows_find_fgroot():
    install_loc = locate_fgfs_in_windows_registry()

    if install_loc:
        return f"{install_loc}data\\"


def locate_fgfs_in_windows_registry():
    import winreg
    import re
    logging.info("Scanning windows registry")
    uninstall_keys = []
    i = 0
    cont_enum = True
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall") as handle:
        logging.info("Building list of installed applications")
        while cont_enum:
            try:
                uninstall_keys.append(winreg.EnumKey(handle, i))
                i += 1
            except OSError:
                cont_enum = False

    install_location = None
    found_fgfs = False

    logging.info(f"{len(uninstall_keys)} applications found")

    for u_key in uninstall_keys:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{u_key}") as handle:
            cont_enum = True
            i = 0
            while cont_enum:
                try:
                    value_name, value_data, _ = winreg.EnumValue(handle, i)

                    if value_name == 'DisplayName':
                        found_fgfs = bool(
                            re.search(r'^FlightGear.*', value_data))
                    elif value_name == 'InstallLocation':
                        install_location = value_data

                    i += 1
                except OSError:
                    cont_enum = False

        if found_fgfs and install_location:
            logging.info("Found FGFS in windows registry!")
            logging.info(f"FGFS install path={install_location}")
            break

    return install_location


def linux_find_fgroot():
    return '/usr/share/games/flightgear/'


def darwin_find_fgroot():
    return '/Applications/FlightGear.app/Contents/Resources/data/'
