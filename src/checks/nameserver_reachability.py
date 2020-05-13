#!/usr/bin/env python3
#DNSHEALTH-11
import dns.resolver
import sys
from dns.exception import DNSException
import checks.check_helpers as helpers

def DESCRIPTION():
    return "Checking of nameserver reachability"

MAX_RDCLASS = 65535

#Helper function to decide wether or not an object(or more specifically a response from a request in our case) is a null pointer or not.
def isNotNone(obj):
    if obj is not None:
        return True
    else:
        return False

def nameserver_reachability(domain, name_servers,ipv6):

    results = []

    for name_server in name_servers:

        #make a dns ns query, acts as a dumb message since whatever we send we just care of what we get back
        query = dns.message.make_query(domain, dns.rdatatype.NS)

        query.flags |= dns.flags.AD
        
        query.find_rrset(query.additional, dns.name.root, MAX_RDCLASS, dns.rdatatype.OPT, create=True, force_unique=True)
        
        ip = helpers.getTheIPofAServer(name_server,ipv6,DESCRIPTION())

        if ip["result"] == False :
            return ip

        #try sending a udp packet to see if it's listening on UDP
        udpPacket = dns.query.udp(query,ip["result"])
     
        #try sending a tcp packet to see if it's listening on TCP
        tcpPacket = dns.query.tcp(query,ip["result"])

        if isNotNone(udpPacket) and isNotNone(tcpPacket):
            results.append({ "name_server" : name_server,"description": {"valid_entry" : str(True), "received_udp_packet" : isNotNone(udpPacket),"received_tcp_packet" : isNotNone(tcpPacket)}})
        else:
            results.append({ "name_server" : name_server,"description": {"valid_entry" : str(False), "received_udp_packet" : isNotNone(udpPacket),"received_tcp_packet" : isNotNone(tcpPacket)}})

    for i in results:
        if i["description"]["valid_entry"] == "False":
            return {"result": False, "description":DESCRIPTION() , "details": "server {0} did not return a tcp or a udp packet".format(i["name_server"]), "detailed_results": results}

    return {"result": True,"description": DESCRIPTION() ,"details": "All the name servers successfully returned a tcp and a udp packet!", "detailed_results": results}

def run(domain, ns,ipv6):
    return nameserver_reachability(domain,ns,ipv6)
