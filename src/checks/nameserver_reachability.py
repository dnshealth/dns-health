#!/usr/bin/env python3
#DNSHEALTH-11
import dns.resolver
import sys
from dns.exception import DNSException
import check_helpers as helpers

def DESCRIPTION():
    return "Checking of nameserver reachability"

MAX_RDCLASS = 65535

#Helper function to decide wether or not an object(or more specifically a response from a request in our case) is a null pointer or not.
def isNotNone(obj):
    if obj is not None:
        return True
    else:
        return False

#get all the reachable name servers form a given domain/url. 
#returns a tuple with true if all the name servers are sending back a tcp/udp packet 
# and a dictionary with 3 fields:
# "name_server" field for the name of the name server
# "received_udp_packet" field for wether or not this nameserver sent a udp packet back
# "received_tcp_packet" field for wether or not this nameserver sent a tcp packet back

def getReachableNameServers(domain, nameServers,ipv6):

    results = []

    for nameServer in nameServers:

        #make a dns ns query, acts as a dumb message since whatever we send we just care of what we get back
        query = dns.message.make_query(domain, dns.rdatatype.NS)

        query.flags |= dns.flags.AD
        
        query.find_rrset(query.additional, dns.name.root, MAX_RDCLASS, dns.rdatatype.OPT, create=True, force_unique=True)
        
        try:

            ip = helpers.getTheIPofAServer(nameServer,ipv6,DESCRIPTION())
            
        except Exception as e:
                
            return {"result": False, "description" : DESCRIPTION() ,"details": e.msg}

        if ip["result"] == False :
            return ip

        #try sending a udp packet to see if it's listening on UDP
        udpPacket = dns.query.udp(query,ip["result"])

        #try sending a tcp packet to see if it's listening on TCP
        tcpPacket = dns.query.tcp(query,ip["result"])

        if isNotNone(udpPacket) and isNotNone(tcpPacket):
            results.append({ "name_server" : nameServer,"description": {"valid_entry" : str(True), "received_udp_packet" : isNotNone(udpPacket),"received_tcp_packet" : isNotNone(tcpPacket)}})
        else:
            results.append({ "name_server" : nameServer,"description": {"valid_entry" : str(False), "received_udp_packet" : isNotNone(udpPacket),"received_tcp_packet" : isNotNone(tcpPacket)}})

    for i in results:
        if i["description"]["valid_entry"] == "False":
            return {"result": False, "description":DESCRIPTION() , "details": "server {0} did not return a tcp or a udp packet".format(i["name_server"]), "detailed_results": results}

    return {"result": True,"description": DESCRIPTION() ,"details": "All the name servers successfully returned a tcp and a udp packet!", "detailed_results": results}

def run(domain, ns,ipv6):
    return getReachableNameServers(domain,ns,ipv6)
