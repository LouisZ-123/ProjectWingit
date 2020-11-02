"""
The code that performs the actions specified in lambda_handler
"""
from lambda_code.utils import *
from lambda_code.errors import *
from lambda_code.constants import *


def create_account(params):
    """
    Attempt to create a new account.
    
    This new account must not have the same username or email as an already
        existing account. The username and password must be working usernames
        and emails.
    If the account can be created, an email will be sent to the specified email
        with a link to activate the account. A random string of alphanumeric
        characters will be made as a verification code
    :param params: the parameters
    """
    all_good, *rest = get_cleaned_params(params, USERNAME_STR, EMAIL_STR, PASSWORD_STR)
    if not all_good:
        return rest[0]
    username, email, password = rest

    # All of this is dependant on the SQL database existing and the connection existing,
    #   so we will put it all in a try-catch since things can break easily
    try:

        # Search the database to make sure the username and email does not already exist
        conn = get_new_db_conn()
        cursor = conn.cursor()
        cursor.execute(GET_WHERE_USERNAME_LIKE_SQL, [username])

        # Make sure there is no duplicate username
        if not cursor.fetchone() is None:
            return error(ERROR_USERNAME_ALREADY_EXISTS, username)

        # Search for email
        cursor.execute(GET_WHERE_EMAIL_LIKE_SQL, [email])
        if not cursor.fetchone() is None:
            return error(ERROR_EMAIL_ALREADY_IN_USE, email)

        # Everything looks good, make the account
        verification_code = generate_verification_code()
        password_hash = gen_crypt(password)
        account_info = (username, email, verification_code, current_time(), password_hash)

        cursor.execute(CREATE_ACCOUNT_SQL, account_info)
        conn.commit()  # Commit the changes to the database

    except Exception as e:
        return error(ERROR_UNKNOWN_ERROR, repr(e))

    # Send the email to the user telling them to activate their account
    return send_activation_email(username, email, verification_code)


def verify_account(params):
    """
    Verifies the given account (only needs username and verification_code)
    :param params: the params passed in the GET call
    """
    all_good, *rest = get_cleaned_params(params, USERNAME_STR, VERIFICATION_CODE_STR)
    if not all_good:
        return rest[0]
    username, verification_code = rest

    # Actually check to see if the verification code matches the database
    try:
        conn = get_new_db_conn()
        cursor = conn.cursor()
        cursor.execute(GET_WHERE_USERNAME_LIKE_SQL, [username])

        result = cursor.fetchone()

        # If the username does not exist
        if result is None:
            return error(ERROR_USERNAME_DOES_NOT_EXIST, username)

        # If the verification code is currently null (already verified), or if
        #   the verification codes match, then verify the account
        if result[VERIFICATION_CODE_STR] == '':
            pass
        elif result[VERIFICATION_CODE_STR] == verification_code:
            cursor.execute(UPDATE_VERIFICATION_CODE_SQL, [username])
            conn.commit()  # Commit the changes to the database
        else:
            return error(ERROR_UNMATCHING_VERIFICATION_CODE, verification_code, username)

        return return_message(good_message='Account Verified!')

    except Exception as e:
        return error(ERROR_UNKNOWN_ERROR, repr(e))


def login_account(params):
    """
    Returns the string "Credentials Accepted" to affirm that the username/email
    (defaults to email if both are given) match the given password_hash
    """
    username, email = None, None

    # Check for email and password
    all_good, *rest = get_cleaned_params(params, EMAIL_STR, PASSWORD_STR)

    # Didn't work, check for username and password
    if not all_good:

        # Check if the error is with the email, not that it doesn't exist
        if eval(rest[0]['body'])[RETURN_ERROR_CODE_STR] != ERROR_MISSING_PARAMS[2]:
            return rest[0]

        # Otherwise try and get a username
        all_good, *rest = get_cleaned_params(params, USERNAME_STR, PASSWORD_STR)

        # Didn't work either, return error
        if not all_good:
            return rest[0]

        # Otherwise, set username and password
        username, password = rest

    # It did work, set email and password
    else:
        email, password = rest

    try:
        conn = get_new_db_conn()
        cursor = conn.cursor()

        # Query will depend on whether or not we are using email/password
        if email is not None:
            cursor.execute(GET_WHERE_EMAIL_LIKE_SQL, [email])
        else:
            cursor.execute(GET_WHERE_USERNAME_LIKE_SQL, [username])

        result = cursor.fetchone()

        # If the username/email does not exist
        if result is None:
            return error(ERROR_EMAIL_DOES_NOT_EXIST, email) if email is not None else \
                error(ERROR_USERNAME_DOES_NOT_EXIST, username)

        # If the account has not yet been verified
        if result[VERIFICATION_CODE_STR] != '':
            return error(ERROR_ACCOUNT_UNVERIFIED)

        # If the password_hash does not match, tell them
        if not password_correct(password, result[PASSWORD_HASH_STR]):
            return error(ERROR_INCORRECT_PASSWORD)

        return return_message(good_message='Credentials Accepted!')

    except Exception as e:
        return error(ERROR_UNKNOWN_ERROR, repr(e))
