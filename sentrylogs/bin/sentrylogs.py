#!/usr/bin/env python
"""Standalone script for Sentry Logs"""
from __future__ import print_function
from locale import Error

import argparse
import yaml


try:
    from configparser import ConfigParser
except ImportError:  # Python 2.7
    from ConfigParser import ConfigParser  # pylint: disable=import-error


# Ignore warnings caused by ``sentrylogs.<...>`` imports
# pylint: disable=no-name-in-module

def get_command_line_args():
    """CLI command line arguments handling"""
    parser = argparse.ArgumentParser(description='Send logs to Sentry.')

    parser.add_argument('--configfile', '-c', default="sentrylogs.yaml",
                        help='A configuration file (.yaml) of some '
                             'Sentry integration')
    # parser.add_argument('--sentrydsn', '-s', default="",
    #                     help='The Sentry DSN string (overrides -c)')
    parser.add_argument('--daemonize', '-d', default=False,
                        action='store_const', const=True,
                        help='Run this script in background')

    return parser.parse_args()


def process_arguments(args):
    """Deal with arguments passed on the command line"""
    print(args)
    if args.configfile:
        print("Reading configfile %s" % args.configfile)
        config = parse_sentry_configuration(args.configfile)


    if args.daemonize:
        print('Running process in background')
        from ..daemonize import create_daemon
        create_daemon()
    print(config)
    return config


def parse_sentry_configuration(filename):
    """Parse Sentry DSN out of an application or Sentry configuration file"""

    with open(filename, "r") as stream:
        # no try..except because I want to send the error to the user is yaml is wrong
        yaml_config = yaml.safe_load(stream)
        # except yaml.YAMLError as exc:
            # raise(exc)
        if not yaml_config['sentry_dsn']:
            raise Error("mising sentry_dsn in configuration file")
        return yaml_config



def launch_log_parsers(config):
    """Run all log file parsers that send entries to Sentry"""
    for parser in config['parsers']:

        if not parser['type']:
            raise Error("parser needs a type: %s " % str(parser))
        if parser['type'] == "nginx":
            from ..parsers.nginx import Nginx
            Nginx().follow_tail()
        if parser['type'] == "zabbixserver":
            from ..parsers.zabbixserver import Zabbixserver
            Zabbixserver(parser['logfile']).follow_tail()

def main():
    """Main entry point of console script"""
    args = get_command_line_args()
    config = process_arguments(args)
    print('Start sending %s logs to Sentry')
    launch_log_parsers(config)


if __name__ == '__main__':
    main()
