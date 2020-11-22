"""
Contains constants for things that I want in constants
Also some functions that are base functions used everywhere

Most of these are just in case I change my mind on what I want things named
"""
import json

# The link to the api
API_URL = "https://mvmb9qdwti.execute-api.us-west-1.amazonaws.com/WingitProduction/wingitresource"

# The number of rounds to use with bcrypt salt, tried to keep time close to 1sec
BCRYPT_ROUNDS = 14

RETURN_INFO_STR = 'info'  # For when everything worked, this is the key for the message of goodness
RETURN_ERROR_MESSAGE_STR = 'error_message'  # The error message
RETURN_ERROR_CODE_STR = 'error_code'  # The error code

EVENT_TYPE_STR = 'event_type'
HTTP_METHOD_STR = 'httpMethod'
GET_REQUEST_STR = 'GET'
POST_REQUEST_STR = 'POST'
DELETE_REQUEST_STR = 'DELETE'
EVENT_CREATE_ACCOUNT_STR = 'create_account'
EVENT_VERIFY_ACCOUNT_STR = 'verify_account'
EVENT_DELETE_ACCOUNT_STR = 'delete_account'
EVENT_CHANGE_PASSWORD_STR = 'change_password'
EVENT_LOGIN_STR = 'login'
EVENT_GET_S3_URL_STR = 'get_s3'

VERIFICATION_CODE_SIZE = 30  # The number of characters to use in the verification code
VERIFICATION_LINK = "{0}?event_type=verify_account&username=%s&verification_code=%s".format(API_URL)
VERIFICATION_EMAIL_HEADER = "\From: %s\nTo: %s\nSubject: %s\n\n%s"
VERIFICATION_EMAIL_SUBJECT = "Wingit Account Activation"

# The prompt that is sent to the user to activate their account
USER_ACTIVATION_PROMPT = """
Hello, %s!

Congratulations on creating your Wingit account! Endless chicken opportunties await you. In order to verify your account, please click the link below.

%s

If you did not create this account, then what are you doing with your life?
"""

# Email/password for sending verification email
GMAIL_USER = "cse110wingit@gmail.com"
GMAIL_PASSWORD = 'teamWINGIT!'

MAX_USERNAME_SIZE = 64  # Max size for a username
PASSWORD_HASH_SIZE = 64  # Size of a sha256 hash in chars
HASH_CHARS = "abcdef0123456789"  # The chars that could exist in a sha256 has (lowercase)


################
# SQL THINGIES #
################


# Info for the database connection
RDS_ENDPOINT = "wingitdb.cv6ukx3546be.us-west-1.rds.amazonaws.com"
RDS_USERNAME = "admin"
RDS_PASSWORD = "teamWINGIT!"
RDS_DATABASE = "wingitdb"

USERS_TABLE_NAME = 'USERS'  # The SQL table name for users
PASSWORD_HASH_STR = 'password_hash'  # Password_hash name on database
NEW_PASSWORD_HASH_STR = 'new_hash'
USERNAME_STR = 'username'  # I think you get the point now
VERIFICATION_CODE_STR = 'verification_code'
EMAIL_STR = 'email'
CREATION_TIME_STR = 'creation_time'
S3_REASON_STR = 's3_reason'

# Create the user account
CREATE_ACCOUNT_SQL = "INSERT INTO {0} ({1}, {2}, {3}, {4}, {5}) VALUES (%s, %s, %s, %s, %s)" \
    .format(USERS_TABLE_NAME, USERNAME_STR, EMAIL_STR, VERIFICATION_CODE_STR, CREATION_TIME_STR, PASSWORD_HASH_STR)

# Update a user's password
UPDATE_PASSWORD_SQL = "UPDATE {0} SET {1}=%s WHERE {2} LIKE %s".format(USERS_TABLE_NAME, PASSWORD_HASH_STR, USERNAME_STR)

# Get rows where [column] LIKE [value]
GET_WHERE_USERNAME_LIKE_SQL = "SELECT * FROM {0} WHERE {1} LIKE %s".format(USERS_TABLE_NAME, USERNAME_STR)
GET_WHERE_EMAIL_LIKE_SQL = "SELECT * FROM {0} WHERE {1} LIKE %s".format(USERS_TABLE_NAME, EMAIL_STR)

# Update user verification code
UPDATE_VERIFICATION_CODE_SQL = "UPDATE {0} SET {1} = '' WHERE {2} LIKE %s" \
    .format(USERS_TABLE_NAME, VERIFICATION_CODE_STR, USERNAME_STR)

DELETE_ACCOUNT_SQL = "DELETE FROM {0} WHERE {1} LIKE %s".format(USERS_TABLE_NAME, USERNAME_STR)


def return_message(good_message=None, data=None):
    """
    Builds a return message to send back to the client if everything was processed (could be an error, or not, but at
        least is was handled.
    :param good_message: if not None, then add an extra key/value to the return dict with key=RETURN_GOOD_MESSAGE_STR
        and value=good_message
    :param data: a dictionary of the rest of the data to return
    """
    if data is None:
        data = {}
    if good_message is not None:
        data[RETURN_INFO_STR] = good_message
    return {
        'statusCode': 200,
        'body': json.dumps(data)
    }
