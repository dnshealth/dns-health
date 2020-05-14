import dns.resolver
from dns.exception import DNSException
import re

 #hard coded list of all the root servers
def ROOT_SERVERS():
    return [
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

def RR_PATTERN():
     return  r'''
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

def getTheIPofAServer(nameOfTheServer, ipv6_enabled,description):
   
    try:
        if(ipv6_enabled):
            temp  = dns.resolver.Resolver().query(nameOfTheServer,'AAAA')
        else:
            temp  = dns.resolver.Resolver().query(nameOfTheServer,'A')
        
    except Exception as e:

        return {"result": False, "description": description ,"details": e.msg}

    answer = temp.response.answer[0][0].to_text()

    if answer is not None:
        return {"result": answer, "description": description, "details": "Successfully found the IP!"}
    elif ipv6_enabled:
        return {"result": False, "description": description ,"details": "No AAAA records for {0} server were found!".format(nameOfTheServer)}
    else:
        return {"result": False, "description": description ,"details": "No A records for {0} server were found!".format(nameOfTheServer)}

#Loop that tries all servers in case some of them are down/unavailable
def ask_servers(list_of_servers, request):
    counter = 0
    for server in list_of_servers:
        try:
            response = dns.query.udp(request, server, 0.3)          #Send a request to a DNS server and get the reply
            return (True, response)
        except dns.exception.Timeout:                               #If there's a timeout the loop continues and tries the next server
            counter += 1
            if counter == list_of_servers.__len__():                #If all servers are unavailable then the test fails
                return (False, None)
            else:
                continue

#Checks for a server IP addresses from the given section of a DNS server's response 
def parse_records(list_of_records, pattern, group):
    counter = 0
    servers = []

    #Check all records of response section
    for text_response in list_of_records:
        counter += 1

        record = re.search(pattern, text_response.to_text(), re.VERBOSE)         #Match it with the given regex pattern
    
        if record != None:                                                       #If the match succeeds add the selected part of the record to a list
            servers.append(record.group(group))

        if counter == list_of_records.__len__() and servers.__len__() == 0:     #If there are no matches with the regex then the parsing fails
            return (False, [])

        if  counter == list_of_records.__len__():                               #When all records have been checked, exit loop and return a list of the selected fields
            return (True, servers)

    return (False, [])


# Function used by consistenctency checks
# Takes "hostname" string, "list_of_NS" list of string, "description" string, "flag" string
# Returns a list of lists of string with nameserver records specified by "flag" (NS, SOA, etc.)
# If error Returns dictionary with "description" key string value, "results" key boolean value, "details" key string value
def consistent(hostname, list_of_NS, description, flag, ipv6):
    listNSIP = []
    list_of_lists = []
    # Dns resolver initialization
    resolver = dns.resolver.Resolver()

    # Getting nameserver IPs
    try:
        for x in list_of_NS:
            listNSIP.append(getTheIPofAServer(x,ipv6,description))
    except Exception as err:
        return (False, str(err) + f": could not resolve IP of nameserver {x}")

    try:
        # For every nameserver IP redefine the resolvers name server and query the hostname from that nameserver
        for name in listNSIP:
            resolver.nameservers = [name]
            temp = []
            try:
                for data in resolver.query(hostname, flag):
                    # Appending query results to a temporary list and removing end dot
                    if data.to_text()[-1] == '.':
                        temp.append(data.to_text()[:-1])
                    else:
                        temp.append(data.to_text())
            except dns.resolver.NoAnswer:
                # If we got no answer from an NS, we could just claim it has no NS records. So temp will remain empty.
                pass

            # Combining list of results from each query in to list of lists
            list_of_lists.append(sorted(temp))
            
    # Throw exception if nameserver query was refused
    except dns.resolver.NoNameservers:
        return {"description": description, "result": False, "details": f"nameserver {name} query was refused"}  

    return list_of_lists