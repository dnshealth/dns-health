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

# Hard coded special IPs that the imports don't cover
bad_1 = "203.0.113.0"
bad_2 = "224.0.0.0"


def prohibited_check(ns_server):

    result = dns.resolver.query(ns_server, 'A')
    for ipval in result:
        if (ipaddress.ip_address(str(ipval)).is_private or
                str(ipval) == bad_1 or
                str(ipval) == bad_2):
            print_fail()
            return False

        else:
            print("[+] The IP for the for " + ns_server + " is: " + ipval.to_text())
            print("[OK]")
            return True


def print_fail():
    print("[-] Error ! The IP is not a global IP.")
    print("[-] TEST FAIL")


# For debugging purposes please use prohibited_check("198.51.100.0")

