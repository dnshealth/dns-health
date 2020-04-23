#!/usr/bin/env python3
# Program checks if all nameservers in list refrence each other
# Takes hostname and list of nameservers as input
# Returns False if delegation and zone are not consistent
# Returns True if delegation and zone are consistent
import socket
import dns.resolver


def run(hostname, list_of_NS, verbose=False):
    description = "Consistency between delegation and zone"
    listNSIP = []
    list_of_lists = []
    # Dns resolver initialization
    resolver = dns.resolver.Resolver()

    # Getting nameserver IPs
    try:
        for x in list_of_NS:
            listNSIP.append(socket.gethostbyname(x))
    except socket.gaierror:
        return {"description": "IP for some nameserver could not be found", "result": False}

    try:
        # For every nameserver IP redefine the resolvers nameserver and query the hostname from that nameserver
        for name in listNSIP:
            resolver.nameservers = [name]
            temp = []
            for data in resolver.query(hostname, 'NS'):
                # Appending query results to a temporary list and removing end dot
                temp.append(data.to_text()[:-1])

            # Combining list of results from each query in to list of lists
            list_of_lists.append(sorted(temp))

    # If query is refused return false
    except:
        pass

    # Checking if all nameservers from all queries match the input list of nameservers
    if not all(x == sorted(list_of_NS) for x in list_of_lists):
        return {"description": description, "result": False}
    else:
        return {"description": description, "result": True}
