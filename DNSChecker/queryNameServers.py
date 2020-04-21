#!/usr/bin/env python3
#Utility function to help for queries on name servers
import dns.query
import dns.resolver
from dns.exception import DNSException

#a functions that returns all the authoritative servers for the domain given.
#  Takes a domain as an argument and returns a tuple of the OK to indicate that it succeed 
# and a list of tuple with all the authoritative domains.
def queryAuthoritativeNameServers(domain):

    defaultResolver = dns.resolver.get_default_resolver()
    
    nameServers = defaultResolver.nameservers[0]

    arrayOfDomains = domain.split('.')

    #a list that holds all the results for all the authoritative servers for a domain given
    results = []

    #start by splitting our domain in all the possible subdomains
    # eg testing.com.se would be split in .se, then in .com.se and finally in tesitng.com.se
    for i in xrange(len(arrayOfDomains), 0, -1):
        
        subString = '.'.join(arrayOfDomains[i-1:])

        print('Looking up %s on %s' % (subString, nameServers))
        
        #make a query to send at the dns servers
        query = dns.message.make_query(subString, dns.rdatatype.NS)
        
        #send the query for every name server we have
        response = dns.query.udp(query, nameServers)

        #retrieve the response code from the dns query we executed
        responseCode = response.rcode()
        
        #An error occured(either we can't find the domain or something else happened) will be caught here and will probably exit
        if responseCode != dns.rcode.NOERROR:
            raise DNSException("AN ERROR OCCURED")
        
        #based onthe type of the reposnse, get a list of the responses of the rrsets
        if len(response.authority) > 0:
            rrsets = response.authority
        elif len(response.additional) > 0:
            rrsets = [response.additional]
        else:
            rrsets = response.answer

        #we must handle all the rrsets, not just the first one
        #bases on the rdtype response, we need to find which name servers are authoritative
        for rrset in rrsets:
            for rr in rrset:
                #when the same server is authoritative for the domain, pass
                if rr.rdtype == dns.rdatatype.NS:
                    
                    nameServers = defaultResolver.query(rr.target).rrset[0].to_text()

                    results.append(("AUTHORITATIVE",rr.target.to_text(),domain))

                elif rr.rdtype == dns.rdatatype.A:
                    
                    nServer = rr.items[0].address

                    results.append(("GLUE",rr.name.to_text(), nServer))

                else:
                    pass
    return ("OK",results)
