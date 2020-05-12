#!/usr/bin/env python3
# Program checks if list of nameservers have unique ASN(are diverse)
# Takes hostname and list of nameservers as input
# Returns False if any two ASN of nameservers are equal
# Returns True id all ASN of nameservers are unique
from ipwhois.net import Net
from ipwhois.asn import IPASN
import socket



def run(hostname, list_of_NS):
    description = "Network diversity"
    listASN = []

    try:
        for x in list_of_NS:
            # Get IP of nameserver
            net = Net(socket.gethostbyname(x))
            
            # Get ASN information object for IP address
            obj = IPASN(net)
            
            # Get dictionary with AS info for the object
            results = obj.lookup()
            
            # Extracts only ASN from dictionary and adds them to a list
            listASN.append(results.get('asn'))
    # Catch error if IP of a nameserver could not be resloved
    except socket.gaierror as err:
        return {"description": description, "result": False, "details": str(err) + f": could not resolve IP of nameserver {x}"}

    # Checks if nameservers ar located in at least 2 different Autonomous Systems
    if  len(set(listASN)) < 2:
        return {"description": description, "result": False, "details": "all nameservers are located in the same Autonomous System"}
    else:
        return {"description": description, "result": True, "details": f"nameserver are located at {len(set(listASN))} different Autonumous Systems"}
