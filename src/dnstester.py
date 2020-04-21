def check_recursive(q, ns_list):
    # checks for if RD flag is checked in the response
    import dns.message
    import dns.query
    import socket
    recursion_exists = False
    for x in ns_list:
        query = dns.message.make_query(q, dns.rdatatype.NS)
        x = socket.gethostbyname(x)
        x = "192.168.1.1"
        response = dns.query.udp(query, x)
        s = str(response)
        if "RA" in s: # When "RA" is in the response message then the ns server tells the client that recursion have happened
            recursion_exists = True
            print("The name server is set to use recursion when it tried to query", x)
    return recursion_exists