#!/usr/bin/env python3
import redis

from flask_session import Session

from flask import request

from datetime import datetime

def check_time_limit(auth_token, session_list, time_limit):
    
    if auth_token not in session_list.keys():
        session_list.set(auth_token) = datetime.now()
        return (200)

class Config:

    SECRET_KEY = None

    FLASK_APP = None

    FLASK_ENV = None

    session = None

    '''

    def parse_credentials(self,host_url,port,password):
        return 'redis://:'+ password + '@' + host_url+ ':' + str(port)

    def initialise_redis(self,host_url,port,password):

        SESSION_TYPE  = redis

        SESSION_REDIS = self.parse_credentials(host_url,port,password)

    '''

    def __init__(self,flask_app,flask_environment,secret_key,host_url,port,password):
        
        SECRET_KEY  = secret_key

        FLASK_APP   = flask_app

        FLASK_ENV   = flask_environment

    def getRequest(self,request):

        previous_time_stamp = self.session.get(ip_of_request).time()

        time_diff = (datetime.now().time() - previous_time_stamp).total_seconds()

        if time_diff < 10:
            return (-1, "time diff is less than 15 seconds")
        else:
            self.session[ip_of_request] = datetime.now()
            return (0, "valid request")

