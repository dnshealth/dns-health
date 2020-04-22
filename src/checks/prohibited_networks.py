#!/usr/bin/env python3

# This feature will check if the NS server IP is global or private
# If it is global it will pass the test
# If it is local it will prompt the user that this IP is from a private network and
# test will fail

# Variables:
# ns_server --> should be taken as an argument from the command line
# ip_val --> extracted value of the ns server
import dns.resolver
import ipaddress

def run(domain,ns_list):
    # Check each ns in ns_list. If one fails, immediately return false. Otherwise, return true after having checked everything
    for ns in ns_list:
        if not prohibited_check:
            return {"description": "Prohibited networks check", "result": False}

    return {"description": "Prohibited networks check", "result": True}


def prohibited_check(ns_server):
    # Excluding special IP - ranges that are not covered in ipaddress module
    deprecated_ips = ipaddress.ip_network('192.88.99.0/24')
    shared_address_space = ipaddress.ip_network('100.64.0.0/10')
    result = dns.resolver.query(ns_server, 'A')
    for ipval in result:
        if (ipaddress.ip_address(str(ipval)).is_private or
                ipaddress.ip_address(str(ipval)).is_multicast or
                ipaddress.ip_address(str(ipval)).is_loopback or
                ipaddress.ip_address(str(ipval)) in deprecated_ips or
                ipaddress.ip_address(str(ipval)) in shared_address_space
        ):
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
