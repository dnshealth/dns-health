from unittest import TestCase
from src.checks.dnssec_main import run

class Test(TestCase):

    
    def test_run(self):
        res = run('google.com',
            ['ns1.google.com.',
            'ns2.google.com.',
            'ns3.google.com.',
            'ns4.google.com.'], False)
        assert not res["result"]

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
            'ns1.p31.dynect.net.'], False)
        assert not res["result"]


    def test_run3(self): 
        res = run('rabvuyraebvu.fef.com',
            ['ns1.parkingcrew.net',
            'ns2.parkingcrew.net'], False)
        assert not res["result"]


    def test_run4(self):
        res = run('example.com',
        ['a.iana-servers.net',
        'b.iana-servers.net'], False)
        assert res["result"]

    def test_run5(self):
      res = run('iana.org',
      ['ns.icann.org',
      'a.iana-servers.net',
      'b.iana-servers.net',
      'c.iana-servers.net'], False)
      assert res['result']

    def test_run6(self):
      res = run('dnssec-deployment.org',
      ['ns1.sea1.afilias-nst.info.',
      'ns1.ams1.afilias-nst.info.',
      'ns1.hkg1.afilias-nst.info.',
      'ns1.yyz1.afilias-nst.info.',
      'ns1.mia1.afilias-nst.info.'], False)
      assert res['result']
        
#*******************IPv6***************************


    def test_run7(self):
        res = run('google.com',
            ['ns1.google.com.',
            'ns2.google.com.',
            'ns3.google.com.',
            'ns4.google.com.'], True)
        assert not res["result"]

    def test_run8(self):
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
            'ns1.p31.dynect.net.'], True)
        assert not res["result"]

    def test_run9(self): 
        res = run('rabvuyraebvu.fef.com',
            ['ns1.parkingcrew.net',
            'ns2.parkingcrew.net'], True)
        assert not res["result"]

    def test_run10(self):
        res = run('example.com',
        ['a.iana-servers.net',
        'b.iana-servers.net'], True)
        print(res)
        assert res["result"]

    def test_run11(self):
      res = run('iana.org',
      ['ns.icann.org',
      'a.iana-servers.net',
      'b.iana-servers.net',
      'c.iana-servers.net'], True)
      print(res)
      assert res["result"]
      
    def test_run12(self):
      res = run('dnssec-deployment.org',
      ['ns1.sea1.afilias-nst.info.',
      'ns1.ams1.afilias-nst.info.',
      'ns1.hkg1.afilias-nst.info.',
      'ns1.yyz1.afilias-nst.info.',
      'ns1.mia1.afilias-nst.info.'], True)
      assert not res["result"]