import dns.name
import dns.query
import dns.dnssec
import dns.message
import dns.resolver
import dns.rdatatype
import dns.rdataclass
import re
import socket
import check_helpers






def get_keys(domain, nameserver):

  response = query_servers(domain, nameserver, dns.rdatatype.DNSKEY)
  
  if not response:
    return (None, None, None, None);

  (RRset, KSK, ZSK) = get_DNSKEY_RRset(response.answer)
  RRsig = get_RRsig(response.answer)

  return(RRset, KSK, ZSK, RRsig)
  



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
    (validation, RRset) = validate_root(server, root_dslist)
    if validation.get('result'):
      domain = prepare_domain(domain)
      domain = domain[0] + '.'
      return next_in_recurssion('.', domain, server, RRset)








def get_DS(section):
 
  child_ds = None
  child_algo = None
  
  for record in section:
    if (record.rdtype == dns.rdatatype.DS):
      child_ds = record
      for DS in record:
        if (DS.digest_type == 1):
          child_algo = ('sha1')
        elif (DS.digest_type == 2):
          child_algo = ('sha256')
      
  
  return (child_ds, child_algo, get_RRsig(section))


def get_A_RRset(section):
  RRset = None
  for sets in section:
    if sets.rdtype == dns.rdatatype.A:
          RRset = sets
          
  
  return RRset


def get_DNSKEY_RRset(section):
  ZSK = []
  KSK = []
  RRset = None
  for sets in section:
    if sets.rdtype == dns.rdatatype.DNSKEY:
      for dnskey in sets:
        RRset = sets
        if dnskey.flags == 257:
          KSK.append(dnskey)
        if dnskey.flags == 256:
          ZSK.append(dnskey)
          
  
  return (RRset , KSK, ZSK)


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
  for RRset in section:
    if RRset.rdtype == dns.rdatatype.NS:
      for NS in RRset:
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
  except:
    return False
  
  return response





def hash_key(domain, key, algorithm):
  return dns.dnssec.make_ds(domain, key, algorithm)







def RRset_val(RRset, RRsig, keys, domain):
  try:
    dns.dnssec.validate(RRset, RRsig, {dns.name.from_text(domain):keys})
  except dns.dnssec.ValidationFailure:
    return {"result":False, "details":"RRSIG validation failed"}
  
  return {"result": True, "details": "Validation succeeded"}







def hash_match(list_of_ds, hashed_key):
  hashtest = False
  
  for ds in list_of_ds:
    if ds == hashed_key:
      hashtest = True
      break
  
  
  if not hashtest:
    return {"result":False, "details":"Hashed DNSKEY does not match parent DS record hash"}

  return {'result': True, 'details': 'Hashed keys match'}


def two_step_validate(domain, hashed_key, dslist, RRsig, RRset, keys):
  
  match = hash_match(dslist, hashed_key)
  if not match.get('result'):
    return match 
  
  return RRset_val(RRset, RRsig, keys ,domain)


def SOA_check(query, parent_domain, current_level_servers, RRset ,keys):
  for server in current_level_servers:
        (RRset_SOA, RRsig)  = get_SOA_keys(query, server)
         
        if RRset_SOA and RRsig:
          return RRset_val(RRset_SOA, RRsig, keys, parent_domain)
        
  return {'result':False, 'details':'No signed SOA records'}



def validate(domain, list_of_keys, RRsig, RRset, child_ds, child_algo, keys):

  if not list_of_keys or not child_algo or not child_ds:
    return {'result': False, 'details':'No keys or DS records'}

  for key in list_of_keys:
    
    
   
    hashed_key = hash_key(domain, key, child_algo)
   
    match = hash_match(child_ds, hashed_key)
    if not match.get('result'):
      continue
    
    res = RRset_val(RRset, RRsig, keys, domain)

    if res.get('result'):
      return res
    
  return {'result': False, 'details': 'No matching DS and hashed DNSKEY records for {0}'.format(domain)}



  

def validate_root(nameserver, root_dslist):

  (RRset, KSK, ZSK, RRsig_set) =get_keys('.', nameserver)


  #The DS record needs to be cast to string since the root anchors are givens as strings
  hashed_key = str(dns.dnssec.make_ds('.', KSK[0], 'sha256'))

  validation_result = two_step_validate('.', hashed_key, root_dslist, RRsig_set, RRset, KSK)

  #Validated ZSK
  return (validation_result, RRset)






