#!/usr/bin/env python3

# Example usage: ./main.py --domain dnshealth.eu --ns dns1.dnshealth.eu dns2.dnshealth.eu
import argparse
from . import helpers
import dns.name
import json
from termcolor import colored

parser = argparse.ArgumentParser()

# We define the parameters that the user should input.
parser.add_argument('--domain', help="The domain to check on NS servers")
# The user can enter a list of nameservers with the --ns param
parser.add_argument('--ns', type=str, nargs='+', help="A list of NS servers to check.")
parser.add_argument('--json', help="Output results from checks as JSON", action='count', default=0)
# add argument to enable ipv6
parser.add_argument('--ipv6', help ="Runs checks against IPv6 addresses", default = 0, action="store_true")
# add argument to enable support for delegated domains
parser.add_argument('--delegated', help ="Runs the checks against the current nameservers of the domain", default = 0, action="store_true")
# We parse the arguments
args = parser.parse_args()

# Now we have the params in args like this:
# args.domain gives the domain the user entered.
# args.ns gives a list of NS servers.
domain = args.domain
ns = args.ns
ipv6 = args.ipv6

if not args.delegated:
    ns = helpers.get_nameservers(domain)

# Check if any of the input values are empty
if domain == None or domain == "":
    raise Exception("ERROR: No domain given")

if ns == None or ns == "":
    raise Exception("ERROR: No nameservers given")

if ipv6 == None or ipv6 == "":
    raise Exception("ERROR: No IP version given")

# Now, we can start to run the checks. We define a list to which we append the results from each check.
results = helpers.return_results(domain,ns,[],ipv6)

    # If the check failed, we shall exit the for loop and stop testing.
#    if not result["result"]:
#        break

# At the end, we want to output the results in a neat user-readable format.
if not args.json:
    for result in results[0].get("checks"):
        # If result passed.
        if result.get("result"):

            print(colored("[\u2713] PASS {0}".format(str(result["description"])), 'green'))
        else:

            print(colored("[X] FAIL {0} , REASON : {1}".format(str(result["description"]), str(result.get("details"))), 'red'))
else:
    print(json.dumps(results))
