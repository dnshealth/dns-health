from unittest import TestCase
from src.checks.consistent_authoritative_nameservers import run


class Test(TestCase):
    def test_run(self):
        # Here we check if the nameservers from the given list each contain the same NS record and SOA record
        # This check should PASS as google.com has 4 nameservers and all of them refrence each other
        res = run("google.com", ["ns1.google.com", "ns2.google.com", "ns3.google.com", "ns4.google.com"], False)
        assert res["result"]
    
    def test_run_2(self):
        # Here we check google.com again but we enter a nameserver that is not for google.com
        # Thus it will not contain the same info as in the google nameserver and test should FAIL
        res = run("google.com", ["ns1.google.com", "dns1.dnshealth.eu"], False)
        assert not res["result"]
        
    def test_run_3(self):
        # Giving the program an incomplete list of nameserver or duplicate nameservers should PASS as well
        # as the program checks only the given list of nameservers and their SOA and NS records
        res = run("kth.se", ["a.ns.kth.se"], False)
        assert res["result"]
        
    # This should pass as all repeating nameservers are filtered out
    def test_run_4(self):
        res = run("kth.se", [
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se"], False)
        assert res["result"]
        
    def test_run_5(self):
        # This should fail as the nameserver IP will not be resolved
        res = run("kth.se", ["a.a.a"], False)
        assert not res["result"]
        
    def test_run_6(self):
        # No idea what this should do
        res = run("google.com", ["216.239.32.10", "ns2.google.com", "ns3.google.com", "ns4.google.com"], False)
        assert res["result"]
        
#**********************IPv6 tests*********************************

    def test_run_7(self):
        # Here we check if the nameservers from the given list each contain the same NS record and SOA record
        # This check should PASS as google.com has 4 nameservers and all of them refrence each other
        res = run("google.com", ["ns1.google.com", "ns2.google.com", "ns3.google.com", "ns4.google.com"], True)
        assert res["result"]
    
    def test_run_8(self):
        # Here we check google.com again but we enter a nameserver that is not for google.com
        # Thus it will not contain the same info as in the google nameserver and test should FAIL
        res = run("google.com", ["ns1.google.com", "dns1.dnshealth.eu"], True)
        assert not res["result"]
        
    def test_run_9(self):
        # Giving the program an incomplete list of nameserver or duplicate nameservers should PASS as well
        # as the program checks only the given list of nameservers and their SOA and NS records
        res = run("kth.se", ["a.ns.kth.se"], True)
        assert res["result"]
        
    # This should pass as all repeating nameservers are filtered out
    def test_run_10(self):
        res = run("kth.se", [
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se",
            "b.ns.kth.se"], True)
        assert res["result"]
        
    def test_run_11(self):
        # This should fail as the nameserver IP will not be resolved
        res = run("kth.se", ["a.a.a"], True)
        assert not res["result"]
        
    def test_run_12(self):
        # This should FAIL as an IP is given
        res = run("google.com", ["216.239.32.10", "ns2.google.com", "ns3.google.com", "ns4.google.com"], True)
        assert not res["result"]