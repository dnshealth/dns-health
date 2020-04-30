# -*- coding: UTF-8 -*-
#!/usr/bin/env python3
#DNSHEALTH-12
import dns.resolver
from dns.exception import DNSException

def getTheIPofAServer(nameOfTheServer):
    
    temp  = dns.resolver.Resolver().query(nameOfTheServer,'A')

    answer = temp.response.answer[0][0].to_text()

    if answer is not None:
        return {"result": answer, "description": "Checking of authoritative servers", "details": "Successfully found the IP!"}
    else:
        return {"result": -1, "description": "Checking of authoritative servers" ,"details": "No A records for {0} server were found!".format(nameOfTheServer)}

def getAuthServers(domain, name_servers):

    for server in name_servers:

        response = None

        try:

            ip = getTheIPofAServer(server)
            
        except  dns.resolver.NXDOMAIN as e:
                
            return {"result": False, "description" : "Checking of authoritative servers" ,"details": e.msg }

        if ip["result"] == -1 :
            
            return {"result": False, "description" : "Checking of authoritative servers" ,"details": e.msg }

        try:

            var = dns.message.make_query(domain,dns.rdatatype.SOA)

            response = dns.query.udp(var, getTheIPofAServer(server)["result"])
        
        except DNSException as e:
            
            return {"result": -1,"description" : "Checking of authoritative servers", "details": e.msg}

        answer   = response.answer

        if len(answer) == 0:
            return {"result": False ,"description": "Checking of authoritative servers", "details": "Resolved 0 authoritative servers"}

    return {"result": True,"description": "Checking of authoritative servers" ,"details": "Successfully validated authoritative answers"}


def run(domain, list_of_name_servers):
    return getAuthServers(domain,list_of_name_servers)
