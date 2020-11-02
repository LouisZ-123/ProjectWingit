from lambda_code.validate_email import validate_email
from lambda_code.errors import *
from lambda_code.constants import *
import time
import random
import smtplib
import hashlib
import lambda_code.pymysql as pymysql
import string


def username_valid(username):
    """
    Checks to make sure the username contains only the characters:
        - A-Z
        - a-z
        - 0-9
        - Underscore "_"
    :param username: the string username to check
    :returns: True or False
    """

    # Make sure the username is not empty or too large
    if len(username) == 0 or len(username) > MAX_USERNAME_SIZE:
        return False

    for c in username:
        if not c.isalnum() and not c == "_":
            return False
    return True


def current_time():
    """
    Return the current time in millis to keep track of when accounts were
    created, to delete non-verified accounts after a certain amount of time
    """
    return round(time.time() * 1000)


def generate_verification_code():
    """
    Generates a verification code to verify the account, full of random
    characters
    """
    return ''.join(random.choice(string.ascii_letters) for i in range(VERIFICATION_CODE_SIZE))


def send_activation_email(username, email, verification_code):
    """
    Sends the activation email/link to the given username and email
    """
    link = VERIFICATION_LINK % (username, verification_code)

    message = VERIFICATION_EMAIL_HEADER % (GMAIL_USER, email, VERIFICATION_EMAIL_SUBJECT,
                                           USER_ACTIVATION_PROMPT % (username, link))

    # Set up the server and send the message
    try:

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, email, message)
        server.close()

        # Return something saying everything went alright
        return return_message(good_message='Account Created!')

    except Exception as e:
        return error(ERROR_UNKNOWN_ERROR, repr(e))


def fix_email(email):
    """
    Removes all periods before the '@' and changes to all lowercase to get unique email address
    """
    email = email.lower()

    # Only remove before '@', or everywhere if there is no '@'
    idx = email.index('@') if '@' in email else len(email)
    return email[:idx].replace('.', '') + email[idx:]


def get_cleaned_params(params, *str_list):
    """
    Gets all of the parameters requested in str_list, cleaned up depending on the param
    Each param is immediately turned into a string before cleaning, and filtered further from there depending
        on what param it is

    If any error occurs, then a 2-tuple is returned: False, and the error that should be returned to the user

    Otherwise, the tuple returned is of size len(str_list) + 1 with the first element being True, and the rest of the
        elements as the cleaned parameters in the order of str_list

    :param params: the params
    :param str_list: the list of string params keys to get and clean
    """
    ret = [True, ]
    for _str in str_list:

        # Check to make sure string is in params
        if _str not in params:
            return False, error(ERROR_MISSING_PARAMS, _str)

        val = str(params[_str])

        # Clean if it needs cleaning, otherwise just add to the list
        # Don't need to do anything special for password or verification code, so they're not listed
        if _str == USERNAME_STR:
            val = val.lower()
            if not username_valid(val):
                return False, error(ERROR_INVALID_USERNAME, val)

        elif _str == EMAIL_STR:
            val = fix_email(val)
            if not validate_email(val):
                return False, error(ERROR_INVALID_EMAIL, val)

        elif _str == PASSWORD_STR:
            if len(val) < MIN_PASSWORD_SIZE:
                return False, error(ERROR_INVALID_PASSWORD,
                                    "Password must be at least %d characters long" % MIN_PASSWORD_SIZE)

        ret.append(val)

    return tuple(ret)


def gen_crypt(password):
    """
    Generates the hash and salt to store in the password_hash in the database
    """
    # Make a random salt using the verification code
    salt = generate_verification_code()
    return salt + hashlib.sha256(str.encode(password + salt)).hexdigest()


def password_correct(password, password_hash):
    """
    Returns true if the password matches the given password hash
    """
    return password_hash[VERIFICATION_CODE_SIZE:] == \
           hashlib.sha256(str.encode(password + password_hash[:VERIFICATION_CODE_SIZE])).hexdigest()


def get_new_db_conn():
    """
    Returns a new connection to the database
    """
    return pymysql.connect(RDS_ENDPOINT, user=RDS_USERNAME, passwd=RDS_PASSWORD, db=RDS_DATABASE,
                           cursorclass=pymysql.cursors.DictCursor)
