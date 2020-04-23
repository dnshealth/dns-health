# -*- coding: UTF-8 -*-
#!/usr/bin/env python3
#DNSHEALTH-12
import dns.resolver
from dns.exception import DNSException

def getTheIPofAServer(nameOfTheServer):
    
    temp  = dns.resolver.Resolver().query(nameOfTheServer,'A')

    for i in temp.response.answer:
        for j in i.items:
            return j.to_text()


def getAuthServers(domain, name_servers):

    for server in name_servers:

        response = None

        try:

            var      = dns.message.make_query(domain,dns.rdatatype.SOA)

            response = dns.query.udp(var, getTheIPofAServer(server))
        
        except DNSException:
            return False

        answer   = response.answer

        if len(answer) == 0:
            return False

    return True


def run(domain, list_of_name_servers):
    answer = getAuthServers(domain,list_of_name_servers)

    return {'description':"answer authoritatively", 'result': answer}