#!/usr/bin/env python3
#DNSHEALTH-11
import dns.resolver

MAX_RDCLASS = 65535

#Helper function to decide wether or not an object(or more specifically a response from a request in our case) is a null pointer or not.
def isNotNone(obj):
    if obj is not None:
        return True
    else:
        return False

#Helper function to return the IP address of a server
def getTheIPofAServer(nameOfTheServer):
    
    temp  = dns.resolver.Resolver().query(nameOfTheServer.target.to_text(),'A')

    for i in temp.response.answer:
        for j in i.items:
            return j.to_text()

#get all the reachable name servers form a given domain/url. 
#returns a tuple with true if all the name servers are sending back a tcp/udp packet 
# and a dictionary with 3 fields:
# "nsName" field for the name of the name server
# "receivedUDPPacket" field for wether or not this nameserver sent a udp packet back
# "receivedTCPPacket" field for wether or not this nameserver sent a tcp packet back

def getReachableNameServers(domain):

    #create an empty list where we can store all the nameservers we found
    name_servers = []

    name_servers = dns.resolver.query(domain,dns.rdatatype.NS, raise_on_no_answer=False)

    #create a dictionary where based on all the nameservers.
    #1st label shows if the nameserver sent back all the packets
    #2nd label refers to the ns name of the domain that we inserted.
    #2rd label shows wether or not we received a UDP response or not.
    #4th label shows wether or not we received a TCP response or not.
    results = {}

    for nameServer in name_servers:

        #make a dns ns query, acts as a dumb message since whatever we send we just care of what we get back
        query = dns.message.make_query(domain, dns.rdatatype.NS)

        query.flags |= dns.flags.AD
        
        query.find_rrset(query.additional, dns.name.root, MAX_RDCLASS, dns.rdatatype.OPT, create=True, force_unique=True)

        ipOfnameServer = getTheIPofAServer(nameServer)

        #try sending a udp packet to see if it's listening on UDP
        udpPacket = dns.query.udp(query,ipOfnameServer)

        #try sending a tcp packet to see if it's listening on TCP
        tcpPacket = dns.query.tcp(query,ipOfnameServer)

        if isNotNone(udpPacket) and isNotNone(tcpPacket):
            results.update({"isGood" : str(True),  "nsName" : nameServer.target.to_text(), "receivedUDPPacket" : isNotNone(udpPacket),"receivedTCPPacket" : isNotNone(tcpPacket)})
        else:
            results.update({"isGood" : str(False), "nsName" : nameServer.target.to_text(), "receivedUDPPacket" : isNotNone(udpPacket),"receivedTCPPacket" : isNotNone(tcpPacket)})

    for i in results:
        if i[0] == "False":
            return (False, results)

    return (True,results)