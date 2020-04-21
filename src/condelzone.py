#!/usr/bin/env python3
#Program checks if all nameservers in list refrence each other
#Takes hostname and list of nameservers as input
#Returns False if delegation and zone are not consistent
#Returns True if delegation and zore are consistent
import socket
import dns.resolver

def is_consistent_delegation_zone(hostname, list_of_NS):
    #Converts second argument from string to list of nameservers
    listNS = list(list_of_NS.strip("[]").split(','))
    listNSIP = []
    list_of_lists = []
    #Dns resolver initialization
    resolver = dns.resolver.Resolver()
    
    #Getting nameserver IPs
    try:
        for x in listNS:
            listNSIP.append(socket.gethostbyname(x))
    except socket.gaierror:
        return False
    
    try:
        #For every nameserver IP redefine the reslovers nameserver and query the hostname from that nameserver
        for name in listNSIP:
            resolver.nameservers = [name]
            temp = []   
            for data in resolver.query(hostname, 'NS'):
                #Appending query results to a temporary list and removing end dot
                temp.append(data.to_text()[:-1])
            
            #Combining list of results from each query in to list of lists
            list_of_lists.append(sorted(temp))
            
    #If query is refused return false
    except dns.resolver.NoNameservers:
        return False

    #Checking if all nameservers from all queries match the input list of nameservers
    return all(x == sorted(listNS) for x in list_of_lists)