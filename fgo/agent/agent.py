from pathlib import Path
import subprocess
import threading
import textwrap
import datetime
import logging
import atexit
import socket
import time
import re
import os

from flask import Flask
from flask_graphql import GraphQLView

from zeroconf import ServiceInfo, Zeroconf

import svn.remote
import svn.local
from svn.exception import SvnException

from fgo import constants
from fgo.gql import schema
from fgo.gql import types

from fgo.agent import util
from fgo.agent import agent_errors


class Agent:
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
            self._m_zeroconf = Zeroconf()
            self._zeroconf_desc = {
                'path': '/graphiql/',
                'endpoint': '/graphql/',
                'uuid': config.uuid,
                'ipaddress': config.my_ip
            }
            self._zeroconf_info = ServiceInfo(
                constants.AGENT_SERVICE_TYPE,
                config.agent_service_name,
                socket.inet_aton(config.my_ip), constants.AGENT_PORT, 0, 0,
                self._zeroconf_desc, f"{config.my_hostname}.local."
            )

    def run(self):
        logging.info("Starting agent")
        with self._context_lock:
            self._context['running'] = True

        flask_app = self._create_app()

        atexit.register(self._shutdown)

        if self._zeroconf_enabled:
            logging.info("Registration of a service, press Ctrl-C to exit...")
            self._m_zeroconf.register_service(self._zeroconf_info)

        self._check_status_thread = threading.Timer(10, self._check_status)
        self._check_status_thread.start()
        flask_app.run(host='0.0.0.0')

    def _check_status(self):
        # state machine that actually manages things
        with self._context_lock:
            if self._context['running']:
                current_status = self._context['info'].status
                current_errors = self._context['info'].errors
                current_aircraft = self._context['info'].aircraft
                current_os = self._context['info'].os
                current_os_string = self._context['info'].os_string
                current_fg_process = self._context['fg_process']

                next_os = current_os
                next_os_string = current_os_string
                next_status = current_status
                next_aircraft = current_aircraft
                next_errors = current_errors
                next_fg_process = current_fg_process

                config = self._context['config']

                if current_status == types.Status.SCANNING:
                    next_os, next_os_string = util.discover_os()
                    next_errors, memo = self._check_environment(
                        next_os, self._config)
                    self._context = {**self._context, **memo}

                    if len(next_errors) == 0:
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
                    logging.info(
                        f"Installing or Updating aircraft '{svn_name}'")
                    expected_aircraft_path = Path(
                        config.aircraft_path,
                        svn_name
                    )
                    logging.info(
                        f"Checking if {expected_aircraft_path} exists")

                    if expected_aircraft_path.exists():
                        logging.info("Updating existing aircraft")
                        lc = svn.local.LocalClient(f"{expected_aircraft_path}")
                        try:
                            lc.update()
                            next_status = types.Status.READY
                            logging.info("Done updating aircraft")
                        except SvnException:
                            next_status = types.Status.ERROR
                            next_errors = [types.Error(
                                code=types.ErrorCode.AIRCRAFT_NOT_IN_VERSION_CONTROL,
                                description=f"Aircraft {svn_name} is not under version control. Delete the folder {expected_aircraft_path} and try reinstalling."
                            )]
                    else:
                        upstream_repo_url = f"{self._context['aircraft_svn_base_url']}/{svn_name}"
                        logging.info(f"Cloning from {upstream_repo_url}")
                        rc = svn.remote.RemoteClient(upstream_repo_url)
                        try:
                            rc.checkout(f"{expected_aircraft_path}")
                        except svn.exception.SvnException as e:
                            logging.error(
                                f"Unable to clone aircraft '{svn_name}': {e}")
                            next_status = types.Status.ERROR
                            next_errors = [
                                types.Error(
                                    code=types.ErrorCode.AIRCRAFT_INSTALL_FAILED,
                                    description=f"{e}"
                                )
                            ]
                        except FileNotFoundError:
                            next_status = types.Status.ERROR
                            next_errors = [types.Error(
                                code=types.ErrorCode.SVN_NOT_INSTALLED,
                                description=f"Aircraft {svn_name} could not be installed. Check that you have svn installed."
                            )]
                        else:
                            logging.info("Done cloning aircraft")
                            next_status = types.Status.READY

                elif current_status == types.Status.FGFS_START_REQUESTED:
                    # assemble arguments
                    env = config.assemble_fgfs_env_vars()
                    env_str = [f'{k}={v}' for k, v in env[0].items()]
                    env_str = ' '.join(env_str)
                    args = [f"{config.fgfs_path}"] + \
                        self._context['state_meta']
                    logging.info(f"***** About to trigger FGFS *****")
                    logging.info("")
                    logging.info(f"     env: {env_str}")
                    logging.info(f"     cmd: {' '.join(args)}")
                    logging.info("")
                    logging.info(f"*********************************")
                    next_fg_process = subprocess.Popen(
                        args,
                        text=True,
                        env=env[1]
                    )
                    self._context['state_meta'] = datetime.datetime.now()
                    next_status = types.Status.FGFS_STARTING

                elif current_status == types.Status.FGFS_STARTING:
                    # TODO: implement actual check whether FGFS is up
                    if (datetime.datetime.now() - self._context['state_meta']).seconds >= config.fgfs_startup_time:
                        next_status = types.Status.FGFS_RUNNING

                elif current_status == types.Status.FGFS_RUNNING:
                    # check that fgfs is still up, set error if it crashes
                    logging.debug(f"current_fg_process = {current_fg_process}")
                    logging.debug(
                        f"current_fg_process.poll() = {current_fg_process.poll()}")

                    if current_fg_process.poll() is not None:
                        rc = current_fg_process.returncode
                        if rc == 0:
                            next_status = types.Status.READY
                        else:
                            msg = f"Abnormal FlightGear termination with returncode {rc}!"
                            logging.error(msg)
                            next_errors = [
                                types.Error(
                                    code=types.ErrorCode.FGFS_ABNORMAL_EXIT,
                                    description=msg
                                )
                            ]
                            next_status = types.Status.ERROR

                        next_fg_process = None

                elif current_status == types.Status.FGFS_STOP_REQUESTED:
                    self._context['fg_process'].terminate()
                    self._context['fg_process'] = None
                    next_status = types.Status.READY
                elif current_status == types.Status.ERROR:
                    pass
                elif current_status == types.Status.READY:
                    pass

                self._context['info'] = types.Info(
                    status=next_status,
                    os=next_os,
                    os_string=next_os_string,
                    timestamp=int(time.time()),
                    errors=next_errors,
                    aircraft=next_aircraft,
                    uuid=self._uuid
                )
                self._context['fg_process'] = next_fg_process

                self._check_status_thread = threading.Timer(
                    10, self._check_status)
                self._check_status_thread.start()

    def _assemble_fg_args(self):
        return [
            self._context['config'].fgfs_path
        ]

    @staticmethod
    def windows_find_fgfs():
        install_loc = util.locate_fgfs_in_windows_registry()

        if install_loc:
            return f"{install_loc}bin\\fgfs.exe"

    @staticmethod
    def linux_find_fgfs():
        res = None
        memo = subprocess.run(
            ["which", "fgfs"],
            capture_output=True,
            text=True
        )
        if memo.returncode == 0:
            res = memo.stdout.strip()

        return res

    @staticmethod
    def darwin_find_fgfs():
        return Agent.linux_find_fgfs()

    @staticmethod
    def windows_find_fghome():
        return Path(
            os.environ['USERPROFILE'],
            'Documents\\FlightGear'
        )

    @staticmethod
    def linux_find_fghome():
        return Path(Path.home(), ".fgfs")

    @staticmethod
    def darwin_find_fghome():
        return Path(Path.home(), "Library/Application Support/FlightGear")

    def _check_environment(self, os_, config):
        error_list = []
        memo = {}
        # check fgfs location - executable
        fgfs_error = self._check_path_set_and_exists('fgfs')
        os_name_lower = os_.lower_name

        if fgfs_error is not None:
            fgfs_find_result = getattr(self, f"{os_name_lower}_find_fgfs")()

            if fgfs_find_result:
                logging.info(f"Found fgfs at {fgfs_find_result}!")
                config.fgfs_path = fgfs_find_result
                config.save()
                fgfs_error = None

        error_list += filter(None, [fgfs_error])

        fgroot_error = self._check_path_set_and_exists('fgroot')

        # http://www.flightgear.org/Docs/getstart/getstartch3.html
        # see http://wiki.flightgear.org/$FG_ROOT
        if fgroot_error is not None and fgfs_error is None:
            proposed_path = getattr(util, f"{os_name_lower}_find_fgroot")()

            if proposed_path is not None:
                path_obj = Path(proposed_path)
                if path_obj.exists():
                    logging.info(f"Found fgroot at {path_obj}!")
                    config.fgroot_path = path_obj
                    config.save()
                    fgroot_error = None

        error_list += filter(None, [fgroot_error])

        protocol_file_error = None

        if fgroot_error is None:
            # check for the custom protocol file
            expected_protocol_file = Path(
                config.fgroot_path,
                "Protocol",
                "fgo.xml"
            )

            if not expected_protocol_file.exists():
                protocol_file_error = agent_errors.ProtocolFileMissingError(
                    expected_protocol_file)
            elif not util.check_protocol_file(expected_protocol_file):
                protocol_file_error = agent_errors.ProtocolFileHashMismatch(
                    expected_protocol_file
                )

        error_list += filter(None, [protocol_file_error])

        fghome_error = self._check_path_set_and_exists('fghome')

        if fghome_error is not None:
            # http://wiki.flightgear.org/$FG_HOME
            path_obj = getattr(self, f"{os_name_lower}_find_fghome")()

            if path_obj.exists():
                logging.info(f"Found fghome at {path_obj}!")
                config.fghome_path = path_obj
                config.save()
                fghome_error = None

        error_list += filter(None, [fghome_error])

        # check if aircraft path set - directory
        aircraft_path_error = self._check_path_set_and_exists('aircraft')
        # if we have a fghome_error, see if there is an aircraft folder in it

        if aircraft_path_error is not None and fghome_error is None:
            proposed_path = Path(config.fghome_path, 'Aircraft')
            if proposed_path.exists():
                logging.info(f"Found aircraft at {proposed_path}!")
                config.aircraft_path = proposed_path
                config.save()
                aircraft_path_error = None

        error_list += filter(None, [aircraft_path_error])
        error_list += filter(None,
                             [self._check_path_set_and_exists('terrasync', allow_none=True)])

        if len(error_list) > 0:
            return error_list, memo

        fgfs_path = config.fgfs_path

        try:
            logging.info("Starting FGFS to find version")
            version_result = subprocess.run(
                [f"{fgfs_path}", '--version'],
                capture_output=True,
                text=True,
                timeout=3,
                env=config.assemble_fgfs_env_vars()[1]
            )
        except (OSError, subprocess.TimeoutExpired) as e:
            error_list.append(
                types.Error(
                    code=types.ErrorCode.FG_VERSION_CHECK_FAILED,
                    description=textwrap.dedent(f"""\
                        {e}

                        Failed to retrieve version. Check paths.
                        FGFS_PATH ({config.fgfs_path}) should point to the FGFS executable
                        FG_ROOT ({config.fgroot_path}) should point to read-only FlightGear files.
                        FG_HOME ({config.fghome_path}) should point to read/write user-specific FlightGear data
                    """)
                )
            )
        else:
            logging.debug(f"Version result: {version_result}")
            match = re.search(r'^.*FlightGear version: (.*)\n',
                              version_result.stdout)
            version_frags = [int(x) for x in match[1].split('.')]
            version_obj = types.Version(
                major=version_frags[0], minor=version_frags[1], patch=version_frags[2])
            memo['version'] = version_obj
            memo[
                'aircraft_svn_base_url'] = f"https://svn.code.sf.net/p/flightgear/fgaddon/branches/release-{version_obj.major}.{version_obj.minor}/Aircraft"

        return error_list, memo

    def _check_path_set_and_exists(self, selector, allow_none=False):
        key = f"{selector}_path"
        value = getattr(self._config, key, None)
        logging.debug(
            f"_check_path_set_and_exists key={key} value={value} allow_none={allow_none}")

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
            self._check_status_thread.join(5)

        if self._zeroconf_enabled:
            logging.info("Unregistering service")
            self._m_zeroconf.unregister_service(self._zeroconf_info)
            self._m_zeroconf.close()

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
