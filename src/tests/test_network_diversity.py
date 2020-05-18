from unittest import TestCase
from src.checks.network_diversity import run

class Test(TestCase):
    def test_run(self):
        # This check should fail, as for some reason ns1.loopia.se and ns2.loopia.se have IPs within
        # the same ASN.
        # 93.188.0.20, 93.188.0.21
        res = run("loopia.se", ["ns1.loopia.se", "ns2.loopia.se"], False)
        assert not res["result"]

    def test_run_2(self):
        # This check should pass as Nordname obviously has their NS servers spread around the globe.
        res = run("nordname.com", ["dns1.nordname.net", "dns2.nordname.net"], False)
        assert res["result"]
        
#***************IPv6 tests****************************************        

    def test_run_3(self):
        # This check should fail, as for some reason ns1.loopia.se and ns2.loopia.se have IPs within
        # the same ASN.
        # 93.188.0.20, 93.188.0.21
        res = run("loopia.se", ["ns1.loopia.se", "ns2.loopia.se"], True)
        assert not res["result"]

    def test_run_4(self):
        # This check should FAIL as Nordname does not have IPv6 support
        res = run("nordname.com", ["dns1.nordname.net", "dns2.nordname.net"], True)
        assert not res["result"]