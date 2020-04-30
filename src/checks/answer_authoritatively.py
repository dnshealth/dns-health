# -*- coding: UTF-8 -*-
#!/usr/bin/env python3
#DNSHEALTH-12
import dns.resolver
from dns.exception import DNSException

def getTheIPofAServer(nameOfTheServer):
    
    temp  = dns.resolver.Resolver().query(nameOfTheServer,'A')

    answer = temp.response.answer[0][0].to_text()

    if answer is not None:
        return {"response": answer, "details": "Successfully found the ip of {0}!".format(nameOfTheServer)}
    else:
        return {"response": -1, "details": "No A records for {0} server were found!".format(nameOfTheServer)}

def getAuthServers(domain, name_servers):

    for server in name_servers:

        response = None

        try:

            ip = getTheIPofAServer(server)
            
        except  dns.resolver.NXDOMAIN as e:
                
            return {"response": "error checking the ip of {0}!".format(server) ,"details": e.msg }

        if ip["response"] == -1 :
            return ip

        try:

            var      = dns.message.make_query(domain,dns.rdatatype.SOA)

            response = dns.query.udp(var, getTheIPofAServer(server)["response"])
        
        except DNSException as e:
            
            return {"response": -1, "details": str(e)}

        answer   = response.answer

        if len(answer) == 0:
            return {"response": False , "details": "Resolved 0 authoritative servers"}

    return {"response": True, "details": "Successfully validated authoritative answers"}


def run(domain, list_of_name_servers):
    return getAuthServers(domain,list_of_name_servers)
