from unittest import TestCase

from src.checks.prohibited_networks import prohibited_check


# Perform two separate test. One will fail one will pass that the main test will pass

class TestProhibitedNetworks(TestCase):
    def test_prohibited_check(self):
        ns = prohibited_check("192.88.99.0")
        assert not ns

    def test_prohibited_check_2(self):
        ns = prohibited_check("ns1.google.com")
        assert ns
