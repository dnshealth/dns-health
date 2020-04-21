#!/usr/bin/env python3
"""Responses from the authoritative name servers must contain the same source IP address
   as the destination IP address of the initial query.
"""
import sys

# DNS imports
import dns.resolver
import dns.flags

# Save parameters to variables
domain = sys.argv[1]
ns = sys.argv[2]
dnsResolver = dns.resolver.query(ns)

# Get the name server from the dns
for ipValue in dnsResolver:
    nsIP = ipValue.to_text()

# Check if source IP and destination IP is the same
domain = domain
name_server = nsIP
ADDITIONAL_RDCLASS = 4096

domain = dns.name.from_text(domain)
if not domain.is_absolute():
    domain = domain.concatenate(dns.name.root)

request = dns.message.make_query(domain, dns.rdatatype.ANY)
request.flags |= dns.flags.AD
request.find_rrset(request.additional, dns.name.root, ADDITIONAL_RDCLASS,
                   dns.rdatatype.OPT, create=True, force_unique=True)
response = dns.query.udp(request, name_server)

if response.answer:
    {"description": response.answer, "result": True}
else:
    False
