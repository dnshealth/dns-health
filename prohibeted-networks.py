#!/usr/bin/env python3

# This feature will check if the NS server IP is global or private
# If it is global it will pass the test
# If it is local it will prompt the user that this IP is from a private network and
# test will fail

# Variables:
# ns_server --> should be taken as an argument from the command line
# ip_val --> extracted value of the ns server
import dns.resolver
from IPy import IP
import ipaddress


def prohibited_chech(ns_server):
    result = dns.resolver.query(ns_server, 'A')
    for ipval in result:

        if ipaddress.ip_address(str(ipval)).is_private:
            print("[+] Error ! The IP is not a global IP.")
            print("[+] TEST FAIL")

        else:
            print("[+] The IP for the for " + ns_server + " is: " + ipval.to_text())
            print("[OK]")


# Hard code check
prohibited_chech("ns1.loopia.se")
