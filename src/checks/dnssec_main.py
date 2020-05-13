import dns.name
import dns.query
import dns.dnssec
import dns.message
import dns.resolver
import dns.rdatatype
import dns.rdataclass
import re
import socket






def get_keys(domain, nameserver):
  response = query_servers(domain, nameserver, dns.rdatatype.DNSKEY)
  
  if not response:
    return (None, None, None);

  (RRset, key) = get_DNSKEY_RRset(response.answer)
  RRsig = get_RRsig(response.answer)

  return(RRset, key, RRsig)
  
def get_SOA_keys(domain, nameserver):
  response = query_servers(domain, nameserver, dns.rdatatype.SOA)
  
  if not response:
    return (None, None)

  RRset = get_SOA_RRset(response.answer)
  RRsig = get_RRsig(response.answer)

  if not RRset:
    RRset = get_SOA_RRset(response.authority)
    RRsig = get_RRsig(response.authority)

  return (RRset, RRsig)





def top_level_domains(domain,root_servers, root_dslist):
  for server in root_servers:
    validation = validate_root(server, root_dslist)
    if validation.get('result'):
      return next_in_recurssion(domain, server)








def get_DS(section):
 
  child_ds = []
  child_algo = None
  
  for record in section:
    if (record.rdtype == dns.rdatatype.DS):
      for DS in record:
        child_ds.append(DS)
        if (DS.digest_type == 1):
          child_algo = ('sha1')
        elif (DS.digest_type == 2):
          child_algo = ('sha256')
      
  
  return (child_ds, child_algo)


def get_A_RRset(section):
  RRset = None
  for sets in section:
    if sets.rdtype == dns.rdatatype.A:
          RRset = sets
          
  
  return RRset


def get_DNSKEY_RRset(section):
  records = []
  RRset = None
  for sets in section:
    if sets.rdtype == dns.rdatatype.DNSKEY:
      for dnskey in sets:
        if dnskey.flags == 257:
          RRset = sets
          records.append(dnskey)
          
  
  return (RRset , records)


def get_SOA_RRset(section):
  for sets in section:
    if sets.rdtype == dns.rdatatype.SOA:
      return sets
  return None


def get_RRsig(section):
  for sets in section:
    if sets.rdtype == dns.rdatatype.RRSIG:
      return sets

  return None









def check_additional_section(section):
  servers = []
  for record in section:
    servers.append(record[0].to_text())
  if len(servers) > 0:
    return servers
  else:
    return False


def check_authority_NS(section):
  list_of_NS = []
  for NS in section[0]:
    list_of_NS.append(NS.to_text())

  return list_of_NS




def query_servers(domain, server, type):

  request = dns.message.make_query(
    domain,
    type,
    "IN",
    want_dnssec=True
  )
  try:
    response = dns.query.tcp(request, server, 1)
    print(response)
    print()   
  except:
    return False

  
  return response





def hash_key(domain, key, algorithm):
  return dns.dnssec.make_ds(domain, key, algorithm)






def two_step_validate(domain, hashed_key, dslist, RRsig, RRset):
  hashtest = False
  
  for ds in dslist:
    if ds == hashed_key:
      hashtest = True
      break

  
  
  
  
  if not hashtest:
    return {"result":False, "details":"Hashed DNSKEY does not match parent DS record hash"}

  print(ds)
  print(hashed_key)
  print()
  
  try:
    dns.dnssec.validate(RRset, RRsig, {dns.name.from_text(domain):RRset})
  except dns.dnssec.ValidationFailure:
    return {"result":False, "details":"RRSIG validation failed"}
  
  
  return {"result": True, "details": "Validation succeeded"}


def SOA_check(query, current_level_servers):
  for server in current_level_servers:
        (RRset, RRsig)  = get_SOA_keys(query, server)
        query = query.split('.', 1)[1]
        print("Got SOA records")
        print(type(RRset))
        print(type(RRsig))
        if RRset and RRsig:
          try:
            dns.dnssec.validate(RRset, RRsig, {dns.name.from_text(query):RRset})
            return{'result': True, 'details':"SOA found and signed"}
          except dns.dnssec.ValidationFailure:
            continue
  return {'result':False, 'details':'No signed SOA records'}



def validate(domain, list_of_keys, RRsig, RRset, child_ds, child_algo):
  for key in list_of_keys:
    
    
   
    hashed_key = hash_key(domain, key, child_algo)
   
    validation = two_step_validate(domain, hashed_key, child_ds, RRsig, RRset)
    if validation.get('result'):
      return validation

  return validation



  

def validate_root(nameserver, root_dslist):

  (RRset, dnskey, RRsig_set) =get_keys('.', nameserver)


  #The DS record needs to be cast to string since the root anchors are givens as strings
  hashed_key = str(dns.dnssec.make_ds('.', dnskey[0], 'sha256'))

  validation_result = two_step_validate('.', hashed_key, root_dslist, RRsig_set, RRset)
  
  
  return validation_result

