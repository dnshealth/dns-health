#!/usr/bin/env python3
# Program checks if all authoritative nameserver SOA and NS records are consistent
# Takes hostname and list of nameservers as input
# Returns False if query fails or nameserver IP can not be resolved
# Returns False if NS records or SOA records are not consistent
# Returns True if NS records and SOA records are consistent; contain the same information
import socket
import dns.resolver
from src.helpers import consistent


def run(hostname, list_of_NS):
    # Filter out duplicate nameserver entries
    list_of_NS = set(list_of_NS)
    description = "Consistency between authoritative nameservers"

    # Get a list of records from all nameservers
    ns_check = consistent(hostname, list_of_NS, description, 'NS')
    
    if not isinstance(ns_check, list):
        return ns_check
    
    ns_res = recordcheck(ns_check, list_of_NS, "NS")
    
    # Check if nameserver NS records are consistent if not return False
    if not ns_res[0]:
        return {"description": description, "result": False, "details": ns_res[1]}
    else:
        pass

    # Check if nameserver SOA records are consistent if not return False
    soa_check = consistent(hostname, list_of_NS, description, 'SOA')
    
    if not isinstance(soa_check, list):
        return soa_check
    
    soa_res = recordcheck(soa_check, list_of_NS, "SOA")
    if not soa_res[0]:
        return {"description": description, "result": False, "details": soa_res[1]}
    else:
        return {"description": description, "result": True, "details": soa_res[1]}


def recordcheck(records, list_of_NS, flag):
    
    if not all(records[0] == i for i in records):
        return (False, f"Inconsistent {flag} records")
    else:
        return (True, f"Consistent {flag} records")