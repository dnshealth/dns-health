#Program checks if given hostname is valid
import re

def is_valid_hostname(hostname):
  if len(hostname) > 255: #check if hostname correct length
    return False
  
  if hostname[-1] == ".":
    hostname = hostname[:-1]  #strip end dot, if present
  
  allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE) #regex to check for invalid simbols
  return all(allowed.match(x) for x in hostname.split(".")) #return True if all parts of hostname are valid