def next_in_recurssion(domain, server):

 

  response = query_servers(domain, server, dns.rdatatype.DNSKEY)

  
  if not response:
    return False

 

  (child_DS, child_algo) = get_DS(response.authority)

  #if there is answer section or there is soa type in authority field this is our server IP
  if (len(response.answer) > 0 or ((len(response.authority) > 0) and (response.authority[0].rdtype == dns.rdatatype.SOA))):
    return ([server], child_DS, child_algo)

  additional_servers = check_additional_section(response.additional)
  
  if additional_servers:
    return (additional_servers, child_DS, child_algo)
    

  auth_ns = check_authority_NS(response.authority)
  for ns in auth_ns:
    auth_ns = dnssec_check(ns, [])
    if dnssec_check.get('result'):
      return (dnssec_check.get('address'), child_DS, child_algo)
    
  return (None, None, None)


    

  return None


def get_next_servers(current, query):
  for server in current:
    try:
      (next_servers, child_ds, child_algo) = next_in_recurssion(query, server)
      if(next_servers):
        return (next_servers, child_ds, child_algo)
    except:
      pass

  return [], None, None
  
def prepare_domain(domain):
  domain = domain if domain[-1:] != '.' else domain[:-1]
  layers = domain.split(".")
  layers.reverse()
  return layers



def run(domain, nameservers):

  root_servers = [
        "198.41.0.4", 
        "199.9.14.201",
        "192.33.4.12",
        "199.7.91.13",
        "192.203.230.10",
        "192.5.5.241",
        "192.112.36.4",
        "198.97.190.53",
        "192.36.148.17", 
        "192.58.128.30",
        "193.0.14.129", 
        "199.7.83.42", 
        "202.12.27.33", 
    ]

  for server in root_servers:
    try:
      dnssec_check(domain, server)
      print("{0} passed".format(server))
    except AttributeError:
      print("{0} failed".format(server))

def dnssec_check(domain, nameserver):

  original_domain = domain
  list_of_levels = prepare_domain(domain)
  

  #IP addresses for the root servers from a to m
  root_servers = [
        "198.41.0.4", 
        "199.9.14.201",
        "192.33.4.12",
        "199.7.91.13",
        "192.203.230.10",
        "192.5.5.241",
        "192.112.36.4",
        "198.97.190.53",
        "192.36.148.17", 
        "192.58.128.30",
        "193.0.14.129", 
        "199.7.83.42", 
        "202.12.27.33", 
    ]

  root_dslist = ['19036 8 2 49aac11d7b6f6446702e54a1607371607a1a41855200fd2ce1cdde32f24e8fb5',
  '20326 8 2 e06d44b80b8f1d39a95c0b0d7c65d08458e880409bbc683457104237c7f8ec8d']

  

  query = list_of_levels[0] + "."
  
  
  (current_level_servers, child_ds, child_algo) = top_level_domains(domain, root_servers, root_dslist)
  
  is_SOA = False

  #Verifies up to the authoritative name server
  for domain in list_of_levels[1:]:

    
    for server in current_level_servers:
      (name, n1,n2) = socket.gethostbyaddr(server)
      print("Getting keys for {0} from {1}".format(query, name))
      (RRset, key, RRsig) = get_keys(query, server)
      if RRset and key and RRsig:
        print("Received keys from {0}".format(name))
        break

      
    
    if not key:
      break
      
    

    validation_result = validate(query, key, RRsig, RRset, child_ds, child_algo)

    if not validation_result.get("result"):
      return {'result':False, 'details':'{0} level failed with {1}'. format(domain, validation_result.get('details'))}

   

    query = domain + '.' + query

    if not current_level_servers:
      break

    (next_level_servers, child_ds, child_algo) = get_next_servers(current_level_servers, query)


    current_level_servers = next_level_servers

    



  
  #Now we do the last part, where we ask the authoritative nameserver for keys
  
  res = SOA_check(query, current_level_servers)
  if res.get('result'):
    is_SOA = True
  



  if not is_SOA:
    for auth_ns in current_level_servers:
      (RRset, key, RRsig) = get_keys(query, auth_ns)
      if RRset and key and RRsig:
        break
    
  
  

    validation_result = validate(query, key, RRsig, RRset, child_ds, child_algo)

  
  
  
    if not validation_result.get("result"):
      return {'result':False, 'details':'Authoritative level failed with {1}'. format(query, validation_result.get('details'))}

  for auth_ns in current_level_servers:
    response = query_servers(query, auth_ns, dns.rdatatype.A)
    if  response != False:
      break
  

  if response == False:
    return {'result': False}

  RRset_A = get_A_RRset(response.answer)
  RRsig = get_RRsig(response.answer)
 

  print(RRsig, RRset_A)

  try:
    dns.dnssec.validate(RRset_A, RRsig, {dns.name.from_text(query):RRset})
    print("PASSED!")
  except dns.dnssec.ValidationFailure:
    return {"result":False, "details":"RRSIG validation failed"}
  
  
  return {"result": True, "details": "Validation succeeded", "address":current_level_servers}

  

  
  
if __name__ == "__main__":
  dnssec_check("ns-ext.nlnetlabs.nl.", [])
  #dnssec_check("iana.org.", [])

  



