from unittest import TestCase
from src.checks.dns_test_recursion import run

class Test(TestCase):
    def test_run(self):
        # Here we check no recursion detection results in true
        res = run("google.com", ["ns1.google.com", "ns2.google.com", "ns3.google.com"])
        assert res["result"]
    def test_run_2(self): 
        # Here we check that no recursion detection results in false
        res = run("google.com", ["ns1.kth.se", "ns2.kth.se", "ns3.kth.se"])
        assert not res["result"]
