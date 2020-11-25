"""
A list of different errors and error codes, along with the ability to generate
the JSON for the errors.

All error codes MUST start with 'ERROR_', for unit testing purposes. Do not
start anything else with the exact prefix 'ERROR_' if it is not an error code tuple.
"""
from lambda_code.constants import *

# Error code -1: this error should be impossible to get, so if you get it, cudos to you
ERROR_IMPOSSIBLE_ERROR = (-1, "It should be impossible to get this error, what on God's green earth did you do?!?!"
                              " - %s", True)

# Error codes 1-99: errors that can happen anywhere
ERROR_MISSING_PARAMS = (1, "Missing param '%s'", True)
ERROR_UNKNOWN_ERROR = (2, "Unknown error occurred: %s", True)
ERROR_UNIMPLEMENTED_HTTP_REQUEST = (3, 'Unimplemented http request type: %s', True)

# Error codes 100-199: errors involving the event_type
ERROR_NO_EVENT_TYPE = (100, "No event type was passed", False)
ERROR_UNKNOWN_EVENT_TYPE = (101, "An unknown event type was passed for http method '%s': %s", True)

# Error codes 200-299: errors involving account information
ERROR_INVALID_EMAIL = (200, "Email is invalid: %s", True)
ERROR_INVALID_USERNAME = (201, "Username is invalid: \"%s\"", True)
ERROR_INVALID_VERIFICATION_CODE = (202, "Verification code invalid: \"%s\"", True)
ERROR_USERNAME_ALREADY_EXISTS = (203, "Username already exists: %s", True)
ERROR_EMAIL_ALREADY_IN_USE = (204, "Email already in use: %s", True)
ERROR_USERNAME_DOES_NOT_EXIST = (205, "Username does not exist: %s", True)
ERROR_UNMATCHING_VERIFICATION_CODE = (206, "Verification code '%s' does not match for username '%s'", True)
ERROR_INCORRECT_PASSWORD = (207, "Password incorrect", False)
ERROR_EMAIL_DOES_NOT_EXIST = (208, "Email does not exist %s", True)
ERROR_ACCOUNT_UNVERIFIED = (209, "Account has not yet been verified, check your email for verification link", False)
ERROR_INVALID_PASSWORD_HASH = (210, "Invalid password hash", False)

# Error codes 300-399: errors involving s3 bucket access
ERROR_UNKNOWN_S3_REASON = (300, "Unknown reason for accessing S3 bucket: %s", True)
ERROR_UNKNOWN_BOTO3_ERROR = (301, "Unknown boto3 error occurred: %s", True)

# The error codes, and their reverse dictionaries
# This is done in a really weird way because I'm smart (or maybe just lazy...)
ALL_ERROR_CODES_BY_NAME = {key: val[0] for key, val in globals().items() if key.startswith('ERROR_')}
ALL_ERROR_NAMES_BY_CODE = {val: key for key, val in ALL_ERROR_CODES_BY_NAME.items()}


def error(error_tuple, *args):
    """
    Return the JSON showing the error
    :param error_tuple: a 3-tuple with element 0 being an integer error code,
        element 1 being an error string, and element 2 being a boolean to decide
        whether or not to format the error string with the given args
    :param args: the args to format the error string with in the event that
        element 2 of the error_tuple is true
    :return the JSON dictionary representation to return to the API call
    """
    error_str = error_tuple[1] if not error_tuple[2] else (error_tuple[1] % args)
    data = {
        RETURN_ERROR_MESSAGE_STR: "%s: %s" % (ALL_ERROR_NAMES_BY_CODE[error_tuple[0]], error_str),
        RETURN_ERROR_CODE_STR: error_tuple[0]
    }
    return return_message(data=data)
