'''
Written by Kristaps Kalnins <kristapskalnin@gmail.com>
Finished on 18.05.2020
Could still use some more refactoring, some edge cases may not work.
'''
import dns.name
import dns.query
import dns.dnssec
import dns.message
import dns.resolver
import dns.rdatatype
import socket
import src.checks.check_helpers as check_helpers





#Gets DNSKEY records for a given domain from a given nameserver
def get_keys(domain, nameserver):

  #Query server for DNSKEY records
  response = query_servers(domain, nameserver, dns.rdatatype.DNSKEY)

  
  if not response:
    return (None, None, None, None);

  #Parse the answer section to get the keys
  (RRset, KSK, ZSK) = get_DNSKEY_RRset(response.answer)
  RRsig = get_RRsig(response.answer)

  return(RRset, KSK, ZSK, RRsig)
  




#Validates the root server responses and returns IP addresses of the TLD servers
def top_level_domains(domain,root_servers, root_dslist):

  #Try all root servers
  for server in root_servers:

    #Validate root respose
    (validation, RRset) = validate_root(server, root_dslist)
    
    #If the validation succeeds find the TLD servers, otherwise try next root server
    if validation.get('result'):

      #This domain is used in the validation of DS records
      domain = prepare_domain(domain)
      domain = domain[0] + '.'

      return next_in_recurssion('.', domain, server, RRset)







#Parse the given section of a DNS response for DS records 
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
      
  #Along with the DS records, return their RRsig record
  return (child_ds, child_algo, get_RRsig(section))



#Parse section for SOA records
def get_SOA_RRset(section):
  RRset = None
  for sets in section:
    if sets.rdtype == dns.rdatatype.SOA:
      RRset = sets

  return RRset




#Parse response section for DNSKEY records
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


#Parse DNS response section for RRSii records
def get_RRsig(section):
  for sets in section:
    if sets.rdtype == dns.rdatatype.RRSIG:
      return sets

  return None








#Used to check addition section of a response for glue records
def check_additional_section(section):
  servers = []
  for record in section:
    servers.append(record[0].to_text())
  if len(servers) > 0:
    return servers
  else:
    return False

#Checks for NS records in a section, used when there are no glue records
def check_authority_NS(section):
  list_of_NS = []
  for RRset in section:
    if RRset.rdtype == dns.rdatatype.NS:
      for NS in RRset:
        list_of_NS.append(NS.to_text())

  return list_of_NS



#Function for querying a DNS server for a specific domain and resource rescord
def query_servers(domain, server, type):

  #Create the query message, using the domain and RR type, and enable DNSSEC
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




#Function for hashing a DNSKEY using a given domain and hashin algorithm
def hash_key(domain, key, algorithm):
  return dns.dnssec.make_ds(domain, key, algorithm)






#Validates a RRset against a RRsig and DNSKEY records
def RRset_val(RRset, RRsig, keys, domain):
  try:
    dns.dnssec.validate(RRset, RRsig, {dns.name.from_text(domain):keys})
  except dns.dnssec.ValidationFailure as e:
    return {"result":False, "details":"RRSIG validation failed with {0}".format(e.msg)}

  return {"result": True, "details": "Validation succeeded"}






#Check for a match between parent zone DS RR and hashed child zone DNSKEY RR 
def hash_match(list_of_ds, hashed_key):
  hashtest = False
  
  for ds in list_of_ds:
    if ds == hashed_key:
      hashtest = True
      break
  
  
  if not hashtest:
    return {"result":False, "details":"Hashed DNSKEY does not match parent DS record hash"}

  return {'result': True, 'details': 'Hashed keys match'}


    

#Executes the two functions above multiple times until a match and validation succeeds, otherwise fail
def validate(domain, list_of_keys, RRsig, RRset, child_ds, child_algo, keys):

  if not list_of_keys or not child_algo or not child_ds:
    return {'result': False, 'details':'No DS records for {0}'.format(domain)}

  for key in list_of_keys:
    
    
   
    hashed_key = hash_key(domain, key, child_algo)
   
    match = hash_match(child_ds, hashed_key)
    if not match.get('result'):
      continue
      

    res = RRset_val(RRset, RRsig, keys, domain)


    if res.get('result'):
      return res
    
  return {'result': False, 'details': 'No matching DS and hashed DNSKEY records for {0}'.format(domain)}



  
