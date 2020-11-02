"""
Utility functions
"""
import requests
import random
import string
from lambda_code.lambda_function import lambda_handler
from lambda_code.constants import MIN_PASSWORD_SIZE, MAX_USERNAME_SIZE

_REQUEST_URL = "https://mvmb9qdwti.execute-api.us-west-1.amazonaws.com/WingitProduction/wingitresource"
_HEX_CHARS = "0123456789abcdefABCDEF"

REQUEST_TYPE_ONLINE = True  # Whether or not we are testing online or offline


def set_request_type_online(request_type_is_online):
    """
    Call this with boolean input to determine if we should test online or offline
    :param request_type_is_online: boolean
    """
    global REQUEST_TYPE_ONLINE
    REQUEST_TYPE_ONLINE = request_type_is_online


def request(**params):
    """
    Sends a request to the API with the given params
    :param params: a kwargs list of params
    :return: the response from the server
    """
    if REQUEST_TYPE_ONLINE:
        response = requests.get(_REQUEST_URL, params=params).json()
        if 'message' in response:
            raise ValueError("Internal server error with params: %s\nOutput: %s" % (params, response))
        return response
    else:
        # The return body is a string (because json.dumps) so we must call eval on it
        return eval(lambda_handler({'queryStringParameters': params}, None)['body'])


def random_str(size, all_ascii=True):
    """
    Returns a random string of characters
    :param size: the number of characters to use
    :param all_ascii: if True, then the only characters returned will be ascii chars
    """
    return ''.join(
        (random.choice(string.ascii_letters) if all_ascii else chr(random.randint(0, 255))) for i in range(size))


def random_valid_password():
    """
    Generates a random password that passes validity checks on the server
    """
    return random_str(MIN_PASSWORD_SIZE + random.randint(0, 5 * MIN_PASSWORD_SIZE), all_ascii=True)


def random_valid_username():
    """
    Generates a random username that passes validity checks on the server, and probably isn't used by anyone
    """
    return random_str(MAX_USERNAME_SIZE, all_ascii=True)


def random_valid_email():
    """
    Generates a random email that passes validity checks on the server, and probably isn't used by anyone
    """
    return random_str(64, all_ascii=True) + '@gmail.com'


def get_binary_permutations(n):
    """
    Returns a list of strings of binary representations of all integers in range [0, 2**n)
    """

    def pad(s):
        return ('0' * (n - len(s)) + s) if len(s) < n else s

    return [pad(bin(i)[2:]) for i in range(2 ** n)]
