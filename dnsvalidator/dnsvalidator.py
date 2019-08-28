#!/usr/bin/env python3

import dns.resolver
import re
import sys
import os
import signal
import random
import string
import threading
import time
import concurrent.futures


from .lib.core.input import InputParser, InputHelper
from .lib.core.output import OutputHelper, Level


def rand():
    return ''.join(random.choice(string.ascii_lowercase) for i in range(10))


def resolve():
    pass


parser = InputParser()
arguments = parser.parse(sys.argv[1:])

output = OutputHelper(arguments)
output.print_banner()
baselines = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]


positivebaselines = ["bet365.com", "telegram.com"]
nxdomainchecks = ["facebook.com", "paypal.com", "google.com",
                  "bet365.com", "telegram.com", "wikileaks.com"]

goodip = ""
valid_servers = []
responses = {}


def resolve_address(server):
    # Skip if not IPv4
    valid = re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", server)
    if not valid:
        output.terminal(Level.VERBOSE, server, "skipping as not IPv4")
        return

    output.terminal(Level.INFO, server, "Checking...")

    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [server]

    # Try to resolve our positive baselines before going any further
    for nxdomaincheck in nxdomainchecks:
        # make sure random subdomains are NXDOMAIN
        try:
            positivehn = "{rand}.{domain}".format(
                rand=rand(),
                domain=nxdomaincheck
            )
            posanswer = resolver.query(positivehn, 'A')

            # nxdomain exception was not thrown, we got records when we shouldn't have.
            # Skip the server.
            output.terminal(Level.ERROR, server,
                            "DNS poisoning detected, passing")
            return
        except dns.resolver.NXDOMAIN:
            pass
        except Exception as e:
            output.terminal(Level.ERROR, server,
                            "Error when checking for DNS poisoning, passing")

    # Check for nxdomain on the rootdomain we're checking
    try:
        nxquery = "{rand}.{rootdomain}".format(
            rand=rand(),
            rootdomain=arguments.rootdomain
        )
        nxanswer = resolver.query(nxquery, 'A')
    except dns.resolver.NXDOMAIN:
        gotnxdomain = True
    except:
        output.terminal(Level.ERROR, server,
                        "Error when checking NXDOMAIN, passing")
        return

    resolvematches = 0
    nxdommatches = 0

    for goodresponse in responses:
        if responses[goodresponse]["goodip"] == goodip:
            resolvematches += 1
        if responses[goodresponse]["nxdomain"] == gotnxdomain:
            nxdommatches += 1

    if resolvematches == 3 and nxdommatches == 3:
        output.terminal(Level.ACCEPTED, server, "provided valid response")
        valid_servers.append(server)
    else:
        output.terminal(Level.REJECTED, server,
                        "invalid response received")


def main():
    global goodip
    # Perform resolution on each of the 'baselines'
    for baseline in baselines:
        output.terminal(Level.INFO, baseline, "resolving baseline")
        baseline_server = {}

        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [baseline]

        # Check our baseline against this server
        try:
            goodanswer = resolver.query(arguments.rootdomain, 'A')
        except dns.exception.Timeout:
            output.terminal(Level.ERROR, baseline,
                    "DNS Timeout for baseline server. Fatal")
            sys.exit(1)

        for rr in goodanswer:
            baseline_server["goodip"] = str(rr)
            goodip = str(rr)

        # checks for often poisoned domains
        baseline_server["pos"] = {}
        for positivebaseline in positivebaselines:
            posanswer = resolver.query(positivebaseline, 'A')
            for rr in posanswer:
                baseline_server["pos"][positivebaseline] = str(rr)

        try:
            nxdomanswer = resolver.query(
                arguments.query + arguments.rootdomain, 'A')
            baseline_server["nxdomain"] = False
        except dns.resolver.NXDOMAIN:
            baseline_server["nxdomain"] = True
        except dns.exception.Timeout:
            output.terminal(Level.ERROR, baseline,
                    "DNS Timeout for baseline server. Fatal")
            sys.exit(1)

        responses[baseline] = baseline_server

    # loop through the list
    with concurrent.futures.ThreadPoolExecutor(max_workers=int(arguments.threads)) as executor:
        thread = {executor.submit(
            resolve_address, server): server for server in InputHelper.return_targets(arguments)}
    output.terminal(Level.INFO, 0, "Finished. Discovered {size} servers".format(
        size=len(valid_servers)))

# Declare signal handler to immediately exit on KeyboardInterrupt


def signal_handler(signal, frame):
    os._exit(0)


signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    main()
