import connexion
import six
from .. import checks
import dns.name
import redis

from swagger_server.models.check import Check  # noqa: E501
from swagger_server.models.inv_par import InvPar  # noqa: E501
from swagger_server.models.result import Result  # noqa: E501
from swagger_server import util


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

    #Extract the domain string and name server list from the Check object
    domain = body.domain
    name_servers = body._nameservers
    token = body.token

    #If the field are empty. return an error
    if domain == "" or name_servers == []:
        return ({"errorDesc": "One of the fields is empty!"}, 400)

    #If the user entered a non valid hostname, stop and don't run the other tests
    if not checks.valid_hostname.run(domain, name_servers).get("result"):
        return ({"errorDesc": "Wrong hostname format"}, 400)\
        
        
    if token == None:
        return ({"errorDesc": "No token given!"}, 400)
    
    if not check_token(token):
        return ({"errorDesc": "Invalid token!"}, 400)
        
            
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
        list_of_check_results.append({"id":check_id, "result": outcome.get("result"), "key": outcome.get("description")})
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
    if r.sismember("token:set", token):
    
        # Remove token from database if it exists
        r.srem("token:set", token)
        
        return True
    
    else:
        return False