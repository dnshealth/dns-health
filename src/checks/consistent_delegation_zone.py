#!/usr/bin/env python3
# Program checks if all nameservers in list refrence each other
# Takes hostname and list of nameservers as input
# Returns False if delegation and zone are not consistent
# Returns True if delegation and zone are consistent
import socket
import dns.resolver


def run(hostname, list_of_NS):
    description = "Consistency between delegation and zone"
    listNSIP = []
    list_of_lists = []
    # Dns resolver initialization
    resolver = dns.resolver.Resolver()

    # Getting nameserver IPs
    try:
        for x in list_of_NS:
            listNSIP.append(socket.gethostbyname(x))
    except socket.gaierror as err:
        return {"description": description, "result": False, "details": str(err) + f": could not resolve IP of nameserver {x}"}

    try:
        # For every nameserver IP redefine the resolvers name server and query the hostname from that nameserver
        for name in listNSIP:
            resolver.nameservers = [name]
            temp = []
            try:
                for data in resolver.query(hostname, 'NS'):
                    # Appending query results to a temporary list and removing end dot
                    temp.append(data.to_text()[:-1])
            except dns.resolver.NoAnswer:
                # If we got no answer from an NS, we could just claim it has no NS records. So temp will remain empty.
                pass

            # Combining list of results from each query in to list of lists
            list_of_lists.append(sorted(temp))

    # If query is refused return false
    except dns.resolver.NoNameservers:
        return {"description": description, "result": False, "details": f"nameserver {name} query was refused"}

    # Checking if all nameservers from all queries match the input list of nameservers
    if not all(x == sorted(list_of_NS) for x in list_of_lists):
        return {"description": description, "result": False, "details": "Delegation is not consistent with nameserver records"}
    else:
        return {"description": description, "result": True, "detais": ""}
