from pathlib import Path
import subprocess
import threading
import platform
import logging
import atexit
import socket
import time
import sys
import re

from flask import Flask
import graphene
from flask_graphql import GraphQLView

from zeroconf import ServiceInfo, Zeroconf

import svn.remote
import svn.local

from . import constants
from .gql import schema
from .gql import types

class Agent():
    def __init__(self, config):
        logging.info("Initialising agent")
        self._config = config

        self._uuid = config.uuid

        self._context_lock = threading.Lock()
        self._check_status_thread = threading.Thread()

        self._context = {
            'running': False,
            'info': types.Info(status=types.Status.SCANNING),
            'context_lock': self._context_lock,
            'config': self._config,
            'version': None,
            'state_meta': None,
            'fg_process': None
        }

        self._zeroconf_enabled = config.zeroconf_enabled

        if self._zeroconf_enabled:
            self._mZeroconf = Zeroconf()
            self._zeroconfDesc = {'path': '/graphiql/', 'endpoint': '/graphql/'}
            self._zeroconfInfo = ServiceInfo(
                constants.AGENT_SERVICE_TYPE,
                config.agent_service_name,
                socket.inet_aton(config.my_ip), constants.AGENT_PORT, 0, 0,
                self._zeroconfDesc, f"{config.my_hostname}.local."
            )


    def run(self):
        logging.info("Starting agent")
        with self._context_lock:
            self._context['running'] = True

        app = self._create_app()

        atexit.register(self._shutdown)

        if self._zeroconf_enabled:
            logging.info("Registration of a service, press Ctrl-C to exit...")
            self._mZeroconf.register_service(self._zeroconfInfo)

        self._check_status_thread = threading.Timer(10, self._check_status, ())
        self._check_status_thread.start()
        app.run()


    def _check_status(self):
        # state machine that actually manages things
        with self._context_lock:
            if self._context['running']:

                current_status = self._context['info'].status
                current_errors = self._context['info'].errors
                current_aircraft = self._context['info'].aircraft
                current_os = self._context['info'].os
                current_os_string = self._context['info'].os_string
                next_aircraft = None
                next_status = None
                next_errors = None

                next_os = current_os
                next_os_string = current_os_string
                next_status = current_status
                next_aircraft = current_aircraft
                next_errors = current_errors

                if current_status == types.Status.SCANNING:
                    next_os, next_os_string = self._discover_os()
                    next_errors, memo = self._check_environment(next_os, self._config)

                    if len(next_errors) == 0:
                        self._context = { **self._context, **memo }
                        next_status = types.Status.READY
                    else:
                        next_status = types.Status.ERROR

                elif current_status == types.Status.INSTALLING_AIRCRAFT:
                    #       the giant state machine will:
                    #           - check if the aircraft has already been cloned
                    #               - do an svn up on it if it already exists
                    #               - or a fresh check out
                    #               - progress state to READY or ERROR when done
                    #
                    svn_name = self._context['state_meta']
                    logging.info(f"Installing or Updating aircraft '{svn_name}'")
                    expected_aircraft_path = Path(
                        self._context['config'].aircraft_path,
                        svn_name
                    )
                    logging.info(f"Checking if {expected_aircraft_path} exists")

                    if expected_aircraft_path.exists():
                        lc = svn.local.LocalClient(f"{expected_aircraft_path}")
                        try:
                            lc.update()
                            next_status = types.Status.READY
                            logging.info("Done updating aircraft")
                        except svn.exception.SvnException:
                            next_status = types.Status.ERROR
                            next_errors = [types.Error(
                                code=types.ErrorCode.AIRCRAFT_NOT_IN_VERSION_CONTROL,
                                description=f"Aircraft {svn_name} is not under version control. Delete the folder {expected_aircraft_path} and try reinstalling."
                            )]
                    else:
                        upstream_repo_url = f"{self._context['aircraft_svn_base_url']}/{svn_name}"
                        logging.info(f"Cloaning from {upstream_repo_url}")
                        rc = svn.remote.RemoteClient(upstream_repo_url)
                        rc.checkout(f"{expected_aircraft_path}")
                        logging.info("Done cloning aircraft")
                        next_status = types.Status.READY
                elif current_status == types.Status.FGFS_STARTING:
                    # assemble arguments
                    arg_list = self._assemble_fg_args()
                    self._context['fg_process'] = subprocess.Popen(
                        arg_list
                    )

                elif current_status == types.Status.ERROR:
                    pass
                elif current_status == types.Status.READY:
                    pass

                self._context['info'] = types.Info(
                    status=next_status,
                    os=next_os,
                    os_string = next_os_string,
                    timestamp=int(time.time()),
                    errors=next_errors,
                    aircraft=next_aircraft,
                    uuid=self._uuid
                )

                self._check_status_thread = threading.Timer(10, self._check_status, ())
                self._check_status_thread.start()

    def _assemble_fg_args(self):
        return [
            self._context['config'].fgfs_path
        ]

    def _scan_for_aircraft(self):
        return []

    def _discover_os(self):
        os_string = platform.system()

        res = types.OS.UNKNOWN

        if os_string == 'Windows':
            res = types.OS.WINDOWS
        elif os_string == 'Linux':
            res = types.OS.LINUX
        elif os_string == 'Darwin':
            res = types.OS.DARWIN

        return res, os_string

    def _windows_find_fgfs(self):
        logging.error("_windows_find_fgfs not implemented!")
        return None

    def _linux_find_fgfs(self):
        res = None
        memo = subprocess.run(
            ["which", "fgfs"],
            capture_output=True,
            text=True
        )
        if memo.returncode == 0:
            res = memo.stdout.strip()

        return res

    def _darwin_find_fgfs(self):
        return self._linux_find_fgfs()

    def _check_environment(self, os, config):
        error_list = []
        memo = {}
        # check fgfs location - executable
        fgfs_error = self._check_path_set_and_exists('fgfs')

        if fgfs_error is not None:
            fgfs_find_result = getattr(self, f"_{os.lower_name}_find_fgfs")()

            if fgfs_find_result:
                logging.info(f"Found fgfs at {fgfs_find_result}!")
                config.fgfs_path = fgfs_find_result
                config.save()
            else:
                error_list.append(fgfs_error)

        fgroot_error = self._check_path_set_and_exists('fgroot')

        if fgroot_error is not None and fgfs_error is None:
            proposed_path = None
            # Linux: ~/.fgfs
            # Windows: at ../data
            if os == types.OS.LINUX:
                proposed_path = Path(Path.home(), ".fgfs")
            elif os == types.OS.WINDOWS:
                proposed_path = Path(config.fgfs_path, "../data")

            if proposed_path and proposed_path.exists():
                logging.info(f"Found fgroot at {proposed_path}!")
                config.fgroot_path = proposed_path
                config.save()
            else:
                error_list.append(fgroot_error)

        # check if aircraft path set - directory
        aircraft_path_error = self._check_path_set_and_exists('aircraft')
        # if we have a fgroot_path, see if there is an aircraft folder in it

        if aircraft_path_error is not None and fgroot_error is None:
            fgroot_path = config.fgroot_path
            proposed_path = Path(fgroot_path, 'aircraft')
            if proposed_path.exists():
                logging.info(f"Found aircraft at {proposed_path}!")
                config.aircraft_path = proposed_path
                config.save()
            else:
                error_list.append(aircraft_path_error)

        # check if terrasync path set - directory
        error_list += filter(None, [self._check_path_set_and_exists('terrasync', allow_none=True)])

        if len(error_list) > 0:
            return error_list, memo

        fgfs_path = config.fgfs_path
        fgroot_path = config.fgroot_path
        version_result = subprocess.run(
            [f"{fgfs_path}", f"--fg-root={fgroot_path}", '--version'],
            capture_output=True,
            text=True
        )
        # parse result to grab the version
        #
        #   In [20]: res.stdout
        #   Out[20]: 'FlightGear version: 2018.2.2\nRevision: b000e132bba859
        #
        #       e.g. version is 2018.2.2
        #       for downloading aircraft, just care about major.minor, i.e. 2018.2
        #       split into constitute parts
        #
        match = re.search(r'^.*FlightGear version: (.*)\n', version_result.stdout)
        version_frags = [int(x) for x in match[1].split('.')]
        version_obj = types.Version(major=version_frags[0], minor=version_frags[1], patch=version_frags[2])
        memo['version'] = version_obj
        memo['aircraft_svn_base_url'] = f"https://svn.code.sf.net/p/flightgear/fgaddon/branches/release-{version_obj.major}.{version_obj.minor}/Aircraft"

        return error_list, memo

    def _check_path_set_and_exists(self, selector, allow_none=False):
        key = f"{selector}_path"
        value = getattr(self._config, key, None)
        logging.debug(f"_check_path_set_and_exists key={key} value={value} allow_none={allow_none}")

        if allow_none and value is None:
            return None

        if value is None:
            return types.Error(code=types.ErrorCode[f'{selector.upper()}_PATH_NOT_SET'])

        if not Path(value).exists():
            return types.Error(
                code=types.ErrorCode[f'{selector.upper()}_PATH_NOT_EXIST'],
                description=f"Could not locate path '{value}'"
            )

        return None

    def _shutdown(self):
        with self._context_lock:
            self._context['running'] = False

        if self._check_status_thread.is_alive():
            logging.info("Waiting to status checker to quit...")
            self._check_status_thread.cancel()

        if self._zeroconf_enabled:
            logging.info("Unregistering service")
            self._mZeroconf.unregister_service(self._zeroconfInfo)
            self._mZeroconf.close()

    def _create_app(self):
        app = Flask(__name__)

        app.add_url_rule(
            '/graphql',
            view_func=GraphQLView.as_view(
                'graphql',
                schema=schema.Schema,
                graphiql=True,
                get_context=lambda: self._context
            )
        )

        return app
