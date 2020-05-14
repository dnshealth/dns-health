#!/usr/bin/env python3
# Program checks if all authoritative nameserver SOA and NS records are consistent
# Takes hostname and list of nameservers as input
# Returns False if query fails or nameserver IP can not be resolved
# Returns False if NS records or SOA records are not consistent
# Returns True if NS records and SOA records are consistent; contain the same information
import dns.resolver
from src.checks.check_helpers import consistent

def DESCRIPTION():
    return "Consistency between authoritative nameservers"

# Takes "hostname" string, "list_of_NS" list of string
# Returns dictionary with "description" key string value, "results" key boolean value, "details" key string value
def run(hostname, list_of_NS, ipv6):
    # Filter out duplicate nameserver entries
    list_of_NS = set(list_of_NS)

    # Get a list of records from all nameservers
    ns_check = consistent(hostname, list_of_NS, DESCRIPTION(), 'NS', ipv6)
    
    # Check if record extraction function returned an error, if so return the error
    if not isinstance(ns_check, list):
        return ns_check
    
    # Compare the records with eachother to see if they are consistent
    ns_res = recordcheck(ns_check, list_of_NS, "NS")
    
    # Extract answer from tuple
    if not ns_res[0]:
        return {"description": DESCRIPTION(), "result": False, "details": ns_res[1]}
    else:
        pass

    # Get a list of SOA records from all nameservers
    soa_check = consistent(hostname, list_of_NS, DESCRIPTION(), 'SOA', ipv6)
    
    # Check if record extraction function returned an error, if so return the error
    if not isinstance(soa_check, list):
        return soa_check
    
    # Compare the records with eachother to see if they are consistent
    soa_res = recordcheck(soa_check, list_of_NS, "SOA")
    
    # Extract answer from tuple
    if not soa_res[0]:
        return {"description": DESCRIPTION(), "result": False, "details": soa_res[1]}
    else:
        return {"description": DESCRIPTION(), "result": True, "details": "Both SOA and NS records are consistent"}


# Takes "records" list of lists of string, "list_of_NS" list of string, "flag" string
# Returns tuple with boolean and string
def recordcheck(records, list_of_NS, flag):
    
    if not all(records[0] == i for i in records):
        return (False, f"Inconsistent {flag} records")
    else:
        return (True, f"Consistent {flag} records")
