from unittest import TestCase
from src.checks.truncref import run

class Test(TestCase):

    #Testing googles serves, which should pass
    def test_run(self):
        res = run('google.com',
            ['ns1.google.com.',
            'ns2.google.com.',
            'ns3.google.com.',
            'ns4.google.com.'])
        assert res["result"]

    #Testing amazon.co.jp servers, which do not have all authoritative NS in-bailiwick of the parent zone. Should pass as well.
    def test_run2(self):
        res = run('amazon.co.jp',
            ['pdns6.ultradns.co.uk.',
            'pdns1.ultradns.net.',
            'ns4.p31.dynect.net.',
            'ns3.p31.dynect.net.',
            'pdns5.ultradns.info.',
            'pdns4.ultradns.org.',
            'pdns3.ultradns.org.',
            'pdns2.ultradns.net.',
            'ns2.p31.dynect.net.',
            'ns1.p31.dynect.net.'])

    #Testing random domain which has only two name servers. Should pass.
    def test_run3(self): 
        res = run('rabvuyraebvu.fef.com',
            ['ns1.parkingcrew.net',
            'ns2.parkingcrew.net'])

    #Test example.com, which does not have glue records for it's authoritative name servers, but it's servers are not in-bailiwick so they pass
    def test_run4(self):
        res = run('example.com',
        ['ns1.example.com',
        'ns2.example.com'])
        assert res["result"]
