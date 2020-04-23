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
    
    temp  = dns.resolver.Resolver().query(nameOfTheServer,'A')

    return temp.response.answer[0][0].to_text()

#get all the reachable name servers form a given domain/url. 
#returns a tuple with true if all the name servers are sending back a tcp/udp packet 
# and a dictionary with 3 fields:
# "nsName" field for the name of the name server
# "receivedUDPPacket" field for wether or not this nameserver sent a udp packet back
# "receivedTCPPacket" field for wether or not this nameserver sent a tcp packet back

def run(domain, ns):
    (result, _msg) = getReachableNameServers(domain,ns)
    return {"result": result, "description": "Nameserver reachability TCP&UDP"}

def getReachableNameServers(domain, nameServers):
    # Nameservers are passed as params

    #create an empty list where we can store all the nameservers we found
    #nameServers = []

    #nameServers = dns.resolver.query(domain,dns.rdatatype.NS, raise_on_no_answer=False)

    #create a dictionary where based on all the nameservers.
    #1st label shows if the nameserver sent back all the packets
    #2nd label refers to the ns name of the domain that we inserted.
    #2rd label shows wether or not we received a UDP response or not.
    #4th label shows wether or not we received a TCP response or not.
    results = {}

    for nameServer in nameServers:

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
            results.update({"isGood" : str(True),  "nsName" : nameServer, "receivedUDPPacket" : isNotNone(udpPacket),"receivedTCPPacket" : isNotNone(tcpPacket)})
        else:
            results.update({"isGood" : str(False), "nsName" : nameServer, "receivedUDPPacket" : isNotNone(udpPacket),"receivedTCPPacket" : isNotNone(tcpPacket)})

    for i in results:
        if i[0] == "False":
            return (False, results)

    return (True,results)
