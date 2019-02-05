import logging
import os
import socket


MY_FQDN=socket.getfqdn()
MY_HOSTNAME=socket.gethostname()
MY_IP_ADDR=os.getenv('IP_ADDRESS', socket.gethostbyname(MY_FQDN))

# AGENT_SERVICE_TYPE="_fgo._tcp.local."
AGENT_SERVICE_TYPE="_http._tcp.local."
AGENT_SERVICE_NAME=f"FGO Agent ({MY_HOSTNAME})._http._tcp.local."
AGENT_PORT=5000


LOG_LEVEL=logging.DEBUG
