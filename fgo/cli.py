#! /usr/bin/env python
from pathlib import Path
import argparse
import logging
import socket
import uuid
import sys
import os

from fgo.agent import agent
from fgo import util
from fgo.config import Config

log_levels = ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL']


def create_parser():
    parser_ = argparse.ArgumentParser()
    commands = ['agent', 'director', 'setup']
    parser_.add_argument('command', choices=commands, default=commands[0])
    parser_.add_argument('--log-level', choices=log_levels,
                         default=log_levels[0])
    parser_.add_argument('--zeroconf-log-level',
                         choices=log_levels, default=log_levels[0])
    parser_.add_argument('--disable-zeroconf',
                         action='store_true', default=False)
    parser_.add_argument('--fqdn')
    parser_.add_argument('--hostname')
    parser_.add_argument('--ip')
    parser_.add_argument('--fgfs-startup-time', type=int,
                         help="Amount of time in seconds to wait for FGFS to start up")

    return parser_


def main():
    parser = create_parser()
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level))
    basic_directories = {**util.check_folders()}

    config = Config.load(basic_directories['base_dir'])
    config.merge_dictionary(basic_directories)
    config.merge_dictionary(
        {'nav_db': Path(basic_directories['director_dir'], 'nav_db.sqlite')})
    config.merge_dictionary({'aircraft_db': Path(
        basic_directories['director_dir'], 'aircraft.sqlite')})

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
            config.my_ip = util.get_ip_address()

            if config.my_ip == '127.0.0.1':
                logging.error(f"""
                    Unable to determine your IP Address! This usually happens when your fqdn is misidentified.

                    Current settings: hostname={config.my_hostname} fqdn={config.my_fqdn}

                    Run with --help to discover switches that you can use to hostname, fqdn, ip address etc.

                    Or run with --disable-zeroconf to turn off 0conf.

                    """)
                sys.exit(1)

        config.agent_service_name = f"FGO Agent ({config.my_hostname})._http._tcp.local."
        logging.info(
            f"My Hostname: {config.my_hostname}, My FQDN: {config.my_fqdn}, My IP Address: {config.my_ip}")
    else:
        logging.info("Zeroconf is disabled")

    if args.command == 'agent':
        if args.fgfs_startup_time is not None:
            config.fgfs_startup_time = args.fgfs_startup_time

        m_agent = agent.Agent(config)

        # work-around this [unfixed bug](https://github.com/pallets/flask/issues/1246#issuecomment-115690934)
        if os.getenv('FLASK_ENV') == 'development':
            os.environ['PYTHONPATH'] = os.getcwd()

        m_agent.run()

    if args.command == 'director':
        from fgo.director.main import DirectorRunner
        DirectorRunner.run(config)

    if args.command == 'setup':
        from fgo.agent.setup import Setup
        Setup(config).run()


if __name__ == "__main__":
    main()
