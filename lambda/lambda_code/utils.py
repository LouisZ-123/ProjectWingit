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


def send_password_change_code_email(username, email, code):
    """
    Sends the activation email/link to the given username and email
    """
    message = PASSWORD_CHANGE_EMAIL % (username, code)

    # Set up the server and send the message
    try:

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, email, message)
        server.close()

        # Return something saying everything went alright
        return return_message(good_message='Password Change Email Sent!')

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
    found, vals, val_str_names = _get_str_in_params(list(str_list), params)
    if not found:
        return False, vals

    clean_vals = []
    for val, val_str_name in zip(vals, val_str_names):
        all_good, val = _check_good_param(val, val_str_name)
        if not all_good:
            return False, val
        clean_vals.append(val)

    return True, dict(zip(val_str_names, clean_vals))


def _get_str_in_params(_str, params):
    """
    If _str a tuple: call _get_str_in_params with all elements, and return good for first one that exists
    if _str a list: call _get_str_in_params with all elements, assert all exists and return list
    if _str a string: make sure _str exists in params, then return singleton list of element
    """
    if isinstance(_str, tuple):
        for s in _str:
            found, vals, val_str_names = _get_str_in_params(s, params)
            if found:
                return True, vals, val_str_names
        return False, error(ERROR_MISSING_PARAMS, _str), None

    elif isinstance(_str, list):
        all_vals = []
        all_val_str_names = []
        for s in _str:
            found, vals, val_str_names = _get_str_in_params(s, params)
            if not found:
                return False, error(ERROR_MISSING_PARAMS, s), None
            all_vals += vals
            all_val_str_names += val_str_names
        return True, all_vals, all_val_str_names

    else:
        if _str not in params:
            return False, error(ERROR_MISSING_PARAMS, _str), None
        return True, [params[_str]], [_str]


def _check_good_param(val, val_str_name):
    """
    Check that passed values are good, and return error if not
    """
    if val_str_name == USERNAME_STR:
        val = val.lower()
        if not username_valid(val):
            return False, error(ERROR_INVALID_USERNAME, val)

    elif val_str_name == EMAIL_STR:
        val = fix_email(val)
        if not validate_email(val):
            return False, error(ERROR_INVALID_EMAIL, val)

    elif val_str_name == PASSWORD_HASH_STR:
        val = val.lower()
        if len(val) != PASSWORD_HASH_SIZE or not all(c in HASH_CHARS for c in val):
            return False, error(ERROR_INVALID_PASSWORD_HASH)

    return True, val


def gen_crypt(password_hash):
    """
    Generates the hash and salt to store in the password_hash in the database
    """
    # Make a random salt using the verification code
    salt = generate_verification_code()
    return salt + hashlib.sha256(str.encode(password_hash + salt)).hexdigest()


def password_correct(password_hash, server_password_hash):
    """
    Returns true if the password matches the given password hash
    """
    return server_password_hash[VERIFICATION_CODE_SIZE:] == \
           hashlib.sha256(str.encode(password_hash + server_password_hash[:VERIFICATION_CODE_SIZE])).hexdigest()


def get_new_db_conn():
    """
    Returns a new connection to the database
    """
    return pymysql.connect(RDS_ENDPOINT, user=RDS_USERNAME, passwd=RDS_PASSWORD, db=RDS_DATABASE,
                           cursorclass=pymysql.cursors.DictCursor)


def random_password_change_code():
    """
    Returns a random code for the user to change their password
    """
    return ''.join([random.choice("0123456789") for i in range(PASSWORD_CHANGE_CODE_SIZE)])