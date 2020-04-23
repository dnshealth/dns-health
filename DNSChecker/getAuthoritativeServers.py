#!/usr/bin/env python3
#DNSHEALTH-12
import dns.query, dns.resolver
from dns.exception import DNSException

# a functions that returns all the authoritative servers for the domain given.
# Takes a domain as an argument and returns a tuple of the OK to indicate that it succeed 
# and a list of tuple with all the authoritative domains.
def getAuthoritativeServers(domain, name_servers):

    default_resolver = dns.resolver.get_default_resolver()

    array_of_domains = domain.split('.')

    #a list that holds all the results for all the authoritative servers for a domain given
    results = []

    #start by splitting our domain in all the possible subdomains
    # eg testing.com.se would be split in .se, then in .com.se and finally in tesitng.com.se
    for i in range(len(array_of_domains), 0, -1):
        
        sub_string = '.'.join(array_of_domains[i-1:])

        print('Looking up %s on %s' % (sub_string, name_servers))
        
        #make a query to send at the dns servers
        query = dns.message.make_query(sub_string, dns.rdatatype.NS)
        
        #send the query for every name server we have
        response = dns.query.udp(query, name_servers)

        #retrieve the response code from the dns query we executed
        response_codes = response.rcode()
        
        #An error occured(either we can't find the domain or something else happened) will be caught here and will probably exit
        if response_codes != dns.rcode.NOERROR:
            raise DNSException("AN ERROR OCCURED")
        
        #based onthe type of the reposnse, get a list of the responses of the rrsets
        if len(response.authority) > 0:
            rrsets = response.authority
        elif len(response.additional) >0:
            rrsets = response.additional
        else:
            rrsets = response.answer

        if sub_string == domain :

        #we must handle all the rrsets, not just the first one
        #bases on the rdtype response, we need to find which name servers are authoritative
        
            for rrset in rrsets:
            
                for rr in rrset:

                    #when the same server is authoritative for the domain, pass
                    if rr.rdtype == dns.rdatatype.NS:
                    
                        name_servers = default_resolver.query(rr.target).rrset[0].to_text()

                        results.append(("AUTHORITATIVE",rr.target.to_text(),domain))

                    elif rr.rdtype == dns.rdatatype.SOA:
                        
                        results.append(("SAME AUTHORITATIVE SERVER", sub_string))

                    else:
                       pass

    return ("OK",results)
