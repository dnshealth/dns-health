from unittest import TestCase
from src.checks.dns_test_recursion import run

class Test(TestCase):
    def test_run(self):
        # Here we check no recursion detection results in true
        res = run("google.se", ["ns1.google.se", "ns2.google.se", "ns3.google.se"])
        # print(res)
        assert res["result"]
    def test_run_2(self): 
        # Here we check that no recursion detection results in false
        res = run("dnshealth.eu", ["dns.google"])
        # print(res)
        assert not res["result"]
