import connexion
import six
import os
import sys

path = os.path.dirname(os.getcwd())
sys.path.insert(0, path)

import src.checks as checks
import dns.name
import dns.resolver
import redis
from datetime import datetime
import itertools

from web_api.models.check import Check  # noqa: E501
from web_api.models.inv_par import InvPar  # noqa: E501
from web_api.models.result import Result  # noqa: E501
from web_api import util

TIME_LIMIT = 5

def test_servers(body):  # noqa: E501
    """Send a query to the backend to test name servers

     # noqa: E501

    :param body: Domain and name servers to be tested
    :type body: dict | bytes

    :rtype:(dictionary, int)
    """
    #Converts request to object of type Check
    if connexion.request.is_json:
        body = Check.from_dict(connexion.request.get_json())  # noqa: E501

    #Extract the domain string and name server list and token string from the Check object
    domain = body.domain
    name_servers = body.nameservers
    token = body.token
    delegation = body.delegation

    if delegation == True:
        name_servers = get_nameservers(domain)
    

    #If the field are empty. return an error
    if domain == "" or domain == None or name_servers == [] or name_servers == None or name_servers == [None]:
        return ({"errorDesc": "One of the fields is empty!"}, 400)

    #If the user entered a non valid hostname, stop and don't run the other tests
    if not checks.valid_hostname.run(domain, name_servers).get("result"):
        return ({"errorDesc": "Wrong hostname format"}, 400)
   
    #Checks if a token has been provided
    if token == None or token == "":
        return ({"errorDesc": "No token given!"}, 400)
    
    #Validates token
    if not check_token(token):
        return ({"errorDesc": "Invalid token!"}, 400)

    #Limits the rate at which the user may query the database 
    if not check_time_limit(token):
        return ({"errorDesc": "Too many queries in {0} seconds!".format(TIME_LIMIT)}, 400)
        
            
    # Now, we can start to run the checks. We define a list to which we append the results from each check.
    checks_list = [checks.minimal_ns,
                   checks.valid_hostname,
                   checks.nameserver_reachability,
                   checks.answer_authoritatively,
                   checks.network_diversity,
                   checks.consistency_glue_authoritative,
                   checks.consistent_delegation_zone,
                   checks.consistent_authoritative_nameservers,
                   checks.truncref, checks.prohibited_networks,
                   checks.dns_test_recursion, 
                   checks.same_source_address]
    results = []

    # Run each check and append result to results.
    for check in checks_list:
        result = check.run(domain,name_servers)
        # Check if the check returns a boolean or a more advanced dict consisting of a description too.
        if isinstance(result, bool):
            result = {"result": result, "description": str(check.__name__)}
        results.append(result)

    #Gives each check result a unique id and parses and combines them into the correct format
    check_id = 0
    list_of_check_results = []
    for outcome in results:
        details = outcome.get("details") if "details" in outcome else outcome.get("description")
        list_of_check_results.append({"id":check_id, "result": outcome.get("result"), "key": details})
        check_id += 1

    #Creates the necessary JSON response as a dictionary
    response = {"domain": domain, "ns": name_servers, "checks":list_of_check_results}

    #Return the results of the checks and send the 200 OK code
    return (response, 200)

conn_params = {
    "host": "localhost",
    "port": 6379,
    "password": None,
    "db": 0
}

# Check if token given by client is valid
def check_token(token):
    
    # Create a Redis client instance
    r = redis.Redis(**conn_params)
    
    # Check if the token is in the token:set
    if r.hexists("token_hash", token):
        return True
    
    return False

def check_time_limit(token):

    #init a client instance for redis
    r = redis.Redis(**conn_params)

    time = r.hget("token_hash", token)

    actualTime = datetime.strptime(time.decode("utf-8"), "%d-%b-%Y (%H:%M:%S.%f)")

    time_delta = (datetime.now() - actualTime)
    
    total_seconds = time_delta.total_seconds()

    if int(total_seconds) < int(TIME_LIMIT) :
        return False
    
    else:
        #lazy update the set
        r.hdel("token_hash", token)
        
        r.hset("token_hash", token, datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"))
        
        return True


def get_nameservers(domain):

    results = []

    try:
        nameservers = dns.resolver.Resolver().query(domain, "NS")

    except Exception as e:
        print(e)

    for i in nameservers.response.answer[0]:
        results.append(i.to_text())
    return results
