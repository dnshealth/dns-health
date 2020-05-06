'''
06.05.2020
Written by Kristaps Kalnins (kristapskalnin@gmail.com)
Checks if there exist DS records for the delegations.
'''
import dns.resolver

def run(domain, name_servers):
  
  result = DS_records(domain)
  result["description"] = "Existence of DS records"

  return  result

def DS_records(domain):

  #Tries to find DS records and returns False if dns.resolver find no DS records
  try:
    response = dns.resolver.query(
      domain,
      "DS",
      "IN")

  except dns.resolver.NoAnswer:

    return {"result": False, "details":"Delegated domain does not have DS records"}

  return {"result": True, "details": "Delegated domain does have DS records"}

  
