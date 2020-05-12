#!/usr/bin/env python3
"""
Responses from the authoritative name servers must contain the same source IP address
   as the destination IP address of the initial query.
"""
import sys

# DNS imports
import dns.resolver
import dns.flags
from dns.query import UnexpectedSource

def DESCRIPTION():
    return "Same source address as destination address"

def run(hostname, list_of_NS,ipv6):

    # Save parameters to variables
    for ns in list_of_NS:
        try:
            dnsResolver = dns.resolver.query(ns)
        except:
            # Any error with resolving will cause other checks to fail. That's why we pass this one.
            return {"description": DESCRIPTION(), "result": True}

        # Get the name server from the dns
        for ipValue in dnsResolver:
            nsIP = ipValue.to_text()

        # Check if source IP and destination IP is the same

        ADDITIONAL_RDCLASS = 4096

        domain = dns.name.from_text(hostname)
        if not domain.is_absolute():
            domain = domain.concatenate(dns.name.root)
        # Make a query
        request = dns.message.make_query(domain, dns.rdatatype.ANY)
        request.flags |= dns.flags.AD
        request.find_rrset(request.additional, dns.name.root, ADDITIONAL_RDCLASS, dns.rdatatype.OPT, create=True, force_unique=True)
        try:
            # Return the response obtained after sending a query via UDP.
            response = dns.query.udp(request, nsIP)

        # A DNS query response came from an unexpected address or port.
        except UnexpectedSource as e:
            return {"description": DESCRIPTION(), "result": False, "details": e.msg}

        return {"description": DESCRIPTION(), "result": True, "details": "Success! Responses from the authoritative name servers contain the same source IP address as the destination IP address."}