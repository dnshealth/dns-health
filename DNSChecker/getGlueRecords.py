#!/usr/bin/env python3
#DNSHEALTH-14
import dns, dns.resolver, dns.query, dns.name
from dns.exception import DNSException

# a function that returns the glue records
# takes the domain name 
# returns a tuple w the ok sign and the list with the answers
def getGlueRecords(domain):

    nameServers         = []

    name                = dns.name.from_text(domain)

    defaultResolver     = dns.resolver.get_default_resolver()

    depth               = 2

    for nameServer in defaultResolver.nameservers:
    
            last = False
    
            while not last:
                
                subString    = name.split(depth)
    
                last         = subString[0].to_unicode() == '@'
    
                subString    = subString[1]

                query        = dns.message.make_query(subString, dns.rdatatype.NS)
    
                response     = dns.query.udp(query, nameServer)
    
                responseCode = response.rcode()

                #if sth bad happens, thorw an exception
                if responseCode != dns.rcode.NOERROR:
                    raise DNSException("AN ERROR OCCURED")
                
                if len(response.authority) > 0:
                    rrset = response.authority[0]
                else:
                    rrset = response.answer[0]

                #okay, we achieved to get a response and store it in the rrset
                if len(rrset) > 0:
                    done = True

                    for host in rrset:
                    # we already have a list of nameservers for this domain, this is to get their IP addresses
                        if host.rdtype == dns.rdatatype.SOA:
                            print ('Same server is authoritative for {}'.format(sub))
                        else:
                            authority = host.target

                            if depth == 3:

                                ipv4 = defaultResolver.query(authority).rrset[0]

                                ipv6 = None

                                #might have an ipv6
                                try:
                                    ipv6 = defaultResolver.query(authority, rdtype=dns.rdatatype.AAAA).rrset[0]
                                except DNSException as e:
                                    pass
                                
                                nameServers += ("GLUE4",authority.to_text(),ipv4)

                                nameServers += ("GLUE6",authority.to_text(),ipv6)
                depth += 1
            if done:
                break

    return ("OK",nameServers)
