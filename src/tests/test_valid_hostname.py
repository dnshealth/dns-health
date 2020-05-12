from unittest import TestCase
from src.checks.valid_hostname import run


class Test(TestCase):
    # This should pass, no syntax errors in domain or any of the NS
    def test_run(self):
        res = run("thisshouldpass.com", ["ns1.thisshouldpass.com", "ns2.thisshouldpass.com"])
        assert res["result"]

    # This should fail. A non-ascii character in the domain name.
    def test_run_2(self):
        res = run("thisshouldfäil.com", ["ns1.thisshouldpass.com", "ns2.thisshouldpass.com"])
        assert not res["result"]

    # This should fail. A dash at the end of the second NS
    def test_run_3(self):
        res = run("thisshouldfail.com", ["ns1.thisshouldfail.com", "ns2.thisshouldfail-.com"])
        assert not res["result"]

    # This should fail as there are no TLD given for domain, and no subdomain/TLD for nameservers
    def test_run_4(self):
        res = run("thisiswrong", ["thisisnotcorrect", "fail.com"])
        assert not res["result"]
        
    # This should pass as there are no illegal characters and both domain and nameservers have the needed number of parts (subdomain, TLD)
    def test_run_5(self):
        res = run("cccc.aaa", ["aaa.bbb.ccc", "ddd.eee.fff"])
        assert res["result"]
