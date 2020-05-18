from unittest import TestCase
from src.checks.valid_hostname import run


class Test(TestCase):
    # This should pass, no syntax errors in domain or any of the NS
    def test_run(self):
        res = run("thisshouldpass.com", ["ns1.thisshouldpass.com", "ns2.thisshouldpass.com"], False)
        assert res["result"]

    # This should fail. A non-ascii character in the domain name.
    def test_run_2(self):
        res = run("thisshouldfäil.com", ["ns1.thisshouldpass.com", "ns2.thisshouldpass.com"], False)
        assert not res["result"]

    # This should fail. A dash at the end of the second NS
    def test_run_3(self):
        res = run("thisshouldfail.com", ["ns1.thisshouldfail.com", "ns2.thisshouldfail-.com"], False)
        assert not res["result"]

    # This should fail as there are no TLD given for domain, and no subdomain/TLD for nameservers
    def test_run_4(self):
        res = run("thisiswrong", ["thisisnotcorrect", "fail.com"], False)
        assert not res["result"]
        
    # This should pass as there are no illegal characters and both domain and nameservers have the needed number of parts (subdomain, TLD)
    def test_run_5(self):
        res = run("cccc.aaa", ["aaa.bbb.ccc", "ddd.eee.fff"], False)
        assert res["result"]
        
    # This should fail as the function is given an IP instead of a domain name
    def test_run_6(self):
        res = run("216.58.207.206", ["ns1.google.com"], False)
        assert not res["result"]
        
    # This should fail as the functions is given an IP instead of a nameserver
    def test_run_7(self):
        res = run ("google.com", ["ns1.google.com", "216.239.34.10"], False)
        assert not res["result"]
        
#**************************IPv6 Tests****************************************

    # This should pass, no syntax errors in domain or any of the NS
    def test_run_8(self):
        res = run("thisshouldpass.com", ["ns1.thisshouldpass.com", "ns2.thisshouldpass.com"], True)
        assert res["result"]

    # This should fail. A non-ascii character in the domain name.
    def test_run_9(self):
        res = run("thisshouldfäil.com", ["ns1.thisshouldpass.com", "ns2.thisshouldpass.com"], True)
        assert not res["result"]

    # This should fail. A dash at the end of the second NS
    def test_run_10(self):
        res = run("thisshouldfail.com", ["ns1.thisshouldfail.com", "ns2.thisshouldfail-.com"], True)
        assert not res["result"]

    # This should fail as there are no TLD given for domain, and no subdomain/TLD for nameservers
    def test_run_11(self):
        res = run("thisiswrong", ["thisisnotcorrect", "fail.com"], True)
        assert not res["result"]
        
    # This should pass as there are no illegal characters and both domain and nameservers have the needed number of parts (subdomain, TLD)
    def test_run_12(self):
        res = run("cccc.aaa", ["aaa.bbb.ccc", "ddd.eee.fff"], True)
        assert res["result"]
        
    # This should fail as the function is given an IP instead of a domain name
    def test_run_13(self):
        res = run("216.58.207.206", ["ns1.google.com"], True)
        assert not res["result"]
        
    # This should fail as the functions is given an IP instead of a nameserver
    def test_run_14(self):
        res = run ("google.com", ["ns1.google.com", "216.239.34.10"], True)
        assert not res["result"]