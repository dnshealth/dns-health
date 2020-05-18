import src.checks as checks
import dns
import socket

def IMPORTANT_CHECKS():
    return [checks.valid_hostname,checks.prohibited_networks,checks.nameserver_reachability,
                   checks.dns_test_recursion, checks.answer_authoritatively,checks.same_source_address]
                   
def ADDITIONAL_CHECKS():
    return [checks.consistency_glue_authoritative, checks.consistent_delegation_zone,
    checks.consistent_authoritative_nameservers,
    checks.minimal_ns,checks.network_diversity,checks.truncref,checks.dnssec_main]

def get_details(result, id):
    return {"id" : id, "result" : result.get("result"), "description" : result.get("description"), "details" : result.get("details")}

def important_checks(domain,name_servers,result_list, ipv6):

    id = 0

    for check in IMPORTANT_CHECKS():
        
        result = check.run(domain,name_servers,ipv6)
        
        result_list.append(get_details(result,id))

        id = id + 1

        if not result.get("result"):
            break

def additional_checks(domain,name_servers,result_list,ipv6):

    #find the correct id since the list might grow up over time
    id = len(IMPORTANT_CHECKS()) + 1

    for check in ADDITIONAL_CHECKS():

        result = check.run(domain,name_servers,ipv6)

        result_list.append(get_details(result,id))

        id = id +1

def return_results(domain,name_servers,result_list,ipv6 ):

    important_checks(domain,name_servers,result_list,ipv6)

    if len(result_list)!=len(IMPORTANT_CHECKS()):
        
        return ({"domain": domain, "ns": name_servers, "checks": result_list}, 200)

    additional_checks(domain,name_servers,result_list,ipv6)

    return ({"domain": domain, "ns": name_servers, "checks": result_list}, 200)


def get_nameservers(domain):

    results = []

    try:
        nameservers = dns.resolver.Resolver().query(domain, "NS")

    except Exception as e:
        print(e)
        return None

    for i in nameservers.response.answer[0]:
        results.append(i.to_text())
    return results
