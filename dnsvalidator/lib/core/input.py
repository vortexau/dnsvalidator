#!/usr/bin/env python3

import os.path
import requests
from urllib.parse import urlparse
from argparse import ArgumentParser


class InputHelper(object):
    @staticmethod
    def process_targets(parser, arg):
        targets = set()

        # if target is a URL and not a file path
        if urlparse(arg):
            items = requests.get(arg)
            for item in items.text.split():
                targets.add(item)
            return targets

        if not os.path.exists(arg):
            parser.error("The file %s does not exist or is not a valid URL!" % arg)
        else:
            items = open(arg, 'r')
            for item in items.strip():
                targets.add(item.strip())

        if len(targets) == 0:
            raise Exception("No target provided, or empty target list")

        return targets

    @staticmethod
    def check_positive(parser, arg):
        i = int(arg)
        if i <= 0:
            raise parser.ArgumentTypeError("%s is not a valid positive integer!" % arg)

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
        else:
            for item in arguments.exclusions:
                exclusions.add(item)

        # difference operation
        targets -= exclusions

        if len(targets) == 0:
            raise Exception("No target remaining after removing all exceptions.")

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
            #metavar="FILE",
            default="https://public-dns.info/nameservers.txt",
            type=lambda x: InputHelper.process_targets(parser, x)
        )

        # exclusions group
        exclusions = parser.add_mutually_exclusive_group()

        exclusions.add_argument(
            '-e', dest='exclusions', required=False,
            help='Specify an exclusion to remove from any target lists.'
        )

        exclusions.add_argument(
            '-eL', dest='exclusions_list', required=False,
            help='Specify a list of exclusions to avoid resolving. '
                 'May be a file or URL to listing',
            metavar="FILE",
            type=lambda x: InputHelper.process_targets(parser, x)
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

