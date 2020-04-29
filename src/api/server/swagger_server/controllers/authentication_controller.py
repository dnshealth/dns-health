import connexion
import six
import redis
import uuid

from swagger_server.models.token import Token  # noqa: E501
from swagger_server import util


def get_token():  # noqa: E501
    r = redis.Redis()
    token = uuid.uuid4().int
    r.sadd("token:set", token)
    return ({"token": token}, 200)

def check_token(token):
    r = redis.Redis()
    if r.sismember("token:set", token):
        return True
    else:
        return False
    