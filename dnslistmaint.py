#!/usr/bin/env python3

import requests
import dns.resolver
import re

goodservers = ["1.1.1.1","8.8.8.8","9.9.9.9"]

dnsserverlist = "https://public-dns.info/nameservers.txt"
updatedlist = "resolvers.txt"
rootdomain = "unisa.edu.au"

validservers = []

# download the latest DNS list
r = requests.get(dnsserverlist)
data = r.text

servers = data.split()

responses = {}

# Perform resolution on each of the 'goodservers' 
for goodserver in goodservers:
    print("Resolving with", goodserver)

    thisserver = {}

    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [goodserver]
    goodanswer = resolver.query(rootdomain, 'A')

    for rr in goodanswer:
        thisserver["goodip"] = str(rr)

    try:
        nxdomanswer = resolver.query('lkjhuihuifr.' + rootdomain,'A')
        thisserver["nxdomain"] = False
    except dns.resolver.NXDOMAIN:
        thisserver["nxdomain"] = True

    responses[goodserver] = thisserver

# loop through the list
for server in servers:
    #print(server)
    server = server.strip()

    # Skip if not IPv4
    valid = re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",server)
    if not valid:
        continue

    print("Checking " + server)

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
        nxanswer = resolver.query('lkjlkjqqewdw.' + rootdomain,'A')
    except dns.resolver.NXDOMAIN:
        gotnxdomain = True
    except:
        continue

    for goodresponse in responses:
        if responses[goodresponse]["nxdomain"] == gotnxdomain:
            nxdommatches += 1

    if resolvematches == 3 and nxdommatches == 3:
        print(server + " provided valid response")
        validservers.append(server)

# write the content of the list to the disk for use
with open(updatedlist) as resolvers:
    resolvers.write(validservers)

print("Update finished. Wrote {size} servers".format(size=len(validservers)))