#The DS records for the root are give as strings, so the root validation needs a separate function
def validate_root(nameserver, root_dslist):

  (RRset, KSK, ZSK, RRsig_set) =get_keys('.', nameserver)


  #The DS record needs to be cast to string since the root anchors are givens as strings
  if not KSK:
    return {'result':False, 'details':'Could not retrieve keys from root'}
  hashed_key = str(dns.dnssec.make_ds('.', KSK[0], 'sha256'))

  match = hash_match(root_dslist, hashed_key)
  if not match.get('result'):
    return (match, RRset)
  
  return (RRset_val(RRset, RRsig_set, RRset ,'.'), RRset)




#Used to get the next servers in the recursion
def next_in_recurssion(parent_domain, subdomain, server, keys):

 
  #Query server for DS records
  response = query_servers(subdomain, server, dns.rdatatype.DNSKEY)

  
  if not response:
    return False

 
  #Parse for DS records
  (child_ds, child_algo, RRsig) = get_DS(response.authority)

  #Validate the DS records
  if child_ds and child_algo and RRsig:
    result = RRset_val(child_ds, RRsig, keys, parent_domain)
    if not result.get('result'):
      return {'result':False, 'details':'DS validation failed'}
   
  




  #if there is answer section or there is soa type in authority field this is our server IP
  if (len(response.answer) > 0 or ((len(response.authority) > 0) and (response.authority[0].rdtype == dns.rdatatype.SOA))):
    return ([server], child_ds, child_algo)

  #Check the additional section if there is no SOA record
  additional_servers = check_additional_section(response.additional)
  
  if additional_servers:
    return (additional_servers, child_ds, child_algo)
    
  #If there are no glue records, find the NS records and resolve them
  auth_ns = check_authority_NS(response.authority)
  
  
  for ns in auth_ns:
    
  
    result_of_resolve = check_helpers.getTheIPofAServer(ns, False, None)
    if result_of_resolve.get('result'):
      return ([result_of_resolve.get('result')], child_ds, child_algo)
    
    
  return (None, None, None)


    

  return None

#Try all current servers to find next severs
def get_next_servers(parent_domain, subdomain, current, keys):
  for server in current:
    try:
      (next_servers, child_ds, child_algo) = next_in_recurssion(parent_domain, subdomain, server, keys)
      if(next_servers):
        return (next_servers, child_ds, child_algo)
    except:
      pass

  return [], None, None
  

#Splits the domain name into parts to make it easier to query servers for the keys
def prepare_domain(domain):

  #Check for '.' at the end of the domain and remove it if it's there
  domain = domain if domain[-1:] != '.' else domain[:-1]
  
  #Split the domain into parts
  layers = domain.split(".")
  
  #Reverse the list, so the queries can be started from the TLDs
  layers.reverse()
  return layers



def run(domain, nameservers, ipv6):

  details = ''
  resolved = []
  failed = []
  name_failed = []
  out = True

  #Find IPs of the nameservers
  for ns in nameservers:
    resolve = check_helpers.getTheIPofAServer(ns, ipv6, None).get('result')
    if not resolve:
      failed.append(resolve)
      name_failed.append(ns)
      resolved.append(resolve)
    else:
      resolved.append(resolve)

  
  dict_of_ns = dict(zip(resolved, nameservers))

  #If some of the server IPs can't be resolved, fail the test
  if len(failed) > 0:
    failed = dict(zip(name_failed, failed))
    details = "Could not resolve IPs for: "
    for key in failed:
      details = details + key +'<br>'
    return {'result':False, 'description':'DNSSEC compiance validation', 'details':details}

  

  #Do the test for each name server, to validate the secure chain
  for server in resolved:
    res = dnssec_check(domain, [server], ipv6)
    if not res.get("result"):
      out = False
      details =  details + "{0} failed with {1}".format(dict_of_ns.get(server), res.get('details')) + '<br>'

  #If none of the servers returned a False the out stays True and all servers pass
  if out:
    details = "All servers validated!"
  

  return {'result':out, 'description':'DNSSEC compliance validation', 'details': details} 


