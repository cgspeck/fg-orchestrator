import argparse
import logging
import socket
import os

from fgo import agent

def create_parser():
    parser = argparse.ArgumentParser()
    commands = ['agent']
    parser.add_argument('command', choices=commands, default=commands[0])
    log_levels = ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL']
    parser.add_argument('--log-level', choices=log_levels, default=log_levels[0])
    parser.add_argument('--zeroconf-log-level', choices=log_levels, default=log_levels[0])
    parser.add_argument('--zeroconf-announce-interval', type=int, default=60)
    parser.add_argument('--fqdn')
    parser.add_argument('--hostname')
    parser.add_argument('--ip')

    return parser

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level))
    logging.getLogger('zeroconf').setLevel(args.zeroconf_log_level)
    settings = {}

    if args.fqdn:
        settings['my_fqdn'] = args.fqdn
    else:
        logging.info('Finding your FQDN')
        settings['my_fqdn'] = socket.getfqdn()

    if args.hostname:
        settings['my_hostname'] = args.hostname
    else:
        logging.info('Finding your hostname')
        settings['my_hostname'] = socket.gethostname()

    if args.ip:
        settings['my_ip'] = args.ip
    else:
        logging.info('Finding your IP Address')
        settings['my_ip'] = os.getenv('IP_ADDRESS', socket.gethostbyname(settings['my_fqdn']))
    
    settings['zeroconf_announce_interval'] = args.zeroconf_announce_interval

    settings['agent_service_name'] = f"FGO Agent ({settings['my_hostname']})._http._tcp.local."
    logging.info(f"My Hostname: {settings['my_hostname']}, My FQDN: {settings['my_fqdn']}, My IP Address: {settings['my_ip']}")
    m_agent = agent.Agent(settings)
    m_agent.run()

