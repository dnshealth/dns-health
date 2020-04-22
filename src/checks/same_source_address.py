#!/usr/bin/env python3
"""Responses from the authoritative name servers must contain the same source IP address
   as the destination IP address of the initial query.
"""
import sys

# DNS imports
import dns.resolver
import dns.flags

from dns.query import UnexpectedSource


def run(hostname, list_of_NS):
    # Save parameters to variables
    for ns in list_of_NS:
        dnsResolver = dns.resolver.query(ns)

        # Get the name server from the dns
        for ipValue in dnsResolver:
            nsIP = ipValue.to_text()

        # Check if source IP and destination IP is the same
        domain = hostname

        ADDITIONAL_RDCLASS = 4096

        domain = dns.name.from_text(domain)
        if not domain.is_absolute():
            domain = domain.concatenate(dns.name.root)

        request = dns.message.make_query(domain, dns.rdatatype.ANY)
        request.flags |= dns.flags.AD
        request.find_rrset(request.additional, dns.name.root, ADDITIONAL_RDCLASS,
                           dns.rdatatype.OPT, create=True, force_unique=True)
        try:
            response = dns.query.udp(request, nsIP)
        except UnexpectedSource as e:
            print(str(e))
            return {"description": "Same source address failed", "result": False}

        return {"description": response.answer, "result": True}
