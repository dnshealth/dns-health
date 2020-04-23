from unitest import TestCase
from src.checks.dns_test_recursion import run

class Test(TestCase):
    def test_run:
        # Here we check that RA gives false
        res = run("google.com", ["ns1.google.com", "ns2.google.com", "ns3.google.com"])
        assert res["result"]
    def test_run_2: 
        # check for RA giving true
        res = run("google.com", ["ns1.kth.se", "ns2.kth.se", "ns3.kth.se"])
        assert res["result"]