def dnssec_check(domain, nameserver, ipv6):

  #Preserve the original domain for responses
  original_domain = domain

  #Splits domain into 
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

  #Root server anchors used for verifying the response from the root servers
  root_dslist = ['19036 8 2 49aac11d7b6f6446702e54a1607371607a1a41855200fd2ce1cdde32f24e8fb5',
  '20326 8 2 e06d44b80b8f1d39a95c0b0d7c65d08458e880409bbc683457104237c7f8ec8d']

  
  #Prepare query for the top level domain
  query = list_of_levels[0] + "."
  

  #Returns IPs of TLD servers and their DS records
  (current_level_servers, child_ds, child_algo) = top_level_domains(domain, root_servers, root_dslist)
 
  #Verfies and matches DS to DNSKEY records 
  for domain in list_of_levels[1:]:

    
    for server in current_level_servers:
       
      #Retrieve the DNSKEY RRset and the RRsig for that DNSKEY record
      (RRset, KSK, ZSK, RRsig) = get_keys(query, server)
      if RRset and KSK and ZSK and RRsig:
        break
      
    
    #If there are no keys try again using the next subdomain  
    if not RRset or not KSK or not ZSK or not RRsig:
        query = domain + '.' + query
        continue

    
    
    #If you DO get keys than validate both the parent zone DS with the child zone DNSKEY, also to an RRSIG validation for the keys
    validation_result = validate(query, KSK, RRsig, RRset, child_ds, child_algo, RRset)


    #If the validation fails return
    if not validation_result.get("result"):
      return {'result':False, 'details':'{0} level failed with {1}'. format(domain, validation_result.get('details'))}

   #Keep track of higher domain and continue the query for lower domains
    parent_domain = query
    query = domain + '.' + query


    #if no servers were found for the next level, break
    if not current_level_servers:
      break

    #Retreive DS records for child zone  and get next level of servers either from glue or resolve them
    (next_level_servers, child_ds, child_algo) = get_next_servers(parent_domain, query, current_level_servers, RRset)
  
    #Replace the current servers with the next ones
    current_level_servers = next_level_servers



  
  #Now we do the last part, where we ask the authoritative nameserver for keys and verify an A or AAAA record
  
  #If there are no DNSKEY RRsets ot RRsig, the check fails
  if not RRset or not KSK or not ZSK or not RRsig:
        try:
          
          name = socket.gethostbyaddr(nameserver[0])[0]
        except socket.herror:
          name = nameserver[0]

        return {'result': False, 'details':'No keys or signitures for {0} from {1}'.format(query, name)}

  #Check if the server returns a SOA record for the query to check if it's the authoritative name server


  #Try to get keys from the nameservers provided by the user
  for auth_ns in nameserver:
    (RRset, KSK, ZSK, RRsig) = get_keys(query, auth_ns)
    if RRset and KSK and ZSK and RRsig:
      break
    
        
  #If you cannot get keys from the servers, exit the program
  if not RRset or not KSK or not ZSK or not RRsig:
      try:
        name = socket.gethostbyaddr(auth_ns)[0]
      except socket.herror:
        name = auth_ns

      return {'result': False, 'details':'No keys or signitures for {0} from {1}'.format(query, name)}
  

  #Validate the TLD DS record with the DNSKEY record of the authoritative nameserver
  validation_result = validate(query, RRset, RRsig, RRset, child_ds, child_algo,  RRset)

  
  
  #If the validation fails, return
  if not validation_result.get("result"):
    return {'result':False, 'details':validation_result.get('details')}



  #After the last zone verification, ask for the SOA record, if in ipv6 mode
  for auth_ns in nameserver:
    response = query_servers(query, auth_ns, dns.rdatatype.SOA)
    if  response != False:
      break
  

  if response == False:
    return {'result': False, 'details':'Could not get response from authoritative name server'}

  RRset_SOA = get_SOA_RRset(response.answer)
 
  RRsig_SOA = get_RRsig(response.answer)
  
  
  #If no SOA record could be retrieved, the test fails and returns
  if not RRset_SOA:
    return {'result': False, 'details':'No SOA records for {0}'.format(query)}
  if not RRsig_SOA:
    return {'result': False, 'details':'SOA records not signed'}

  #Validate the SOA record with it's RRsig and DNSKEY records
  res = RRset_val(RRset_SOA, RRsig_SOA,  RRset, query)

  #If the validation succeeds return a passing result, otherwise fail
  if res.get('result'):
    return {'result': True, 'details': "Securely retrived SOA record for {0}".format(original_domain)}

  return {'result': False, 'details' : 'Could not verify SOA record of {0}'.format(original_domain)}
  
