from unittest import TestCase
from src.checks.same_source_address import run


class Test(TestCase):
    def test_run(self):
        result = run("dnshealth.eu", ["dns1.dnshealth.eu", "dns2.dnshealth.eu"])
        assert result["result"]