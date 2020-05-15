import src.checks.check_helpers as helpers

def DESCRIPTION():
    return "Unique Nameservers"

def unique_ns_list(l,ipv6): # Takes in a list
    if test_len(l):    # Tests if the length of the list is greater than 1
        if unique_ip(l,ipv6): # If that passes it checks for unique ip
            # print("The servers are more than 1 and unique")
            return {"result": True, "details": "Passed"}
        else:
            # print("Though the servers are more than 1, at least 2 of the servers in the list are not unique")
            return {"result": False, "details": "Though the servers are more than 1, at least 2 of the servers in the list are not unique"}
    else:
        # print("There are less than 2 nameservers ")
        return {"result": False, "details": "There are less than 2 nameservers"}
    
def test_len(l):
    return len(l)>1

def unique_ip(l,ipv6):
    try: 
        y =  helpers.getTheIPofAServer(l[0],ipv6,DESCRIPTION()) # Will return the ip adress of the host adress
        l2 = l[1:] # creates a list starting from the second element
        for x in l2: # "for each" loop for every element in the second list
            try:
                if y == helpers.getTheIPofAServer(x,ipv6,DESCRIPTION()):
                    return False # if the comparison ever detects same host ip it will return false
                elif len(l2)<2:
                    return True # if the second list is ever lesser than 2 then it will return true
            except Exception:
                pass
        return unique_ip(l2,ipv6)
    except Exception:
        return False
 
def run(domain, ns,ipv6):
    res = unique_ns_list(ns,ipv6)
    return {"description": DESCRIPTION(), "result": res.get("result"), "details": res.get("details")}

 # uses recursive calls to return the answer
