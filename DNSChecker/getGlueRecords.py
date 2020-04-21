#!/usr/bin/env python3
#DNSHEALTH-14
import queryNameServers

#a function that returns all the glue records for the given domain/domain
#returns a list of tuples with what kind of record we received, the domain of the glue record and the domain we queried
def getGlueRecords(domain):
    
    (status,res) = queryNameServers.queryAuthoritativeNameServers(domain)

    if status =="OK":
   
        result = []

        for i in res:
            if i[0]=='GLUE':
                result.append(i)

        return result

    else:
        return "ERROR"
