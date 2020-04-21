#DNSHEALTH-12
import queryNameServers

#a function that returns all the authoritative servers for the given domain/domain
#returns a list of tuples with what kind of record we received, the domain of the authority and the domain we queried
def getAuthoritativeServers(domain):
    
    (status,res) = queryNameServers.queryAuthoritativeNameServers(domain)

    if status =="OK":
   
        result = []

        for i in res:
            if i[0]=='AUTHORITATIVE':
                result.append(i)

        return result

    else:
        return "ERROR"
