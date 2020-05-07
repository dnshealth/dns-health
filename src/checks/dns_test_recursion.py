import dns.resolver
def run(domain, ns, ipv6_enabled):
    res = check_recursive(domain, ns, ipv6_enabled)
    return {"description": "Check nameservers not recursive", "result": not res.get("result"), "details": res.get("details")}

def check_recursive(q, ns_list, ipv6_enabled):
    # checks for if RD flag is checked in the response
    # q is for the server outside the jurisdiction of the name servers
    # ns_list is a list of all the name servers to be tested
    import dns.message
    import dns.query
    for x in ns_list:
        try:
            query = dns.message.make_query(q, dns.rdatatype.NS)
        
            y = getTheIPofAServer(x, ipv6_enabled)
            response = dns.query.udp(query, y)
            s = str(response)
            if "RA" in s: # When "RA" is in the response message then the ns server tells the client that recursion have happened
                
                return {"result": True, "details": "Recursion has been detected because RA was found in the response message from {0}".format(x)}
                # print("The name server is set to use recursion when it tried to query", x)
        except Exception:
            pass

    
    return {"result": False, "details": "no recursion"}

    # It will return a boolean of whether recursion occured

def getTheIPofAServer(nameOfTheServer, ipv6_enabled):
   
    try:
        if(ipv6_enabled):
            temp  = dns.resolver.Resolver().query(nameOfTheServer,'AAAA')
        else:
            temp  = dns.resolver.Resolver().query(nameOfTheServer,'A')
        

    except Exception as e:

        return {"result": False, "description": "Check dns recursion" ,"details": e.msg}

    answer = temp.response.answer[0][0].to_text()

    if answer is not None:
        return {"result": answer, "description": "Check dns recursion", "details": "Successfully found the IP!"}
    elif ipv6_enabled:
        return {"result": False, "description": "Check dns recursion" ,"details": "No AAAA records for {0} server were found!".format(nameOfTheServer)}
    else:
        return {"result": False, "description": "Check dns recursion" ,"details": "No A records for {0} server were found!".format(nameOfTheServer)}