def next_in_recurssion(parent_domain, subdomain, server, keys):

 

  response = query_servers(subdomain, server, dns.rdatatype.DNSKEY)

  
  if not response:
    return False

 

  (child_ds, child_algo, RRsig) = get_DS(response.authority)

  if child_ds and child_algo and RRsig:
    result = RRset_val(child_ds, RRsig, keys, parent_domain)
    if not result.get('result'):
      return {'result':False, 'details':'DS validation failed'}
   
  




  #if there is answer section or there is soa type in authority field this is our server IP
  if (len(response.answer) > 0 or ((len(response.authority) > 0) and (response.authority[0].rdtype == dns.rdatatype.SOA))):
    return ([server], child_ds, child_algo)

  additional_servers = check_additional_section(response.additional)
  
  if additional_servers:
    return (additional_servers, child_ds, child_algo)
    

  auth_ns = check_authority_NS(response.authority)
  
  
  for ns in auth_ns:
    
  
    result_of_resolve = check_helpers.getTheIPofAServer(ns, False, None)
    if result_of_resolve.get('result'):
      return ([result_of_resolve.get('result')], child_ds, child_algo)
    
    
  return (None, None, None)


    

  return None


def get_next_servers(parent_domain, subdomain, current, keys):
  for server in current:
    try:
      (next_servers, child_ds, child_algo) = next_in_recurssion(parent_domain, subdomain, server, keys)
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
  

  #Validated DS records
  (current_level_servers, child_ds, child_algo) = top_level_domains(domain, root_servers, root_dslist)
  
  is_SOA = False

  #Verifies up to the authoritative name server
  for domain in list_of_levels[1:]:

    
    
    for server in current_level_servers:
       
      (RRset, KSK, ZSK, RRsig) = get_keys(query, server)
      if RRset and KSK and ZSK and RRsig:
        break
      
    

    if not RRset or not KSK or not ZSK or not RRsig:
        query = domain + '.' + query
        continue
        return {'result': False, 'details':'No keys or signitures for {0} from {1}'.format(query, socket.gethostbyaddr(server)[0])}

    validation_result = validate(query, KSK, RRsig, RRset, child_ds, child_algo, RRset)



    if not validation_result.get("result"):
      return {'result':False, 'details':'{0} level failed with {1}'. format(domain, validation_result.get('details'))}

   
    parent_domain = query
    query = domain + '.' + query

    if not current_level_servers:
      break

    (next_level_servers, child_ds, child_algo) = get_next_servers(parent_domain, query, current_level_servers, RRset)
  

    current_level_servers = next_level_servers

    



  
  #Now we do the last part, where we ask the authoritative nameserver for keys
  
  res = SOA_check(query, parent_domain ,current_level_servers, RRset, ZSK)
  if res.get('result'):
    is_SOA = True
  



  if not is_SOA:
    for auth_ns in current_level_servers:
      (RRset, KSK, ZSK, RRsig) = get_keys(query, auth_ns)
      if RRset and KSK and ZSK and RRsig:
        break
    
        
    
    if not RRset or not KSK or not ZSK or not RRsig:
        return {'result': False, 'details':'No keys or signitures for {0} from {1}'.format(query, socket.gethostbyaddr(server)[0])}
  


    validation_result = validate(query, RRset, RRsig, RRset, child_ds, child_algo,  RRset)

  
  
  
    if not validation_result.get("result"):
      return {'result':False, 'details':validation_result.get('details')}




  for auth_ns in current_level_servers:
    response = query_servers(query, auth_ns, dns.rdatatype.A)
    if  response != False:
      break
  

  if response == False:
    return {'result': False}

  RRset_A = get_A_RRset(response.answer)
  RRsig_A = get_RRsig(response.answer)
 

  if is_SOA:
    query = parent_domain
   

  res = RRset_val(RRset_A, RRsig_A,  RRset, query)

  if res.get('result'):
    list_of_A = []
    for A_record in RRset_A:
      list_of_A.append(A_record.to_text())
    return {'result': True, 'details': "Securely retrived A record for {0}".format(original_domain), 'address': list_of_A}

  return {'result': False, 'details' : 'Could not verify A record of {0}'.format(original_domain)}
  

  
  
if __name__ == "__main__":
  print(dnssec_check("dnssec-deployment.org", []))
  #dnssec_check("iana.org.", [])

  



