from pathlib import Path
import threading
import platform
import logging
import atexit
import socket
import time
import sys

from flask import Flask
import graphene
from flask_graphql import GraphQLView

from zeroconf import ServiceInfo, Zeroconf

from . import constants
from .gql import schema
from .gql import types

class Agent():
    def __init__(self, settings):
        self._settings = settings

        self._uuid = settings['uuid']

        self._context_lock = threading.Lock()
        self._check_status_thread = threading.Thread()

        self._context = {
            'running': False,
            'info': types.Info(status=types.Status.SCANNING),
            'context_lock': self._context_lock,
            'settings': self._settings
        }

        self._zeroconf_enabled = settings['zeroconf_enabled']

        if self._zeroconf_enabled:
            self._mZeroconf = Zeroconf()
            self._zeroconfDesc = {'path': '/graphiql/', 'endpoint': '/graphql/'}
            self._zeroconfInfo = ServiceInfo(
                constants.AGENT_SERVICE_TYPE,
                settings['agent_service_name'],
                socket.inet_aton(settings['my_ip']), constants.AGENT_PORT, 0, 0,
                self._zeroconfDesc, f"{settings['my_hostname']}.local."
            )


    def run(self):
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
                    next_errors = self._check_environment(current_os)

                    if len(next_errors) == 0:
                        next_aircraft = self._scan_for_aircraft()
                        next_status = types.Status.READY
                    else:
                        next_status = types.Status.ERROR

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

    def _check_environment(self, os):
        error_list = []
        # check fgfs location - executable
        error_list += filter(None, [self._check_path_set_and_exists('fgfs')])
        # TODO: on linux, use `which` to find location of fgfs
        #       if success reset error_list

        # check if aircraft path set - directory
        error_list += filter(None, [self._check_path_set_and_exists('aircraft')])

        # check if terrasync path set - directory
        error_list += filter(None, [self._check_path_set_and_exists('terrasync')])

        return error_list

    def _check_path_set_and_exists(self, selector):
        key = f"{selector}_path"
        if not self._settings.get(key):
            return types.Error(code=types.ErrorCode[f'{selector.upper()}_PATH_NOT_SET'])

        value = self._settings[key]
        if not Path(value).exists():
            return types.Error(
                code=types.ErrorCode[f'{selector.upper()}_PATH_NOT_EXIST'],
                description=f"Could not locate path '{value}'"
            )

    def _shutdown(self):
        with self._context_lock:
            self._context['running'] = False

        print(f"shutdown running status: {self._context['running']}")
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
