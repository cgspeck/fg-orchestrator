import argparse
import logging
import socket
import sys
import os

from fgo import agent

def create_parser():
    parser = argparse.ArgumentParser()
    commands = ['agent']
    parser.add_argument('command', choices=commands, default=commands[0])
    log_levels = ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL']
    parser.add_argument('--log-level', choices=log_levels, default=log_levels[0])
    parser.add_argument('--zeroconf-log-level', choices=log_levels, default=log_levels[0])
    parser.add_argument('--disable-zeroconf', action='store_true', default=False)
    parser.add_argument('--fqdn')
    parser.add_argument('--hostname')
    parser.add_argument('--ip')

    return parser

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level))
    settings = {}

    settings['zeroconf_enabled'] = not args.disable_zeroconf

    if settings['zeroconf_enabled']:
        logging.getLogger('zeroconf').setLevel(args.zeroconf_log_level)

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
            try:
                settings['my_ip'] = os.getenv('IP_ADDRESS', socket.gethostbyname(settings['my_fqdn']))
            except socket.gaierror:
                logging.error(f"""
                    Unable to determine your IP Address! This usually happens when your fqdn is misidentified.

                    Current settings: hostname={settings['my_hostname']} fqdn={settings['my_fqdn']}

                    Run with --help to discover switches that you can use to hostname, fqdn, ip address etc.

                    """)
                sys.exit(1)

        settings['agent_service_name'] = f"FGO Agent ({settings['my_hostname']})._http._tcp.local."
        logging.info(f"My Hostname: {settings['my_hostname']}, My FQDN: {settings['my_fqdn']}, My IP Address: {settings['my_ip']}")
    else:
        logging.info("Zeroconf is disabled")

    m_agent = agent.Agent(settings)

    # work-around this [unfixed bug](https://github.com/pallets/flask/issues/1246#issuecomment-115690934)
    if os.getenv('FLASK_ENV') == 'development':
        os.environ['PYTHONPATH'] = os.getcwd()

    m_agent.run()

