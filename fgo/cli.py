import argparse
import logging
import socket
import uuid
import sys
import os

from pathlib import Path

from fgo import agent
from fgo import util
from fgo import config

from fgo.director.main import DirectorRunner

log_levels = ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL']

def create_parser():
    parser = argparse.ArgumentParser()
    commands = ['agent', 'director']
    parser.add_argument('command', choices=commands, default=commands[0])
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
    basic_directories = { **util.check_folders() }

    config = config.Config.load(basic_directories['base_dir'])
    config.merge_dictionary(basic_directories)

    if not config.uuid:
        config.uuid = str(uuid.uuid4())
        logging.info(f"Created ID {config.uuid} for this agent")
        config.save()

    config.zeroconf_enabled = not args.disable_zeroconf

    if config.zeroconf_enabled:
        logging.getLogger('zeroconf').setLevel(args.zeroconf_log_level)
        config.zeroconf_log_level = args.zeroconf_log_level

        if args.fqdn:
            config.my_fqdn = args.fqdn
        else:
            logging.info('Finding your FQDN')
            config.my_fqdn = socket.getfqdn()

        if args.hostname:
            config.my_hostname = args.hostname
        else:
            logging.info('Finding your hostname')
            config.my_hostname = socket.gethostname()

        if args.ip:
            config.my_ip = args.ip
        else:
            logging.info('Finding your IP Address')
            try:
                config.my_ip = os.getenv('IP_ADDRESS', socket.gethostbyname(config.my_fqdn))
            except socket.gaierror:
                logging.error(f"""
                    Unable to determine your IP Address! This usually happens when your fqdn is misidentified.

                    Current settings: hostname={config.my_hostname} fqdn={config.my_fqdn}

                    Run with --help to discover switches that you can use to hostname, fqdn, ip address etc.

                    Or run with --disable-zeroconf to turn off 0conf.

                    """)
                sys.exit(1)

            config.agent_service_name = f"FGO Agent ({config.my_hostname})._http._tcp.local."
            logging.info(f"My Hostname: {config.my_hostname}, My FQDN: {config.my_fqdn}, My IP Address: {config.my_ip}")
    else:
        logging.info("Zeroconf is disabled")

    if args.command == 'agent':
        m_agent = agent.Agent(config)

        # work-around this [unfixed bug](https://github.com/pallets/flask/issues/1246#issuecomment-115690934)
        if os.getenv('FLASK_ENV') == 'development':
            os.environ['PYTHONPATH'] = os.getcwd()

        m_agent.run()

    if args.command == 'director':
        dr = DirectorRunner()
        dr.run()
