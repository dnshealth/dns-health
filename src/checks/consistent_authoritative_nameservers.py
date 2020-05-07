#!/usr/bin/env python3
# Program checks if all authoritative nameserver SOA and NS records are consistent
# Takes hostname and list of nameservers as input
# Returns False if query fails or nameserver IP can not be resolved
# Returns False if NS records or SOA records are not consistent
# Returns True if NS records and SOA records are consistent; contain the same information
import dns.resolver


def getTheIPofAServer(nameOfTheServer, ipv6_enabled):
   
    try:
        if(ipv6_enabled):
            temp  = dns.resolver.Resolver().query(nameOfTheServer,'AAAA')
        else:
            temp  = dns.resolver.Resolver().query(nameOfTheServer,'A')
        

    except Exception as e:

        return {"result": False, "description": "Check consistent authoritative nameservers" ,"details": e.msg}

    answer = temp.response.answer[0][0].to_text()

    if answer is not None:
        return {"result": answer, "description": "Check consistent authoritative nameservers", "details": "Successfully found the IP!"}
    elif ipv6_enabled:
        return {"result": False, "description": "Check consistent authoritative nameservers" ,"details": "No AAAA records for {0} server were found!".format(nameOfTheServer)}
    else:
        return {"result": False, "description": "Check consistent authoritative nameservers" ,"details": "No A records for {0} server were found!".format(nameOfTheServer)}

def run(hostname, list_of_NS, ipv6_enabled):
    # Filter out duplicate nameserver entries
    list_of_NS = set(list_of_NS)
    description = "Consistency between authoritative nameservers"

    # Consistent function return tuple with result: True/False and details
    ns_check = consistent(hostname, list_of_NS, 'NS', ipv6_enabled)
    
    # Check if nameserver NS records are consistent if not return False
    if not ns_check[0]:
        return {"description": description, "result": False, "details": ns_check[1]}
    else:
        pass

    # Check if nameserver SOA records are consistent if not return False
    soa_check = consistent(hostname, list_of_NS, 'SOA', ipv6_enabled)
    
    if not soa_check[0]:
        return {"description": description, "result": False, "details": soa_check[1]}
    else:
        return {"description": description, "result": True, "details": soa_check[1]}


def consistent(hostname, list_of_NS, qtype, ipv6_enabled):
    listNSIP = []
    list_of_lists = []
    # Dns resolver initialization
    resolver = dns.resolver.Resolver()

    # Getting nameserver IPs
    for x in list_of_NS:
        listNSIP.append(getTheIPofAServer(x, ipv6_enabled))

    try:
        # For every nameserver IP redefine the reslovers nameserver and query the hostname from that nameserver
        for name in listNSIP:
            resolver.nameservers = [name]
            temp = []
            try:
                for data in resolver.query(hostname, qtype):
                    # Appending query results to a temporary list and removing end dot
                    if data.to_text()[-1] == '.':
                        temp.append(data.to_text()[:-1])
                    else:
                        temp.append(data.to_text())
            except:
                # In the case of an exception, we can just ignore it and go with an empty temp array.
                pass


            # Combining list of results from each query in to list of lists
            list_of_lists.append(sorted(temp))

    # If query is refused return false
    except dns.resolver.NoNameservers as err:
        return (False, str(err) + f": nameserver {name} query was refused")

    # Check if first query is equal to all other queries as they need to be the same
    if not all(list_of_lists[0] == i for i in list_of_lists):
        return (False, "Inconsistent NS or SOA records")
    else:
        return (True, "Consistent NS and SOA records")
