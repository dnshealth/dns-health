# -*- coding: UTF-8 -*-
#!/usr/bin/env python3
#DNSHEALTH-14
import dns, dns.resolver, dns.query, dns.name
from dns.exception import DNSException
import checks.check_helpers as helpers

def DESCRIPTION():
    return "Check glue consistency"

def getGlueRecords(domain, list_of_name_servers,ipv6):

    #ietrate over the list of name servers given so we can test them again the actual ip's and server names
    for server in list_of_name_servers:

        server.split(".")

        query = dns.message.make_query(server, dns.rdatatype.A)
        
        (_, response_from_the_servers) = helpers.ask_servers(helpers.ROOT_SERVERS(),query)

        try:
            answer = response_from_the_servers.additional

            (_,response) = helpers.parse_records(answer,helpers.RR_PATTERN(),5)
       
        except Exception as e:
            
            return {"result": False, "description" :  DESCRIPTION() ,"details": e.msg}

        (_, response_from_the_servers)= helpers.ask_servers(response,query)

        additional_section = response_from_the_servers.additional

        correct_servers = []

        if ipv6:
            for tempo in additional_section:
                if ' IN AAAA ' in tempo.to_text():
                    correct_servers.append(tempo)
        else:
            for tempo in additional_section:
                if ' IN A ' in tempo.to_text():
                    correct_servers.append(tempo)
        

        results = {}

        #build the dictionary based on the additional section of the response we got the server
        for entry in correct_servers:

            name_of_the_server = entry.name.to_text().strip(".")
            
            if name_of_the_server in results :
                results[name_of_the_server].append(entry[0].to_text())
            else:
                results[name_of_the_server] = [entry[0].to_text()]

            if name_of_the_server not in list_of_name_servers:
                results.pop(name_of_the_server,None)

        #get all the ipv4 and ipv6 addresses and compare them against the dictionary we built
        for i in list_of_name_servers:

            ip_query = None

            if ipv6:
                ip_query = dns.message.make_query(i,dns.rdatatype.AAAA)
            else:
                ip_query = dns.message.make_query(i,dns.rdatatype.A)
            
            ip = helpers.getTheIPofAServer(server,ipv6,DESCRIPTION())
            
            if ip["result"] == False:
                return ip

            ip_reponse_of_the_name_server = dns.query.udp(ip_query,ip["result"])

            ip_answer_of_the_name_server = ip_reponse_of_the_name_server.answer
            
            #basically, our solution works like that. for every ip we get for every server, we delete them from the dictionary.
            #if the dictionary has some extra addresses or one of the results and not in the dictionary, return false.

            for ip["result"] in ip_answer_of_the_name_server:
                if i in results:
                    if ip["result"][0].to_text() not in results[i]:
                        return {"result": False,"description":DESCRIPTION(), "details": "{0} could not be found in the glue records for ipv4 addresses".format(ip["result"][0].to_text())}

                    results[i].remove(ip["result"][0].to_text())

        for _,value in results.items():
            if len(value) != 0:
                return {"result": False, "description": DESCRIPTION(), "details": "Extra addresses were found when queried the servers!({0})".format(value)}
        return {"result": True,"description":DESCRIPTION(), "details": "Sucess! There is consistency between glue and authoritative data!"}

def run(domain, list_of_name_servers,ipv6):
    return getGlueRecords(domain,list_of_name_servers,ipv6)

print(run("kth.se",["a.ns.kth.se", "b.ns.kth.se"],True))