#Program checks if given hostname is valid
#Takes hostname and list of nameservers as input
#Returns False if hostname is not valid
#Rturns True if hostname is valid
import re

def is_valid_hostname(hostname, list_of_NS):
  #check if hostname correct length
  if len(hostname) > 255: 
    return False
  
  if hostname[-1] == ".":
    #strip end dot, if present
    hostname = hostname[:-1]  
  
  #regex to check for invalid simbols
  allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE) 
  #return True if all parts of hostname are valid
  return all(allowed.match(x) for x in hostname.split(".")) 