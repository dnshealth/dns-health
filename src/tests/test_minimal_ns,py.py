from unittest import TestCase
from src.checks.minimal_ns import run

class Test(TestCase):
    def test_run(self):
        # here we want to test to see if the given list
        # if ns indeed have different ip or not
        # should return true
        res = run("google.com", ["ns1.google.com", "ns2.google.com", "ns3.google.com"])
        assert res["result"]
    
    def test_run_2(self):
        # tests a list with only 1 item
        res = run("google.com", ["ns1.google.com"])
        assert res["result"]

    def test_run_3(self):
        # tests a list that would result in the same ip
        res = run("google.com", ["ns1.google.com", "ns2.google.com", "ns2.google.com"])
        assert res["result"]
