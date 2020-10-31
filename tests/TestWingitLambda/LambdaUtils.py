"""
Utility functions
"""
import requests
import random
import time

_REQUEST_URL = "https://mvmb9qdwti.execute-api.us-west-1.amazonaws.com/WingitProduction/wingitresource"
_HEX_CHARS = "0123456789abcdefABCDEF"


def request(**params):
    """
    Sends a request to the API with the given params
    :param params: a kwargs list of params
    :return: the response from the server
    """

    response = requests.get(_REQUEST_URL, params=params).json()
    if 'message' in response:
        raise ValueError("Internal server error with params: %s\nOutput: %s" % (params, response))
    return response


def get_error_codes():
    """
    Requests all of the error codes from the server
    :return: a dictionary
    """
    return request(event_type='get_error_codes')


def random_64(all_hex=True, all_lower=True):
    return random_str(64, all_hex=all_hex, all_lower=all_lower)


def random_str(size, all_hex=True, all_lower=True):
    """
    Returns a random string of characters
    :param size: the number of characters to use
    :param all_hex: if True, then the only characters returned will be hexadecimal
        (0-9, a-f, A-F). Otherwise return a list of random characters with
        ascii value 0-255.
    :param all_lower: if True, then all characters returned will be lowercase,
        otherwise it is a mix of upper and lower case
    """
    ret = ""
    for i in range(size):
        if all_hex:
            ret += random.choice(_HEX_CHARS)
        else:
            ret += chr(random.randint(0, 255))
    return ret if not all_lower else ret.lower()


def get_binary_permutations(n):
    """
    Returns a list of strings of binary representations of all integers in range [0, 2**n)
    """
    def pad(s):
        return ('0' * (n - len(s)) + s) if len(s) < n else s
    return [pad(bin(i)[2:]) for i in range(2**n)]
