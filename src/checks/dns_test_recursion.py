def run(domain, ns, verbose=False):
    res = check_recursive(domain, ns, verbose)
    return {"description": "Check nameservers not recursive", "result": not res}


def check_recursive(q, ns_list, verbose):
    # checks for if RD flag is checked in the response
    # q is for the server outside the jurisdiction of the name servers
    # ns_list is a list of all the name servers to be tested
    import dns.message
    import dns.query
    import socket
    recursion_exists = False
    try:
        for x in ns_list:
            query = dns.message.make_query(q, dns.rdatatype.NS)
            x = socket.gethostbyname(x)
            response = dns.query.udp(query, x)
            s = str(response)
            if "RA" in s: # When "RA" is in the response message then the ns server tells the client that recursion have happened
                recursion_exists = True

                if verbose:
                    print("The name server is set to use recursion when it tried to query", x)
    except socket.gaierror:
        # If we can't reach the server
        return False

    return recursion_exists
    # It will return a boolean of whether recursion occured

