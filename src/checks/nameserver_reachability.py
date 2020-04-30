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

    answer = temp.response.answer[0][0].to_text()

    if answer is not None:
        return {"result": answer,"description": "Checking of nameserver reachability" ,"details": "Successfully found the IP!"}
    else:
        return {"result": -1, "description": "Checking of nameserver reachability" ,"details": "No A records for {0} server were found!".format(nameOfTheServer)}

#get all the reachable name servers form a given domain/url. 
#returns a tuple with true if all the name servers are sending back a tcp/udp packet 
# and a dictionary with 3 fields:
# "name_server" field for the name of the name server
# "received_udp_packet" field for wether or not this nameserver sent a udp packet back
# "received_tcp_packet" field for wether or not this nameserver sent a tcp packet back

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

    results = []

    for nameServer in nameServers:

        #make a dns ns query, acts as a dumb message since whatever we send we just care of what we get back
        query = dns.message.make_query(domain, dns.rdatatype.NS)

        query.flags |= dns.flags.AD
        
        query.find_rrset(query.additional, dns.name.root, MAX_RDCLASS, dns.rdatatype.OPT, create=True, force_unique=True)
        
        try:

            ip = getTheIPofAServer(nameServer)
            
        except  dns.resolver.NXDOMAIN as e:
                
            return {"result": False, "description" :  "Checking of nameserver reachability" ,"details": e.msg}

        if ip["result"] == -1 :
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
            return {"result": False, "description": "Checking of nameserver reachability" , "details": "server {0} did not return a tcp or a udp packet".format(i["name_server"]), "detailed_results": results}

    return {"result": True,"description": "Checking of nameserver reachability" ,"details": "All the name servers successfully returned a tcp and a udp packet!", "detailed_results": results}

def run(domain, ns):
    return getReachableNameServers(domain,ns)
