#!/usr/bin/env python3
# Program checks if all authoritative nameserver SOA and NS records are consistent
# Takes hostname and list of nameservers as input
# Returns False if query fails or nameserver IP can not be resolved
# Returns False if NS records or SOA records are not consistent
# Returns True if NS records and SOA records are consistent; contain the same information
import socket
import dns.resolver


def run(hostname, list_of_NS, verbose=False):
    # Filter out duplicate nameserver entries
    list_of_NS = set(list_of_NS)
    description = "Consistent authoritative nameservers"
  
    # Check if nameserver NS records are consistent if not return False
    if not consistent(hostname, list_of_NS, 'NS'):
        return {"description": "NS records are not consistent", "result": False}
    else:
        pass
  
    # Check if nameserver SOA records are consistent if not return False
    if not consistent(hostname, list_of_NS, 'SOA'):
        return {"description": "SOA records are not consistent", "result": False}
    else:
        return {"description": description, "result": True}


def consistent(hostname, list_of_NS, qtype):
    listNSIP = []
    list_of_lists = []
    # Dns resolver initialization
    resolver = dns.resolver.Resolver()
    
    # Getting nameserver IPs
    try:
        for x in list_of_NS:
            listNSIP.append(socket.gethostbyname(x))
    except socket.gaierror:
        return False
    
    try:
        # For every nameserver IP redefine the reslovers nameserver and query the hostname from that nameserver
        for name in listNSIP:
            resolver.nameservers = [name]
            temp = []   
            for data in resolver.query(hostname, qtype):
                # Appending query results to a temporary list and removing end dot
                if data.to_text()[-1] == '.':
                  temp.append(data.to_text()[:-1])
                else:
                  temp.append(data.to_text())
            
            # Combining list of results from each query in to list of lists
            list_of_lists.append(sorted(temp))
            
    # If query is refused return false
    except dns.resolver.NoNameservers:
        return False
    
    # Check if first query is equal to all other queries as they need to be the same
    if not all(list_of_lists[0] == i for i in list_of_lists):
      return False
    else:
      return True