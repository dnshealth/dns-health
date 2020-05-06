'''
06.05.2020
Written by Hristo Georgiev (h.georgiev121@gmail.com)
Checks if the DS format is kawai.
'''
import dns.resolver


def run(domain, name_servers):
    result = ds_formatting(domain)
    result["description"] = "Existence of DS records"

    return result


def ds_formatting(domain):

    result = dns.resolver.query(
        domain,
        "DS",
        "IN")
    for A in result:
        print()

