#!/usr/bin/env python3
#Program checks if all authoritative nameserver SOA and NS records are consistent
#Takes hostname and list of nameservers as input
import socket
import dns.resolver