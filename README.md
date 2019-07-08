# DNS Validator
Maintains a list of DNS servers by verifying them against baseline servers, and ensuring accurate responses.

[![Python 3.2|3.6](https://img.shields.io/badge/python-3.2|3.6-green.svg)](https://www.python.org/) [![License](https://img.shields.io/badge/license-GPL3-_red.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html) 
[![Twitter](https://img.shields.io/badge/twitter-@vortexau-blue.svg)](https://twitter.com/vortexau)
[![Twitter](https://img.shields.io/badge/twitter-@codingo__-blue.svg)](https://twitter.com/codingo_) 

# Usage

| Argument   | Description                                                                                                  |
|------------|--------------------------------------------------------------------------------------------------------------|
| (stdin)    | Pipe target lists from another application to verify. |
| -t         | Specify a target DNS server to verify. |
| -tL        | Specify a list of targets or a URL to a list of targets |
| -e         | Specify a target exclusion. |
| -eL        | Specify a list of targets or a URL to a list of targets to exclude. |
| -r         | Specify a root domain to compare to. |
| -q         | Specify a resolver query to use (default:dnsvalidator) |
| -threads   | Specify the maximum number of threads to run at any one time (DEFAULT:5)                                     |
| -timeout   | Specify a timeout value in seconds for any single thread (DEFAULT:600)                                       |
| -o         | Specify an output file to write successful output to. |
| --no-color | If set then any foreground or background colours will be stripped out                                        |
| --silent   | If set then only successfully resolved servers will be displayed and banners and other information will be redacted. |
| -v         | If set then verbose output will be displayed in the terminal.                                                 |
