import connexion
import six
import redis
import uuid
from datetime import datetime

# from swagger_server.models.token import Token  # noqa: E501
# from swagger_server import util

# Generate token save it to Redis database and pass it to the user
def get_token():  # noqa: E501
    
    # Connection paramaters for Redis database
    conn_params = {
    "host": "localhost",
    "port": 6379,
    "password": None,
    "db": 0
    }
    
    # Create a Redis client instance 
    r = redis.Redis(**conn_params)
    
    # Generate token
    token = uuid.uuid4().int
    
    # Save token to database
    r.sadd("token:set", (token, datetime.now()))
    
    # Return token in dictionary with response code
    return ({"token": token}, 200)