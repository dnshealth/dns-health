#!/usr/bin/env python3

import dns.resolver

domain = "codeitfactory.com"
result = dns.resolver.query(domain, 'A')
for ipval in result:
    print('IP', ipval.to_text())