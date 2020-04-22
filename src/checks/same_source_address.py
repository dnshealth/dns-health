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


def run(hostname, list_of_NS, verbose=False):
    # Save parameters to variables
    for ns in list_of_NS:
        dnsResolver = dns.resolver.query(ns)

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
        request.find_rrset(request.additional, dns.name.root, ADDITIONAL_RDCLASS,
                           dns.rdatatype.OPT, create=True, force_unique=True)
        try:
            # Return the response obtained after sending a query via UDP.
            response = dns.query.udp(request, nsIP)

        # A DNS query response came from an unexpected address or port.
        except UnexpectedSource as e:
            if verbose:
                print(str(e))
            return {"description": "Same source address for DNS response", "result": False}

        return {"description": "Same source address for DNS response", "result": True}