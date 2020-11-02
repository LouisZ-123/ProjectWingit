from lambda_code.actions import *
from lambda_code.utils import *


def lambda_handler(event, context):
    """
    The main function that is called for every request.
    :param event: the incomming parameters
    :param context: the current context
        See info for context here: https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
    """

    params = event['queryStringParameters']  # The parameters passed in Rest API call

    # If no parameters are passed, just return this string for testing purposes
    if params is None:
        return {
            'statusCode': 200,
            'body': json.dumps("Hello Wingit!")
        }

    # If there is no event type, show an error
    if EVENT_TYPE_STR not in params:
        return error(ERROR_NO_EVENT_TYPE)

    # Get the event type
    event_type = params[EVENT_TYPE_STR]

    # Creating an account
    if event_type == EVENT_CREATE_ACCOUNT_STR:
        return create_account(params)

    # Verifying the account
    elif event_type == EVENT_VERIFY_ACCOUNT_STR:
        return verify_account(params)

    # Logging in to the account
    elif event_type == EVENT_LOGIN_STR:
        return login_account(params)

    else:
        # If the event type is unknown, show an error
        return error(ERROR_UNKNOWN_EVENT_TYPE, event_type)
