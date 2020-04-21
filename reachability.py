import dns.resolver

MAX_RDCLASS = 65535

@staticmethod
def isNotNone(obj):
    if obj is not None:
        return True
    else:
        return False


def getNSResults(url):

    #create an empty list where we can store all the nameservers we found
    nameServers = []

    nameServers = dns.resolver.query(url,dns.rdatatype.NS, raise_on_no_answer=False)

    #create a dictionary where based on all the nameservers.
    #1st label refers to the ns name of our url that we inserted.
    #2nd label shows wether or not we received a UDP response or not.
    #3rd label shows wether or not we received a TCP response or not.
    results = {}

    for nameServer in nameServers:

        #make a dns ns query, acts as a dumb message since whatever we send we just care of what we get back
        query = dns.message.make_query(url, dns.rdatatype.NS)

        query.flags |= dns.flags.AD
        
        query.find_rrset(query.additional, dns.name.root, MAX_RDCLASS, dns.rdatatype.OPT, create=True, force_unique=True)

        #make sure it's an str and prints the name of the name server
        #print type(nameServer.target.to_text())
        #print nameServer.target.to_text()

        #try sending a udp packet to see if it's listening on UDP
        udpPacket = dns.query.udp(query,nameServer.target.to_text())

        #try sending a tcp packet to see if it's listening on TCP
        tcpPacket = dns.query.tcp(None,nameServer)

        #add the results in a dictionary and return it, to be checked later by the user.
        results.update({"nsName" == nameServer, "receivedUDPPacket" == isNotNone(udpPacket),"receivedTCPPacket" == isNotNone(tcpPacket)})


getNSResults("google.com")
