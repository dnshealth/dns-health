# -*- coding: UTF-8 -*-
#!/usr/bin/env python3
#DNSHEALTH-12
import dns.resolver
from dns.exception import DNSException

def getTheIPofAServer(nameOfTheServer, ipv6_enabled):
   
    try:
        if(ipv6_enabled):
            temp  = dns.resolver.Resolver().query(nameOfTheServer,'AAAA')
        else:
            temp  = dns.resolver.Resolver().query(nameOfTheServer,'A')
        

    except Exception as e:

        return {"result": False, "description": "Checking for authoritative answers" ,"details": e.msg}

    answer = temp.response.answer[0][0].to_text()

    if answer is not None:
        return {"result": answer, "description": "Checking for authoritative answers", "details": "Successfully found the IP!"}
    elif ipv6_enabled:
        return {"result": False, "description": "Checking for authoritative answers" ,"details": "No AAAA records for {0} server were found!".format(nameOfTheServer)}
    else:
        return {"result": False, "description": "Checking for authoritative answers" ,"details": "No A records for {0} server were found!".format(nameOfTheServer)}

def getAuthServers(domain, name_servers, ipv6_enabled):

    for server in name_servers:

        response = None

        try:

            ip = getTheIPofAServer(server, False)
            
        except Exception as e:
                
            return {"result": False, "description" : "Checking for authoritative answers" ,"details": e.msg }

        if ip["result"] == False :
            
            return ip

        try:

            var = dns.message.make_query(domain,dns.rdatatype.SOA)

            response = dns.query.udp(var, getTheIPofAServer(server, False)["result"])
        
        except DNSException as e:
            
            return {"result": -1,"description" : "Checking for authoritative answers", "details": e.msg}

        answer   = response.answer

        if len(answer) == 0:
            return {"result": False ,"description": "Checking for authoritative answers", "details": "Resolved 0 authoritative servers"}

    return {"result": True,"description": "Checking for authoritative answers" ,"details": "Successfully validated authoritative answers"}


def run(domain, list_of_name_servers, ipv6_enabled):
    return getAuthServers(domain,list_of_name_servers, ipv6_enabled)
