from unittest import TestCase
from src.checks.consistent_delegation_zone import run


class Test(TestCase):
    def test_run(self):
        # Here we ask the list of NS servers below for what they think google.com should have as NS servers.
        # Obviously, with google, these should be consistent across all 4 and our check should PASS.
        res = run("google.com", ["ns1.google.com", "ns2.google.com", "ns3.google.com", "ns4.google.com"], False)
        assert res["result"]

    def test_run_2(self):
        # We added a test zone for google.com on dns1.dnshealth.eu which contains a different set of NS records
        # from those on ns1.google.com. This shall FAIL the check (hence the not-word in assert)
        res = run("google.com", ["ns1.google.com", "dns1.dnshealth.eu"], True)
        assert not res["result"]