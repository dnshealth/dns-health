#!/usr/bin/env python3
# Program checks if given hostname is valid
# Takes hostname and list of nameservers as input
# Returns False if hostname is not valid
# Returns True if hostname is valid
import re
import socket

# Takes "hostname" string, "list_of_NS" list of string
# Returns dictionary with "description" key string value, "results" key boolean value, "details" key string value
def run(hostname, list_of_NS, ipv6):
    # Define description of check
    description = "Valid hostname"
    
    # Check if IP was given instead of domain name(hostname contains only numbers)
    if not re.match(r"[a-zA-Z]+", hostname):
        return {"description": description, "result": False, "details": "IP given insted of domain name"}

    # Check if any of the given nameservers is an IP address insted of the domain name for said nameserver
    for nameserver in list_of_NS:
        if not re.match(r"[a-zA-Z]+", nameserver):
            return {"description": description, "result": False, "details": "IP given insted of nameserver"}
        
    # Check if hostname correct length
    if len(hostname) > 255:
        return {"description": description, "result": False, "details": "Hostname too long"}
    
    # Strip end dot, if present
    if hostname[-1] == ".":    
        hostname = hostname[:-1]
        

    # Strip end dots from nameservers
    for i in range(len(list_of_NS)):
        if list_of_NS[i][-1] == ".":
            list_of_NS[i] = list_of_NS[i][:-1]


    # Regex to check for invalid simbols
    allowed = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
    
    # Check if hostname has correct number of parts
    if len(hostname.split(".")) < 2:
        return {"description": description, "result": False, "details": "Hostname incorrect form"}
    
    # Return True if all parts of hostname are valid
    result = all(allowed.match(x) for x in hostname.split("."))
    
    # Check if all nameservers, have correct number of parts
    for x in list_of_NS:
        if len(x.split(".")) < 2:
            return {"description": description, "result": False, "details": "Nameserver(s) incorrect form"}
        
    # Return True if all parts of nameserver are valid 
    resultNS = all(allowed.match(y) for x in list_of_NS for y in x.split("."))
        
    # If both domain and nameserver addresses are valid return True otherwise False
    if result and resultNS:
        return {"description": description, "result": True, "details": ""}
    
    elif result and not resultNS:
        return {"description": description, "result": False, "details": "Nameserver(s) are invalid"}
    
    elif not result and resultNS:
        return {"description": description, "result": False, "details": "Hostname is invalid"}
    
    else:
        return {"description": description, "result": False, "details": "Hostname and nameservers are invalid"}
