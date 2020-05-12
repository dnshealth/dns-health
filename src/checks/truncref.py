import sys
import re
import dns.name
import dns.message
import dns.query
import dns.exception
import check_helpers as helpers

def DESCRIPTION():
    return "No truncation of referrals"

def truncref(domain, authoritative_server,ipv6):

    #Makes sure that both domains with and without a period at the end work
    authoritative_server = authoritative_server if authoritative_server[-1:] == '.' else authoritative_server + '.'
    domain = domain if domain[-1:] == '.' else domain + '.'

    #Definitions of the fields as stated in the regex comment
    Domain = 1
    TTL = 2
    Class = 3
    Type = 4
    IP = 5

    #Converts string to dns.name.Name object
    domain_name = dns.name.from_text(authoritative_server)
 
    #Create a DNS query message asking for the A record of the domain, EDNS is not
    #used since that would result in UDP packets larger than 512 octets.

    request = None

    if ipv6:

        request = dns.message.make_query(
         domain_name,             #Name of the query
         'AAAA',                #Type of record
         'IN',               #Record class
         False,              #Should EDNS be used?
        )

    else:
        request = dns.message.make_query(
         domain_name,             #Name of the query
         'A',                #Type of record
         'IN',               #Record class
         False,              #Should EDNS be used?
        )

    #Queries root servers and fails if they can't be reached
    (message, response_from_root) = helpers.ask_servers(helpers.ROOT_SERVERS(), request)
    if message != True:
        return {"description": "None of the root DNS servers could be reached", "result":False}
        
    #Parses response from root servers to get IP addresses of TLD servers
    (message, TLD_servers) = helpers.parse_records(response_from_root.additional, helpers.RR_PATTERN(), IP)
    if message != True:
        return {"description": "No such Top-level domain", "result":False}
 
    #Sends query to one of the TLD servers to get info on the nameservers and their glue records
    (message, response_from_TLD) = helpers.ask_servers(TLD_servers, request)
    if message != True:
        return {"description": "None of the TLD DNS servers could be reached", "result":False}

    #Extracting the domain names of the authoritative name servers from the TLD server response
    domains = []
    for data in response_from_TLD.authority[0]:
        domains.append(data.to_text())

    #Comparing the TLDs of the authoritative name server and the returned name servers
    TLD_matches = 0
    for names in domains:
        if re.search(r'(\.[^\.]+\.)$', names).group(0) == re.search(r'(\.[^\.]+\.)$', authoritative_server).group(0):
            TLD_matches += 1

    #Check if all authoritative name servers are in-bailiwick of the parent zone
    if TLD_matches != domains.__len__():
        return {"description": "All authoritative nameservers are not in-bailiwick of the parent zone", "result":True}
    else:
        (message, glue) = helpers.parse_records(response_from_TLD.additional, helpers.RR_PATTERN(), IP)                         #If all servers are in-bailiwick then parse the additional section for A records

        if glue.__len__() >= 1 and domains.__len__() >= 2:                                                      #Checks that there is at least one A record and at least two name servers
            return {"description": "At least one A record found among glue records", "result":True}
        
        else:                                                                                                   #Otherwise fail -> there are no glue records
            return {"description": "No glue records found", "result":False}

def run(domain, list_of_servers,ipv6):

    test_result = True
    #Goes through the list of authoritative name servers for the domain and checks each one
    for server in list_of_servers:

        result = truncref(domain, server,ipv6)

        if not result.get("result"):
            test_result = False
            break                                                                                                                               #If one of them fails the check stops immediately 
        
        else:
            continue

    if test_result == False:
        response  = server + " failed with: {0}".format(result.get("description"))
    else:
        response = "All servers passed"

    return {"description": DESCRIPTION(), "result":test_result, "details": response}                                               #If loop exits without returning all servers passed
