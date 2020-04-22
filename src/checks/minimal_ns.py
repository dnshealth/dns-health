import socket


def run(domain, ns, verbose=False):
    res = unique_ns_list(ns, verbose)
    return {"description": "Unique Nameservers", "result": res}


def unique_ns_list(l, verbose): # Takes in a list
    if test_len(l):    # Tests if the length of the list is greater than 1
        if unique_ip(l): # If that passes it checks for unique ip
            if verbose:
                print("The servers are more than 1 and unique")
            return True
        else:
            if verbose:
                print("Though the servers are more than 1, at least 2 of the servers in the list are not unique")
            return False
    else:
        if verbose:
            print("There are less than 2 nameservers ")
        return False


def test_len(l):
    return len(l)>1


def unique_ip(l): 
    y = socket.gethostbyname(l[0]) # Will return the ip adress of the host adress
    l2 = l[1:] # creates a list starting from the second element
    for x in l2: # "for each" loop for every element in the second list
        
        if y == socket.gethostbyname(x):
            return False # if the comparison ever detects same host ip it will return false
        elif len(l2)<2:
            return True # if the second list is ever lesser than 2 then it will return true
 
    
    return unique_ip(l2)
 # uses recursive calls to return the answer
