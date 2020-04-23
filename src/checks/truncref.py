import sys
import re
import dns.name
import dns.message
import dns.query
import dns.exception



#Loop that tries all servers in case some of them are down/unavailable
def __ask_servers(list_of_servers, request):
    counter = 0
    for server in list_of_servers:
        try:
            response = dns.query.udp(request, server, 0.3)          #Send a request to a DNS server and get the reply
            return ("OK", response)
        except dns.exception.Timeout:                               #If there's a timeout the loop continues and tries the next server
            counter += 1
            if counter == list_of_servers.__len__():                #If all servers are unavailable then the test fails
                return ("Failed", None)
            else:
                continue


#Checks for a server IP addresses from the given section of a DNS server's response 
def __parse_records(list_of_records, pattern, group):
 counter = 0
 servers = []

 #Check all records of response section
 for text_response in list_of_records:
    counter += 1

    record = re.search(pattern, text_response.to_text(), re.VERBOSE)         #Match it with the given regex pattern
    
    if record != None:                                                       #If the match succeeds add the selected part of the record to a list
        servers.append(record.group(group))

    if counter == list_of_records.__len__() and servers.__len__() == 0:     #If there are no matches with the regex then the parsing fails
        return ("Failed", [])

    if  counter == list_of_records.__len__():                               #When all records have been checked, exit loop and return a list of the selected fields
        return ("OK", servers)




def run(domain, list_of_servers):

    details = []
    #Goes through the list of authoritative name servers for the domain and checks each one
    for server in list_of_servers:

        result = __truncref(domain, server)
        details.append(result)
        if not result.get('result'):
            return {"description": "Check for {0} failed with: {1}".format(server, result.get('description')), "result":False, 'details': details}             #If one of them fails the check stops immediately 
        
        else:
            continue
    
    return {"description": "All authoritative name servers passed!", "result":True, "details": details}                                                         #If loop exits without returning all servers passed


def __truncref(domain, authoritative_server):

    #Makes sure that both domains with and without a period at the end work
    authoritative_server = authoritative_server if authoritative_server[-1:] == '.' else authoritative_server + '.'
    domain = domain if domain[-1:] == '.' else domain + '.'


    '''Regex pattern for cheking if the returned record is an A record
        
        Group 1 is the domain of the record
        Group 2 is the TTL
        Group 3 is the class
        Group 4 is the record type(A in this case)
        Group 5 is the data section

        Use this by calling:
            re.search(A_addr_pattern, $TEXTSTRING, re.VERBOSE)

        Where $TEXTSTRING is a record from the response
    '''
    RR_pattern = r'''
    ^               #Check from start of string
    
    (\S+)           #Check if there's a URL    

    \s{1}           #Whitespace

    (\d+)           #TTL field

    \s{1}           #Whitespace

    (IN|CH|HS)      #DNS record class

    \s{1}           #Whitespace

    (A)             #A-type or NS-type record

    \s{1}           #Whitespace

    (\S+)           #Data field of record (IP address in this case)
    
    $               #The end of string should follow

    '''
    #Definitions of the fields as stated in the regex comment
    Domain = 1
    TTL = 2
    Class = 3
    Type = 4
    IP = 5



    #IP addresses for the root servers from a to m
    root_servers = [
        "198.41.0.4", 
        "199.9.14.201",
        "192.33.4.12",
        "199.7.91.13",
        "192.203.230.10",
        "192.5.5.241",
        "192.112.36.4",
        "198.97.190.53",
        "192.36.148.17", 
        "192.58.128.30",
        "193.0.14.129", 
        "199.7.83.42", 
        "202.12.27.33", 
    ]
    

    #Converts string to dns.name.Name object
    domain_name = dns.name.from_text(authoritative_server)
 
   

    #Create a DNS query message asking for the A record of the domain, EDNS is not
    #used since that would result in UDP packets larger than 512 octets.
    request = dns.message.make_query(
        domain_name,             #Name of the query
        'A',                #Type of record
        'IN',               #Record class
        False,              #Should EDNS be used?
    )



    #Queries root servers and fails if they can't be reached
    (message, response_from_root) = __ask_servers(root_servers, request)
    if message != "OK":
        return {"description": "None of the root DNS servers could be reached", "result":False}
        


    #Parses response from root servers to get IP addresses of TLD servers
    (message, TLD_servers) = __parse_records(response_from_root.additional, RR_pattern, IP)
    if message != "OK":
        return {"description": "No usable IP addresses were returned by the DNS root servers", "result":False}
 
    

    #Sends query to one of the TLD servers to get info on the nameservers and their glue records
    (message, response_from_TLD) = __ask_servers(TLD_servers, request)
    if message != "OK":
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
        return {"description": "All authoritative nameservers are not in-bailiwick of th parent zone", "result":True}
    else:
        (message, name_servers) = __parse_records(response_from_TLD.additional, RR_pattern, IP)                         #If all servers are in-bailiwick then parse the additional section for A records

        if name_servers.__len__() >= 1:                                                                                 #Checks that there is at least one A record
            return {"description": "At least one A record found among glue records", "result":True}
        else:
            return {"description": "No A records found", "result":False}
