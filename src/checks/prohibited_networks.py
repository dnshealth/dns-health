#!/usr/bin/env python3

# This feature will check if the NS server IP is global or private
# If it is global it will pass the test
# If it is local it will prompt the user that this IP is from a private network and
# test will fail

# Variables:
# ns_server --> should be taken as an argument from the command line
# ip_val --> extracted value of the ns server
import dns.resolver
import ipaddress

def DESCRIPTION():
    return "Prohibited Networks"

def run(domain, ns_list,ipv6):

    # Check each ns in ns_list. If one fails, immediately return false. Otherwise, return true after having checked
    # everything
    for ns in ns_list:
        dictionary = prohibited_check(ns, ipv6)
        if not dictionary.get("result"):
            return {"description": DESCRIPTION(), "result": False, "details": dictionary.get("details")}

    return {"description": DESCRIPTION(), "result": True, "details": dictionary.get("details")}

def prohibited_check(ns_server, ipv6):
    if ipv6:
        try:
            result = dns.resolver.query(ns_server, 'AAAA')
        except:
            return False

        
        for ipval in result:
            if ipaddress.ip_address(str(ipval)).is_private:
                return {"result": False,
                        "details": "The IP is in a private range."}
            elif ipaddress.ip_address(str(ipval)).is_unspecified:
                return {"result": False,
                        "details": "The IP is in a unspecified range. Example: ::/128"}
            elif ipaddress.ip_address(str(ipval)).is_multicast:
                return {"result": False,
                        "details": "The IP of {0} is in a multicast range. " .format(ns_server)}
            elif ipaddress.ip_address(str(ipval)).ipv4_mapped is not None:
                return {"result": False,
                        "details": "The IP is in a ipv4 mapped addresses range."}
            elif ipaddress.ip_address(str(ipval)).teredo is not None:
                return {"result": False,
                        "details": "The IP is in a teredo addresses range."}
            elif ipaddress.ip_address(str(ipval)).sixtofour is not None:
                return {"result": False,
                        "details": "For addresses that appear to be 6to4 addresses (starting with 2002::/16) as defined by RFC 3056."}
            elif ipaddress.ip_address(str(ipval)).is_loopback:
                return {"result": False,
                        "details": "The IP of {0} is in a loopback range. ".format(ns_server)}
            elif ipaddress.ip_address(str(ipval)).is_reserved:
                return {"result": False,
                        "details": "The IP of {0} is in a reserved range. .".format(ns_server)}

        return {"result": True, "details": "All sub checks passed"}
    else :
        # Excluding special IP - ranges that are not covered in ipaddress module
        deprecated_ips = ipaddress.ip_network('192.88.99.0/24')
        shared_address_space = ipaddress.ip_network('100.64.0.0/10')
        try:
            result = dns.resolver.query(ns_server, 'A')
        except:
            return False
        # for ipval in result:
        #     if (
        #             ipaddress.ip_address(str(ipval)).is_private or
        #             ipaddress.ip_address(str(ipval)).is_multicast or
        #             ipaddress.ip_address(str(ipval)).is_loopback or
        #             ipaddress.ip_address(str(ipval)) in deprecated_ips or
        #             ipaddress.ip_address(str(ipval)) in shared_address_space
        #     ):
        #         return False
        #
        #     else:
        #         return True
        for ipval in result:
            if ipaddress.ip_address(str(ipval)).is_private:
                return {"result": False,
                        "details": "The IP is in a private range. Example: 127.0.0.1 or 192.168.0.1/24"}

            elif ipaddress.ip_address(str(ipval)).is_multicast:
                return {"result": False,
                        "details": "The IP of {0} is in a multicast range. The range of addresses between 244.0.0.0 - 224.0.0.255, is reserved for the use of routing protocols and other low-level topology." .format(ns_server)}

            elif ipaddress.ip_address(str(ipval)).is_loopback:
                return {"result": False,
                        "details": "The IP of {0} is in a loopback range. The range of addresses between 127.0.0.0 - 127.255.255.255, is reserved for the use of loopback purposes.".format(ns_server)}
            elif ipaddress.ip_address(str(ipval)) in deprecated_ips:
                return {"result": False,
                        "details": "The IP of {0} is in a deprecated range. The range of addresses {1} are deprecated, so they can't be used for NS.".format(ns_server, str(deprecated_ips))}

            elif ipaddress.ip_address(str(ipval)) in shared_address_space:
                return {"result": False,
                        "details": "The IP of {0} is in a shared address space. The range of addresses {1} are for use in ISP CGN deployments and NAT devices that can handle the same addresses occurring both on inbound and outbound interfaces.".format(ns_server, str(shared_address_space))}

        return {"result": True, "details": "All sub checks passed"}


# For debugging purposes please use print(prohibited_check("192.88.99.1"))

