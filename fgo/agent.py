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

ZERO_CONF_INTERVAL = 60
zeroconfThread = threading.Thread()
mZeroconf = Zeroconf()
zeroconfDesc = {'path': '/graphiql/', 'endpoint': '/graphql/'}
zeroconfInfo = ServiceInfo(constants.AGENT_SERVICE_TYPE,
                    constants.AGENT_SERVICE_NAME,
                    socket.inet_aton(constants.MY_IP_ADDR), constants.AGENT_PORT, 0, 0,
                    zeroconfDesc, f"{constants.MY_HOSTNAME}.local.")

def zeroconfAnnounce():
    global zeroconfThread
    zeroconfThread = threading.Timer(ZERO_CONF_INTERVAL, zeroconfAnnounce, ())
    zeroconfThread.start()

def zeroconfUnregister():
    global zeroconfThread
    global mZeroconf
    global zeroconfInfo
    print("Unregistering service")
    mZeroconf.unregister_service(zeroconfInfo)
    mZeroconf.close()

class Query(graphene.ObjectType):
    hello = graphene.String(description='A typical hello world')

    def resolve_hello(self, info):
        return 'World'

def create_app():
    logging.basicConfig(level=constants.LOG_LEVEL)
    app = Flask(__name__)

    atexit.register(zeroconfUnregister)
    print("Registration of a service, press Ctrl-C to exit...")
    mZeroconf.register_service(zeroconfInfo)
    schema = graphene.Schema(query=Query)

    app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))
    # Optional, for adding batch query support (used in Apollo-Client)
    # app.add_url_rule('/graphql/batch', view_func=GraphQLView.as_view('graphql', schema=schema, batch=True))

    return app

if __name__ == '__main__':
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    app = create_app()
    app.run()



