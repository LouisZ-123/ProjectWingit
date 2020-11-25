from lambda_code.actions import *
from lambda_code.utils import *
import urllib.parse


def lambda_handler(event, context):
    """
    The main function that is called for every request.
    :param event: the incoming parameters
    :param context: the current context
        See info for context here: https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
    """
    if event[HTTP_METHOD_STR] == GET_REQUEST_STR:
        return _get(event, context)
    elif event[HTTP_METHOD_STR] == POST_REQUEST_STR:
        return _post(event, context)
    elif event[HTTP_METHOD_STR] == DELETE_REQUEST_STR:
        return _delete(event, context)
    else:
        return error(ERROR_UNIMPLEMENTED_HTTP_REQUEST, event[HTTP_METHOD_STR])


def _get(event, context):
    """
    Handler for a GET request
    """
    # Get the event type
    all_good, event_type, params = _get_event_type_and_info(event, GET_REQUEST_STR)
    if not all_good:
        return event_type

    # Verifying the account
    if event_type == EVENT_VERIFY_ACCOUNT_STR:
        return verify_account(params)

    # Logging in to the account
    elif event_type == EVENT_LOGIN_STR:
        return login_account(params)

    # Getting a post_url
    elif event_type == EVENT_GET_S3_URL_STR:
        return get_s3_permissions(params)

    else:
        # If the event type is unknown, show an error
        return error(ERROR_UNKNOWN_EVENT_TYPE, GET_REQUEST_STR, event_type)


def _post(event, context):
    """
    Handler for a POST request
    """
    # Get the event type
    all_good, event_type, body = _get_event_type_and_info(event, POST_REQUEST_STR)
    if not all_good:
        return event_type

    # Creating an account
    if event_type == EVENT_CREATE_ACCOUNT_STR:
        return create_account(body)

    else:
        # If the event type is unknown, show an error
        return error(ERROR_UNKNOWN_EVENT_TYPE, POST_REQUEST_STR, event_type)


def _delete(event, context):
    """
    Handler for a DELETE request
    """
    # Get the event type
    all_good, event_type, body = _get_event_type_and_info(event, DELETE_REQUEST_STR)
    if not all_good:
        return event_type

    # Creating an account
    if event_type == EVENT_DELETE_ACCOUNT_STR:
        return delete_account(body)

    else:
        # If the event type is unknown, show an error
        return error(ERROR_UNKNOWN_EVENT_TYPE, POST_REQUEST_STR, event_type)


def _get_event_type_and_info(event, http_method):
    """
    Returns a 3-tuple of (1) True if no error, False if error, (2) the event type if no error, the error if error, and
    (3) the info if there was no error and None if there was
    """

    def _parse_url(url_params):
        """
        Parses the input string into a dictionary
        """
        ret = {}
        for substring in url_params.split('&'):
            left, right = substring.split('=')
            right = urllib.parse.unquote(right)
            if left in ret:
                ret[left] = [ret[left], right] if isinstance(ret[left], str) else ret[left] + [right]
            else:
                ret[left] = right
        return ret

    if http_method == GET_REQUEST_STR:
        info = event['queryStringParameters']
    elif http_method in [POST_REQUEST_STR, DELETE_REQUEST_STR]:
        info = _parse_url(event['body'])
    else:
        return False, error(ERROR_IMPOSSIBLE_ERROR, '_get_event_type, should not have implemented any other method'
                                                    'in the api gateway yet... %s' % http_method), None

    # If no parameters are passed, just return this string for testing purposes
    if info is None:
        return False, {
            'statusCode': 200,
            'body': json.dumps("Hello Wingit %s!" % http_method)
        }, None

    # If there is no event type, show an error
    if EVENT_TYPE_STR not in info:
        return False, error(ERROR_NO_EVENT_TYPE), None

    # Get the event type
    return True, info[EVENT_TYPE_STR], info
