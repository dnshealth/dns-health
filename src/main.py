#!/usr/bin/env python3

# Example usage: ./main.py --domain dnshealth.eu --ns dns1.dnshealth.eu dns2.dnshealth.eu
import argparse
import checks
import dns.name

parser = argparse.ArgumentParser()

# We define the parameters that the user should input.
parser.add_argument('--domain')
# The user can enter a list of nameservers with the --ns param
parser.add_argument('--ns', type=str, nargs='+')

# We parse the arguments
args = parser.parse_args()

# Now we have the params in args like this:
# args.domain gives the domain the user entered.
# args.ns gives a list of NS servers.
domain = args.domain
ns = args.ns

# Now, we can start to run the checks. We define a list to which we append the results from each check.
checks = [checks.valid_nameserver]
results = []

# Run each check and append result to results.
for check in checks:
    result = check.run(domain,ns)
    results.append(result)

    # If the check failed, we shall exit the for loop and stop testing.
    if not result["result"]:
        break

# At the end, we want to output the results in a neat user-readable format.
for result in results:
    # If result passed.
    if result["result"]:
        print "[*] PASS {0}".format(result["description"])
    else:
        print "[*] FAIL {0}".format(result["description"])
