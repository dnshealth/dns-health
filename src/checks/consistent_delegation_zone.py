#!/usr/bin/env python3
# Program checks if all nameservers in list refrence each other
# Takes hostname and list of nameservers as input
# Returns False if delegation and zone are not consistent
# Returns True if delegation and zone are consistent
import dns.resolver
from src.checks.check_helpers import consistent

def DESCRIPTION():
    return "Consistency between delegation and zone"


# Takes "hostname" string, "list_of_NS" list of string
# Returns dictionary with "description" key string value, "results" key boolean value, "details" key string value
def run(hostname, list_of_NS, ipv6):
    
    # Get a list of nameserver records from each namserver
    records = consistent(hostname, list_of_NS, DESCRIPTION(), "NS", ipv6)
    
    # If function threw an error, return the error
    if not isinstance(records, list):
        return records
    
    # If no error was thrown check if nameserver records are consistent with delegation
    return recordcheck(records, list_of_NS, DESCRIPTION())

# Takes "records" list of lists of string, "list_of_NS" list of string, "description" string
# Returns dictionary with "description" key string value, "results" key boolean value, "details" key string value
def recordcheck(records, list_of_NS, description):
    
    # Checking if all nameservers from all queries match the input list of nameservers
    if not all(x == sorted(list_of_NS) for x in records):
        return {"description": description, "result": False, "details": "Delegation is not consistent with nameserver records"}
    else:
        return {"description": DESCRIPTION(), "result": True, "details": "Delegation is consistent with nameserver records"}
