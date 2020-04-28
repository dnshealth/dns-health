import connexion
import six
from .. import checks
import dns.name

from swagger_server.models.check import Check  # noqa: E501
from swagger_server.models.inv_par import InvPar  # noqa: E501
from swagger_server.models.result import Result  # noqa: E501
from swagger_server import util


def test_servers(body):  # noqa: E501
    """Send a query to the backend to test name servers

     # noqa: E501

    :param body: Domain and name servers to be tested
    :type body: dict | bytes

    :rtype: Result
    """
    if connexion.request.is_json:
        body = Check.from_dict(connexion.request.get_json())  # noqa: E501

    if body.domain == "" or body._nameservers == []:
        return ("One of the fields is empty!", 400)

    domain = body.domain
    name_servers = body._nameservers

    if not checks.valid_hostname.run(domain, name_servers).get("result"):
        return("Wrong hostname format", 400)

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


    check_id = 0
    list_of_check_results = []
    for outcome in results:
        list_of_check_results.append({"id":check_id, "result": outcome.get("result"), "key": "keytest"})
        check_id += 1

    response = {"domain": domain, "ns": name_servers, "checks":list_of_check_results}

    return (response, 200)