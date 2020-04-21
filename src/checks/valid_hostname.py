#!/usr/bin/env python3
#Program checks if given hostname is valid
#Takes hostname and list of nameservers as input
#Returns False if hostname is not valid
#Returns True if hostname is valid
import re

def run(hostname, list_of_NS):
  description = "Valid hostnames"

  #Check if hostname correct length
  if len(hostname) > 255: 
    return False
  
  if hostname[-1] == ".":
    #strip end dot, if present
    hostname = hostname[:-1]  
  
  #regex to check for invalid simbols
  allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE) 
  #Return True if all parts of hostname are valid
  result = all(allowed.match(x) for x in hostname.split(".")) 
  # Also check that the nameservers have correct format
  result &= all(allowed.match(y) for x in list_of_NS for y in x.split("."))
  return {"description": description, "result": result}
