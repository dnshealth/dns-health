import connexion
import six

from swagger_server.models.token import Token  # noqa: E501
from swagger_server import util


def get_token():  # noqa: E501
    """Send random token to user

    User is given token which is later used for authentication # noqa: E501


    :rtype: Token
    """
    return 'do some magic!'
