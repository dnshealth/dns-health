# dns-health

# Prerequisites
python 3.8 and python libraries in requirements.txt. To install python libraries, run:
```
pip3.8 install -r requirements.txt
```

# Running the command line tool
To run the command line tool, run:
```
python3.8 -m src.main --domain kth.se --ns a.ns.kth.se b.ns.kth.se nic2.lth.se ns2.chalmers.se
```
To run checks against the current nameservers of the define, define the _delegated_ parameter.
```
python3.8 -m src.main --domain kth.se --delegated true
```
To run checks against the IPv6 addresses, add the ipv6 flag
```
python3.8 -m src.main --domain kth.se --delegated true --ipv6
```
