#!/usr/bin/env python3
# Program checks if list of nameservers have unique ASN(are diverse)
# Takes hostname and list of nameservers as input
# Returns False if any two ASN of nameservers are equal
# Returns True id all ASN of nameservers are unique
from ipwhois.net import Net
from ipwhois.asn import IPASN
import dns.resolver


def getTheIPofAServer(nameOfTheServer, ipv6_enabled):
   
    try:
        if(ipv6_enabled):
            temp  = dns.resolver.Resolver().query(nameOfTheServer,'AAAA')
        else:
            temp  = dns.resolver.Resolver().query(nameOfTheServer,'A')
        

    except Exception as e:

        return {"result": False, "description": "Check network diversity" ,"details": e.msg}

    answer = temp.response.answer[0][0].to_text()

    if answer is not None:
        return {"result": answer, "description": "Check network diversity", "details": "Successfully found the IP!"}
    elif ipv6_enabled:
        return {"result": False, "description": "Check network diversity" ,"details": "No AAAA records for {0} server were found!".format(nameOfTheServer)}
    else:
        return {"result": False, "description": "Check network diversity" ,"details": "No A records for {0} server were found!".format(nameOfTheServer)}


def run(hostname, list_of_NS, ipv6_enabled):
    description = "Network diversity"
    listASN = []

    for x in list_of_NS:
        # Getting IPs of nameservers
        net = Net(getTheIPofAServer(x, ipv6_enabled))
        obj = IPASN(net)
        # Getting dictionary with AS info for specific IP
        results = obj.lookup()
        # Extracts only ASN from dictionary and adds them to a list
        listASN.append(results.get('asn'))

    # Checks if nameservers ar located in at least 2 different Autonomous Systems
    if  len(set(listASN)) < 2:
        return {"description": description, "result": False, "details": "all nameservers are located in the same Autonomous System"}
    else:
        return {"description": description, "result": True, "details": f"nameserver are located at {len(set(listASN))} different Autonumous Systems"}
