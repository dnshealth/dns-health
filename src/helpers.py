import src.checks as checks
import dns
import socket

def IMPORTANT_CHECKS():
    return [checks.valid_hostname,checks.prohibited_networks,checks.nameserver_reachability,
                   checks.dns_test_recursion, checks.answer_authoritatively,checks.same_source_address]
                   
def ADDITIONAL_CHECKS():
    return [checks.consistency_glue_authoritative, checks.consistent_delegation_zone,
    checks.consistent_authoritative_nameservers,
    checks.minimal_ns,checks.network_diversity,checks.truncref]

def get_details(result, id):
    return {"id" : id, "result" : result.get("result"), "description" : result.get("description"), "details" : result.get("details")}

def important_checks(domain,name_servers,result_list):

    id = 0

    for check in IMPORTANT_CHECKS():
        
        result = check.run(domain,name_servers)
        
        result_list.append(get_details(result,id))

        id = id + 1

        if not result.get("result"):
            break

def additional_checks(domain,name_servers,result_list):

    #find the correct id since the list might grow up over time
    id = len(IMPORTANT_CHECKS()) + 1

    for check in ADDITIONAL_CHECKS():

        result = check.run(domain,name_servers)

        result_list.append(get_details(result,id))

        id = id +1

def return_results(domain,name_servers,result_list):

    important_checks(domain,name_servers,result_list)

    if len(result_list)!=len(IMPORTANT_CHECKS()):
        
        return ({"domain": domain, "ns": name_servers, "checks": result_list}, 200)

    additional_checks(domain,name_servers,result_list)

    return ({"domain": domain, "ns": name_servers, "checks": result_list}, 200)


# Function used by consistenctency checks
# Takes "hostname" string, "list_of_NS" list of string, "description" string, "flag" string
# Returns a list of lists of string with nameserver records specified by "flag" (NS, SOA, etc.)
# If error Returns dictionary with "description" key string value, "results" key boolean value, "details" key string value
def consistent(hostname, list_of_NS, description, flag):
    listNSIP = []
    list_of_lists = []
    # Dns resolver initialization
    resolver = dns.resolver.Resolver()

    # Getting nameserver IPs
    try:
        for x in list_of_NS:
            listNSIP.append(socket.gethostbyname(x))
    except socket.gaierror as err:
        return {"description": description, "result": False, "details": str(err) + f": could not resolve IP of nameserver {x}"}

    try:
        # For every nameserver IP redefine the resolvers name server and query the hostname from that nameserver
        for name in listNSIP:
            resolver.nameservers = [name]
            temp = []
            try:
                for data in resolver.query(hostname, flag):
                    # Appending query results to a temporary list and removing end dot
                    if data.to_text()[-1] == '.':
                        temp.append(data.to_text()[:-1])
                    else:
                        temp.append(data.to_text())
            except dns.resolver.NoAnswer:
                # If we got no answer from an NS, we could just claim it has no NS records. So temp will remain empty.
                pass

            # Combining list of results from each query in to list of lists
            list_of_lists.append(sorted(temp))
            
    # Throw exception if nameserver query was refused
    except dns.resolver.NoNameservers:
        return {"description": description, "result": False, "details": f"nameserver {name} query was refused"}  

    return list_of_lists