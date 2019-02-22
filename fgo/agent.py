import threading
import logging
import atexit
import socket
import sys
from time import sleep

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
            'info': types.Info(status=types.Status.READY)
        }

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
        self._running = True
        app = self._create_app()

        if self._zeroconf_enabled:
            atexit.register(self._zeroconfUnregister)
            logging.info("Registration of a service, press Ctrl-C to exit...")
            self._mZeroconf.register_service(self._zeroconfInfo)
            self._zeroconfAnnounce()

        app.run()

    def _zeroconfAnnounce(self):
        if self._running:
            self.zeroconfThread = threading.Timer(self._zeroconf_announce_interval, self._zeroconfAnnounce, ())
            self.zeroconfThread.start()

    def _zeroconfUnregister(self):
        self._running = False
        logging.info("Unregistering service")
        self._mZeroconf.unregister_service(self._zeroconfInfo)
        if self._zeroconfThread.is_alive():
            logging.info("Waiting for background thread to terminate...")
            self._zeroconfThread.join()
        self._mZeroconf.close()

    def _create_app(self):
        app = Flask(__name__)

        app.add_url_rule(
            '/graphql',
            view_func=GraphQLView.as_view(
                'graphql',
                schema=schema.Schema,
                graphiql=True,
                get_context=lambda: {
                    'info': types.Info(status=types.Status.READY)
                }
            )
        )

        return app
