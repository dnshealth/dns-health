#!/usr/bin/env python3
#Program checks if list of nameservers have unique ASN(are diverse)
#Takes hostname and list of nameservers as input
#Returns False if any two ASN of nameservers are equal
#Returns True id all ASN of nameservers are unique
from ipwhois.net import Net
from ipwhois.asn import IPASN
import socket

def run(hostname, list_of_NS):
  description = "Network diversity"
  listASN = []
  
  try:
    for x in list_of_NS:
      #Getting IPs of nameservers
      net = Net(socket.gethostbyname(x))
      obj = IPASN(net)
      #Getting dictionary with AS info for specific IP
      results = obj.lookup()
      #Extracts only ASN from dictionary and adds them to a list
      listASN.append(results.get('asn'))
  except:
    return {"description": "IP address of some nameserver not found", "result": False}
  
  #Checks if all ASN in list are unique
  if len(listASN) > len(set(listASN)):
    return {"description": description, "result": False}
  else:
    return {"description": description, "result": True}