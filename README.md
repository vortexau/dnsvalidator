# DNS Validator
Maintains a list of IPv4 DNS servers by verifying them against baseline servers, and ensuring accurate responses.

[![Python 3.2|3.6](https://img.shields.io/badge/python-3.2|3.6-green.svg)](https://www.python.org/) [![License](https://img.shields.io/badge/license-GPL3-_red.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html) 
[![Twitter](https://img.shields.io/badge/twitter-@vortexau-blue.svg)](https://twitter.com/vortexau)
[![Twitter](https://img.shields.io/badge/twitter-@codingo__-blue.svg)](https://twitter.com/codingo_) 

![DNSValidator](https://github.com/vortexau/dnsvalidator/blob/master/.github/dnsvalidator.png)

DNS Validator's approach is different to other DNS query validation tools. This tool performs multiple validation steps on each resolver:

* Baselines non-geolocated domain names against "trusted" public DNS resolvers, `1.1.1.1`, `8.8.8.8` and `9.9.9.9` 
  * For each resolver being tested DNS Validator ensures that each baselined domain name resolves to the same IP Address.
    * Servers that return an answer that differs from the baseline are immediately skipped
* Performs DNS lookup of known commonly spoofed DNS addresses to ensure NXDOMAIN is returned when expected.
  * Resolvers that do not return NXDOMAIN for random subdomains of known target domains are immediately skipped.

# Usage

| Argument   | Description                                                                                                  |
|------------|--------------------------------------------------------------------------------------------------------------|
| (stdin)    | Pipe target lists from another application to verify. |
| -t         | Specify a target DNS server to verify. |
| -tL        | Specify a list of targets or a URL to a list of targets |
| -e         | Specify a target exclusion. |
| -eL        | Specify a list of targets or a URL to a list of targets to exclude. |
| -r         | Specify a root domain to compare to. Must be non-geolocated or most resolvers will fail. |
| -q         | Specify a resolver query to use (default:dnsvalidator) |
| -threads   | Specify the maximum number of threads to run at any one time (DEFAULT:5)                                     |
| -timeout   | Specify a timeout value in seconds for any single thread (DEFAULT:600)                                       |
| -o         | Specify an output file to write successful output to. |
| --no-color | If set then any foreground or background colours will be stripped out                                        |
| --silent   | If set then only successfully resolved servers will be displayed and banners and other information will be redacted. |
| -v         | If set then verbose output will be displayed in the terminal.                                                 |

# Setup
Install using:
```
$ python3 setup.py install
```
Dependencies will then be installed and DNS Validator will be added to your path as `dnsvalidator`.

# Examples:

## CLI:

```bash
$ dnsvalidator -tL https://public-dns.info/nameservers.txt -threads 20 -o resolvers.txt
```

## Docker:

Build 

```bash
$ docker build -t dnsvalidator .
```

Run:

```bash
$ docker run -v $(pwd):/dnsvalidator/output -t dnsvalidator -tL https://public-dns.info/nameservers.txt -threads 20 -o /dnsvalidator/output/resolvers.txt
```

# Caveats

* **WARNING** Keep the thread count to a reasonable level and/or use a VPS/VPN appropriately. Pushing the thread count too high can make it look like you are attempting to attack DNS servers, resulting in network level DNS blocks from your ISP. _As us how we know..._ 
* Only IPv4 DNS Resolvers are validated at the current time. IPv6 resolvers are skipped.
* Root domains used for baseline tests must not be geolocated; specifically they must return the same IP address regardless of the location on the planet they are resolved from. Domains such as `google.com` or `facebook.com` (and many others) are not suitable for baselines, as they return a geo-located IP address when resolved.
  * Using a root domain that is geo-located will result in only resolvers local to the user being returned as valid.
