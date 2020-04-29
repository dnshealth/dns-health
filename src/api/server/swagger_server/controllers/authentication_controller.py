import connexion
import six
import redis
import uuid

# from swagger_server.models.token import Token  # noqa: E501
# from swagger_server import util

# Connection paramaters for Redis database
conn_params = {
    "host": "localhost",
    "port": 6379,
    "password": None,
    "db": 0
}

# Generate token save it to Redis database and pass it to the user
def get_token():  # noqa: E501
    
    # Create a Redis client instance 
    r = redis.Redis(**conn_params)
    
    # Generate token
    token = uuid.uuid4().int
    
    # Save token to database
    r.sadd("token:set", token)
    
    # Return token in dictionary with response code
    return ({"token": token}, 200)