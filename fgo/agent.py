import logging
import socket
import sys
from time import sleep

from zeroconf import ServiceInfo, Zeroconf
from ipdb import set_trace
from . import constants

if __name__ == '__main__':
    logging.basicConfig(level=constants.LOG_LEVEL)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    desc = {'path': '/graphiql/', 'endpoint': '/graphql/'}

    info = ServiceInfo(constants.AGENT_SERVICE_TYPE,
                       constants.AGENT_SERVICE_NAME,
                       socket.inet_aton(constants.MY_IP_ADDR), constants.AGENT_PORT, 0, 0,
                       desc, f"{constants.MY_HOSTNAME}.local.")

    zeroconf = Zeroconf()
    print("Registration of a service, press Ctrl-C to exit...")
    zeroconf.register_service(info)
    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering...")
        zeroconf.unregister_service(info)
        zeroconf.close()
