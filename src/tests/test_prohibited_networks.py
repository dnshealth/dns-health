from unittest import TestCase

from src.checks.prohibited_networks import prohibited_check


# Perform two separate test. One will fail one will pass that the main test will pass

class TestProhibitedNetworks(TestCase):
    def test_run(self):
        ns = prohibited_check("192.88.99.0",False)
        assert not ns

    def test_run2(self):
        ns = prohibited_check("ns1.google.com",False)
        assert ns
