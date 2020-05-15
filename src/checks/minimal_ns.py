import socket

def run(domain, ns):
    res = unique_ns_list(ns)
    return {"description": "Unique Nameservers", "result": res.get("result"), "details": res.get("details")}

def unique_ns_list(l): # Takes in a list
    if test_len(l):    # Tests if the length of the list is greater than 1
        if unique_ip(l): # If that passes it checks for unique ip
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

def unique_ip(l):
    try: 
        y = socket.gethostbyname(l[0]) # Will return the ip adress of the host adress
        l2 = l[1:] # creates a list starting from the second element
        for x in l2: # "for each" loop for every element in the second list
            try:
                if y == socket.gethostbyname(x):
                    return False # if the comparison ever detects same host ip it will return false
                elif len(l2)<2:
                    return True # if the second list is ever lesser than 2 then it will return true
            except Exception:
                pass
        return unique_ip(l2)
    except Exception:
        return False
 
    
    
 # uses recursive calls to return the answer
