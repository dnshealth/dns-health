from unittest import TestCase
from src.checks.same_source_address import run


class Test(TestCase):
    def test_run(self):
        result = run("dnshealth.eu", ["dns1.dnshealth.eu", "dns2.dnshealth.eu"], False)
        assert result["result"]
        
        
#*************IPv6*******************

    def test_run_2(self):
        result = run("dnshealth.eu", ["dns1.dnshealth.eu", "dns2.dnshealth.eu"], True)
        assert result["result"]
        