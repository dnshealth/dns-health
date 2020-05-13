#!/usr/bin/env python3
# Program checks if list of nameservers have unique ASN(are diverse)
# Takes hostname and list of nameservers as input
# Returns False if any two ASN of nameservers are equal
# Returns True id all ASN of nameservers are unique
from ipwhois.net import Net
from ipwhois.asn import IPASN
import src.checks.check_helpers as helpers

def DESCRIPTION():
    return "Network diversity"


def run(hostname, list_of_NS,ipv6):

    listASN = []

    try: 
        for x in list_of_NS:
            # Getting IPs of nameservers
            net = Net(helpers.getTheIPofAServer(x,ipv6,DESCRIPTION())["result"])
            obj = IPASN(net)
            # Getting dictionary with AS info for specific IP
            results = obj.lookup()
            # Extracts only ASN from dictionary and adds them to a list
            listASN.append(results.get('asn'))
    except Exception as err:
        return {"description": DESCRIPTION(), "result": False, "details": str(err) + f": could not resolve IP of nameserver {x}"}

    # Checks if nameservers ar located in at least 2 different Autonomous Systems
    if  len(set(listASN)) < 2:
        return {"description": DESCRIPTION(), "result": False, "details": "all nameservers are located in the same Autonomous System"}
    else:
        return {"description": DESCRIPTION(), "result": True, "details": f"nameserver are located at {len(set(listASN))} different Autonumous Systems"}
