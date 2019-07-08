#!/usr/bin/env python3

import dns.resolver
import re
import sys
import os
import signal

from .lib.core.input import InputParser, InputHelper
from .lib.core.output import OutputHelper, Level


def main():
    parser = InputParser()
    arguments = parser.parse(sys.argv[1:])

    output = OutputHelper(arguments)
    output.print_banner()
    baselines = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]

    valid_servers = []
    responses = {}

    # Perform resolution on each of the 'baselines'
    for baseline in baselines:
        output.terminal(Level.INFO, baseline, "resolving baseline")
        thisserver = {}

        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [baseline]
        goodanswer = resolver.query(arguments.rootdomain, 'A')

        for rr in goodanswer:
            thisserver["goodip"] = str(rr)

        try:
            nxdomanswer = resolver.query(arguments.query + arguments.rootdomain, 'A')
            thisserver["nxdomain"] = False
        except dns.resolver.NXDOMAIN:
            thisserver["nxdomain"] = True

        responses[baseline] = thisserver

    # loop through the list
    for server in InputHelper.return_targets(arguments):
        output.terminal(Level.VERBOSE, server, "starting check")
        server = server.strip()

        # todo: move into own method
        # Skip if not IPv4
        valid = re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", server)
        if not valid:
            output.terminal(Level.VERBOSE, server, "skipping as not IPv4")
            continue

        output.terminal(Level.INFO, server, "Checking...")

        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [server]

        try:
            answer = resolver.query(arguments.rootdomain, 'A')
        except:
            continue

        resolvematches = 0
        nxdommatches = 0

        for rr in answer:
            ans = str(rr)

        for goodresponse in responses:
            if responses[goodresponse]["goodip"] == ans:
                resolvematches += 1

        try:
            nxanswer = resolver.query('lkjlkjqqewdw.' + arguments.rootdomain, 'A')
        except dns.resolver.NXDOMAIN:
            gotnxdomain = True
        except:
            output.terminal(Level.ERROR, server, "Error when checking NXDOMAIN, passing")
            continue

        for goodresponse in responses:
            if responses[goodresponse]["nxdomain"] == gotnxdomain:
                nxdommatches += 1

        if resolvematches == 3 and nxdommatches == 3:
            output.terminal(Level.ACCEPTED, server, "provided valid response")
            valid_servers.append(server)
        else:
            output.terminal(Level.REJECTED, server, "invalid response received")

    # todo: move into proper class
    # write the content of the list to the disk for use
    if arguments.output:
        with open(arguments.output, "w+") as resolvers:
            resolvers.write(valid_servers)
            output.terminal(Level.INFO, 0,
                            "Update finished. Wrote {size} servers".format(size=len(valid_servers)))
        return
    output.terminal(Level.INFO, 0, "Finished. Discovered {size} servers".format(size=len(valid_servers)))

# Declare signal handler to immediately exit on KeyboardInterrupt
def signal_handler(signal, frame):
    os._exit(0)


signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    main()

