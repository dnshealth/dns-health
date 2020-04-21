#!/usr/bin/env python3
#Program checks if list of nameservers have unique ASN(are diverse)
#Takes hostname and list of nameservers as input
#Returns False if any two ASN of nameservers are equal
#Returns True id all ASN of nameservers are unique
from ipwhois.net import Net
from ipwhois.asn import IPASN
from pprint import pprint
import socket

def is_network_diverse(hostname, list_of_NS):
  #Converts input list of nameservers from string to list
  listNS = list(list_of_NS.strip('[]').split(','))
  listASN = []
  
  try:
    for x in listNS:
      net = Net(socket.gethostbyname(x))
      obj = IPASN(net)
      #Get dictionary with AS info for specific IP
      results = obj.lookup()
      #Extracts only ASN from dictionary and adds them to a list
      listASN.append(results.get('asn'))
  except:
    return False
  
  #Checks if all ASN in list are unique
  if len(listASN) > len(set(listASN)):
    return False
  else:
    return True