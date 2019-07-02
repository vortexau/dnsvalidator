#!/usr/bin/env python3

import requests
import dns.resolver
import re
import sys

from dnslistmaint.dnsvalidator.lib.core.input import InputParser, InputHelper
from dnslistmaint.dnsvalidator.lib.core.output import OutputHelper, Level


def main():
    parser = InputParser()
    arguments = parser.parse(sys.argv[1:])

    output = OutputHelper(arguments)

    output.print_banner()

    # todo: move this into CLI options or a config file
    baselines = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]

    dnsserverlist = "https://public-dns.info/nameservers.txt"
    updatedlist = "resolvers.txt"
    rootdomain = "unisa.edu.au"

    validservers = []

    # download the latest DNS list
    r = requests.get(dnsserverlist)
    data = r.text

    servers = data.split()

    responses = {}

    # Perform resolution on each of the 'baselines'
    for baseline in baselines:
        output.terminal(Level.INFO, baseline, "resolving baseline")
        thisserver = {}

        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [baseline]
        goodanswer = resolver.query(rootdomain, 'A')

        for rr in goodanswer:
            thisserver["goodip"] = str(rr)

        try:
            # todo: add random nonce to args
            nxdomanswer = resolver.query('lkjhuihuifr.' + rootdomain, 'A')
            thisserver["nxdomain"] = False
        except dns.resolver.NXDOMAIN:
            thisserver["nxdomain"] = True

        responses[baseline] = thisserver

    # loop through the list
    for server in servers:
        output.terminal(Level.VERBOSE, server, "starting check")
        server = server.strip()

        # Skip if not IPv4
        valid = re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", server)
        if not valid:
            output.terminal(Level.VERBOSE, server, "skipping as not IPv4")
            continue

        output.terminal(Level.INFO, server, "Checking...")

        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [server]

        try:
            answer = resolver.query(rootdomain, 'A')
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
            nxanswer = resolver.query('lkjlkjqqewdw.' + rootdomain, 'A')
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
            validservers.append(server)
        else:
            output.terminal(Level.REJECTED, server, "invalid response received")

    # todo: move into proper class
    # write the content of the list to the disk for use
    with open(updatedlist, "w+") as resolvers:
        resolvers.write(validservers)

    print("Update finished. Wrote {size} servers".format(size=len(validservers)))


if __name__ == "__main__":
    main()