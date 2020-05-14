import dns.message
import dns.query
import src.checks.check_helpers as helpers

def DESCRIPTION():
    return "Check whether nameservers are recursive or not"

def check_recursive(q, ns_list,ipv6):
    # checks for if RD flag is checked in the response
    # q is for the server outside the jurisdiction of the name servers
    # ns_list is a list of all the name servers to be tested

    for x in ns_list:
        
        try:
            
            query = dns.message.make_query(q, dns.rdatatype.NS)
        
            y = helpers.getTheIPofAServer(x,ipv6,DESCRIPTION())
            
            response = dns.query.udp(query, y)
            
            s = str(response)
            
            if "RA" in s: # When "RA" is in the response message then the ns server tells the client that recursion have happened
                
                return {"result": True, "details": "Recursion has been detected because RA was found in the response message from {0}".format(x)}
          
        except Exception:
            pass

    
    return {"result": False, "details": "no recursion"}

    # It will return a boolean of whether recursion occured

def run(domain, ns,ipv6):
    res = check_recursive(domain, ns,ipv6)
    return {"description":DESCRIPTION(), "result": not res.get("result"), "details": res.get("details")}
