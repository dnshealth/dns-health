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
            if counter == list_of_servers.__len__():                  #If all servers are unavailable then the test fails
                return ("Failed", None)
            else:
                continue



def __parse_for_IP(list_of_records, pattern):
 counter = 0
 servers = []
 for text_response in list_of_records:
    counter += 1

    record = re.search(pattern, text_response.to_text(), re.VERBOSE)

    if record != None:
        servers.append(record.group(5))

    if counter == list_of_records.__len__() and servers.__len__() == 0:
        print("\nCan't get IP address of servers")
        print("\nTest Failed!")
        return ("Failed", None)

    if  counter == list_of_records.__len__():
        return ("OK", servers)



def size_check(domain):


    '''Regex pattern for cheking if the returned record under "Additional" is an A record
        
        Group 1 is the URL of the record
        Group 2 is the TTL
        Group 3 is the class
        Group 4 is the record type(A in this case)
        Group 5 is the data section

        Use this by calling:
            re.search(A_addr_pattern, $TEXTSTRING, re.VERBOSE)

        Where $TEXTSTRING is a record from the response
    '''


    A_addr_pattern = r'''
    ^               #Check from start of string
    
    (\S+)           #Check if there's a URL    

    \s{1}           #Whitespace

    (\d+)           #TTL field

    \s{1}           #Whitespace

    (IN|CH|HS)      #DNS record class

    \s{1}           #Whitespace

    (A)             #A-type record

    \s{1}           #Whitespace

    (\d{1,3}        #At least 1 to 3 digits for first field of IP address
    
    \D{1}           #A non decimal '.' sepetator        

    \d{1,3}         #1 to 3 digits for the second field

    \D{1}           #Another seperator period

    \d{1,3}         #Third field of IP address

    \D{1}           #Seperator

    \d{1,3})        #Last field of IP
    
    $               #The end of string should follow

    '''

    number_of_root_servers = 13


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
    domain = dns.name.from_text(domain)
 
   

    #Create a DNS query message asking for the A record of the domain, EDNS is not
    #used since that would result in UDP packets larger than 512 octets.
    request = dns.message.make_query(
        domain,             #Name of the query
        'A',                #Type of record
        'IN',               #Record class
        False,              #Should EDNS be used?
    )




    '''
    Note for tomorrow (21.04.2020)
    Makes this a function in case of referrals
    test with amazon.co.jp if you don't remember
    '''
    (message, response_from_root) = __ask_servers(root_servers, request)
    if message != "OK":
        print("Can't contact root servers")
        print("Test failed")
        return False;
        

    #Checks for a TLD server IP address from the additional section of the root servers response 
    (message, TLD_servers) = __parse_for_IP(response_from_root.additional, A_addr_pattern)
    if message != "OK":
        print("No usable IP adresses in response")
        print("Test failed")
        return False;
 
    
    #Sends query to one of the TLD servers to get info on the nameservers and their glue records
    (message, response_from_TLD) = __ask_servers(TLD_servers, request)
    if message != "OK":
        print("Can't contact TLD servers")
        print("Test failed")
        return False;


    print(response_from_TLD)

    (message, name_servers) = __parse_for_IP(response_from_TLD.additional, A_addr_pattern)
    if message != "OK":
        print("No usable IP adresses in response")
        print("Test failed")
        return False;
   

    print("Test Passed!")
    return True
  

    
   

if __name__ == "__main__":
    size_check('amazon.co.jp')


