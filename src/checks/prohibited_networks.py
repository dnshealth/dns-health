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


def run(domain, ns_list):
    # Check each ns in ns_list. If one fails, immediately return false. Otherwise, return true after having checked
    # everything
    for ns in ns_list:
        if not prohibited_check(ns):
            return {"description": "Prohibited networks check", "result": False}

    return {"description": "Prohibited networks check", "result": True}


def prohibited_check(ns_server):
    # Excluding special IP - ranges that are not covered in ipaddress module
    deprecated_ips = ipaddress.ip_network('192.88.99.0/24')
    shared_address_space = ipaddress.ip_network('100.64.0.0/10')
    try:
        result = dns.resolver.query(ns_server, 'A')
    except:
        return False
    for ipval in result:
        print(ipval)
        if (
                ipaddress.ip_address(str(ipval)).is_private or
                ipaddress.ip_address(str(ipval)).is_multicast or
                ipaddress.ip_address(str(ipval)).is_loopback or
                ipaddress.ip_address(str(ipval)) in deprecated_ips or
                ipaddress.ip_address(str(ipval)) in shared_address_space
        ):
            return False

        else:
            return True


# For debugging purposes please use print(prohibited_check("192.88.99.1"))
print(prohibited_check("ns.blabla.com"))
