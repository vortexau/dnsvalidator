#!/usr/bin/env python3

import sys
import requests
from urllib.parse import urlparse
from argparse import ArgumentParser
from pathlib import Path

class InputHelper(object):
    @staticmethod
    def process_targets(parser, arg):
        if InputHelper.validate_url(arg):
            targets = InputHelper.process_url(parser, arg)
        else:
            filename = InputHelper.validate_filename(parser, arg)
            if filename:
                targets = InputHelper.process_file(filename)

        if len(targets) == 0:
            raise Exception("No target provided, or empty target list")

        return targets

    @staticmethod
    def validate_url(string):
        try:
            result = urlparse(string)
            # if there isn't a scheme, its probably not a URL we can reliably use
            return result.scheme
        except:
            # assume its a file and let the os decide
            return False

    @staticmethod
    def validate_filename(parser, arg):
        filename_arg = Path(arg)
        # sometimes we'll encounter ~ and ..
        filename_resolved = filename_arg.expanduser().resolve()
        if not filename_resolved.is_file():
            parser.error("The file %s does not exist or is not a valid URL!" % arg)
        else:
            return str(filename_resolved)

    @staticmethod
    def process_url(parser, arg):
        try:
            items = requests.get(arg)
        except:
            e = sys.exc_info()[0]
            parser.error(f"Tried to fetch {arg} but got {e} are you sure this is a valid URL?")

        if items.status_code != 200:
            parser.error(f"Tried to fetch {arg} but got HTTP {items.status_code} {items.reason}.")

        return items.text.split()

    @staticmethod
    def process_file(arg):
        with open(arg, 'r') as file:
            return [line.rstrip('\n') for line in file]

    @staticmethod
    def check_positive(parser, arg):
        i = int(arg)
        if i <= 0:
            raise parser.ArgumentTypeError(
                "%s is not a valid positive integer!" % arg)

        return arg

    @staticmethod
    def return_targets(arguments):
        targets = set()
        exclusions = set()
        if arguments.target:
            targets.add(arguments.target)
        else:
            for item in arguments.target_list:
                targets.add(item)

        if arguments.exclusion:
            exclusions.add(arguments.exclusion)
        elif arguments.exclusions_list:
            for item in arguments.exclusions_list:
                exclusions.add(item)

        # difference operation
        targets -= exclusions

        if len(targets) == 0:
            raise Exception(
                "No target remaining after removing all exceptions.")
        return targets

class InputParser(object):
    def __init__(self):
        self._parser = self.setup_parser()

    def parse(self, argv):
        return self._parser.parse_args(argv)

    @staticmethod
    def setup_parser():
        parser = ArgumentParser()

        targets = parser.add_mutually_exclusive_group(required=False)

        targets.add_argument(
            '-t', dest='target', required=False,
            help='Specify a target DNS server to try resolving.'
        )

        targets.add_argument(
            '-tL', dest='target_list', required=False,
            help='Specify a list of target DNS servers to try to resolve. '
                 'May be a file, or URL to listing',
            default="https://public-dns.info/nameservers.txt",
            type=lambda x: InputHelper.process_targets(parser, x)
        )

        # exclusions group
        exclusions = parser.add_mutually_exclusive_group()

        exclusions.add_argument(
            '-e', dest='exclusion', required=False,
            help='Specify an exclusion to remove from any target lists.'
        )

        exclusions.add_argument(
            '-eL', dest='exclusions_list', required=False,
            help='Specify a list of exclusions to avoid resolving. '
                 'May be a file or URL to listing',
            type=lambda x: InputHelper.process_targets(parser, x)
        )

        parser.add_argument('-o', '--output',
                            dest='output',
                            help='Destination file to write successful DNS validations to.')

        parser.add_argument(
            '-r', dest='rootdomain', required=False,
            help="Specify a root domain to compare to (default:",
            default="bet365.com"
        )

        parser.add_argument(
            '-q', dest='query', required=False,
            help="Specify a resolver query to use (default:dnsvalidator)",
            default="dnsvalidator"
        )

        parser.add_argument(
            '-threads', dest='threads', required=False,
            help="Specify the maximum number of threads to run (DEFAULT:5)",
            default=5,
            type=lambda x: InputHelper.check_positive(parser, x)
        )

        parser.add_argument(
            '-timeout', dest='timeout', required=False,
            help="Command timeout in seconds (DEFAULT:600)",
            default=600,
            type=lambda x: InputHelper.check_positive(parser, x)
        )

        parser.add_argument(
            '--no-color', dest='nocolor', action='store_true', default=False,
            help='If set then any foreground or background colours will be '
                 'stripped out.'
        )

        output_types = parser.add_mutually_exclusive_group()
        output_types.add_argument(
            '-v', '--verbose', dest='verbose', action='store_true', default=False,
            help='If set then verbose output will be displayed in the terminal.'
        )
        output_types.add_argument(
            '--silent', dest='silent', action='store_true', default=False,
            help='If set only findings will be displayed and banners '
                 'and other information will be redacted.'
        )

        return parser
