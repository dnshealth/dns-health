def check_recursive(ns_list):
    # checks for if RD flag is checked in the response
    import dns.message
    import dns.query
    recursion_exists = False
    for x in ns_list:
        query = dns.message.make_query(x, dns.rdatatype.NS)
        response = dns.message.make_response(query)
        s = str(response)
        if "RD" in s:
            recursion_exists = True
            print("The name server is set to use recursion when it tried to reach", x)
    return recursion_exists