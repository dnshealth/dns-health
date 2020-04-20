import socket

def unique_ns_list(l):
    if test_len(l):
        if unique_ip(l):
            print("The servers are more than 1 and unique")
            return True
        else:
            print("Though the servers are more than 1, at least 2 of the servers in the list are not unique")
            return False
    else:
        print("There are less than 2 nameservers")
        return False
    
def test_len(l):
    return len(l)>1

def unique_ip(l):
    y = socket.gethostbyname(l[0])
    l2 = l[1:]
    for x in l2:
        
        if y == socket.gethostbyname(x):
            return False
        elif len(l2)<2:
            return True
    
    return unique_ip(l2)
