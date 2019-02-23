import threading
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
        self._context = {
            'running': False,
            'info': types.Info(status=types.Status.READY)
        }

        self._context_lock = threading.Lock()
        self._check_status_thread = threading.Thread()

        self._zeroconf_enabled = settings['zeroconf_enabled']

        if self._zeroconf_enabled:
            self._zeroconfThread = threading.Thread()
            self._mZeroconf = Zeroconf()
            self._zeroconfDesc = {'path': '/graphiql/', 'endpoint': '/graphql/'}
            self._zeroconf_announce_interval = settings['zeroconf_announce_interval']
            self._zeroconfInfo = ServiceInfo(constants.AGENT_SERVICE_TYPE,
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
            self._zeroconfAnnounce()

        self._check_status_thread = threading.Timer(10, self._check_status, ())
        self._check_status_thread.start()
        app.run()


    def _check_status(self):
        # state machine that actually manages things
        print('check state')
        with self._context_lock:
            print(f"check state running status: {self._context['running']}")
            if self._context['running']:
                # self._context['info'].timestamp = int(time.time())
                self._context['info'] = types.Info(
                    status=types.Status.READY,
                    timestamp=int(time.time())
                )
                print(self._context['info'].timestamp)

                self._check_status_thread = threading.Timer(10, self._check_status, ())
                self._check_status_thread.start()

    def _zeroconfAnnounce(self):
        print('0conf announce')
        with self._context_lock:
            print(f"0conf running status: {self._context['running']}")
            if self._context['running']:
                self.zeroconfThread = threading.Timer(self._zeroconf_announce_interval, self._zeroconfAnnounce, ())
                self.zeroconfThread.start()

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
            if self._zeroconfThread.is_alive():
                logging.info("Waiting for background thread to terminate...")
                self._zeroconfThread.cancel()
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
