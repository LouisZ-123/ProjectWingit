"""
The code that performs the actions specified in lambda_handler
"""
from lambda_code.utils import *
from lambda_code.s3_utils import *


def create_account(body):
    """
    Attempt to create a new account.
    
    This new account must not have the same username or email as an already
        existing account. The username and password must be working usernames
        and emails.
    If the account can be created, an email will be sent to the specified email
        with a link to activate the account. A random string of alphanumeric
        characters will be made as a verification code
    :param body: the parameters
    """
    all_good, *rest = get_cleaned_params(body, USERNAME_STR, EMAIL_STR, PASSWORD_HASH_STR)
    if not all_good:
        return rest[0]
    username, email, password_hash = rest

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
        server_password_hash = gen_crypt(password_hash)
        account_info = (username, email, verification_code, current_time(), server_password_hash)

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


def _verify_login_credentials(params, require_verified=True):
    """
    Verifies the login credentials are correct.
    :param params: could contain either email or username, along with password
    :param require_verified: if True, return an error if the account is not yet verified
    :return: a tuple with 1st element: False if there was an error, True if all good, 2nd element: the return
        error if there was an error, or the username of the login (irregardless of if the user gave email or username)
    """
    username, email = None, None

    # Check for email and password
    all_good, *rest = get_cleaned_params(params, EMAIL_STR, PASSWORD_HASH_STR)

    # Didn't work, check for username and password
    if not all_good:

        # Check if the error is with the email, not that it doesn't exist
        if json.loads(rest[0]['body'])[RETURN_ERROR_CODE_STR] != ERROR_MISSING_PARAMS[2]:
            return False, rest[0]

        # Otherwise try and get a username
        all_good, *rest = get_cleaned_params(params, USERNAME_STR, PASSWORD_HASH_STR)

        # Didn't work either, return error
        if not all_good:
            return False, rest[0]

        # Otherwise, set username and password
        username, password_hash = rest

    # It did work, set email and password
    else:
        email, password_hash = rest

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
            return (False, error(ERROR_EMAIL_DOES_NOT_EXIST, email)) if email is not None else \
                (False, error(ERROR_USERNAME_DOES_NOT_EXIST, username))

        # If the account has not yet been verified
        if require_verified and result[VERIFICATION_CODE_STR] != '':
            return False, error(ERROR_ACCOUNT_UNVERIFIED)

        # If the password_hash does not match, tell them
        if not password_correct(password_hash, result[PASSWORD_HASH_STR]):
            return False, error(ERROR_INCORRECT_PASSWORD)

        return True, result[USERNAME_STR]

    except Exception as e:
        return False, error(ERROR_UNKNOWN_ERROR, repr(e))


def login_account(params):
    """
    Returns the string "Credentials Accepted" to affirm that the username/email
    (defaults to email if both are given) match the given password_hash
    """
    all_good, e = _verify_login_credentials(params)
    if not all_good:
        return e
    return return_message(good_message='Credentials Accepted!')


def delete_account(body):
    """
    Delete a user's account
    """
    # Attempt to login with the given credentials, and if it fails, return the login error
    all_good, other = _verify_login_credentials(body, require_verified=False)
    if not all_good:
        return other
    username = other

    try:
        conn = get_new_db_conn()
        cursor = conn.cursor()
        result = cursor.execute(DELETE_ACCOUNT_SQL, username)
        conn.commit()

        return return_message(good_message="Account Deleted!")
    except Exception as e:
        return error(ERROR_UNKNOWN_ERROR, repr(e))


def get_s3_permissions(params):
    """
    Gets a presigned url for an s3 bucket so a user can upload a file
    """
    # Make sure we have correct params
    all_good, *rest = get_cleaned_params(params, PASSWORD_HASH_STR, S3_REASON_STR)
    if not all_good:
        return rest[0]
    password_hash, reason = rest

    # Attempt to login with the given credentials, and if it fails, return the login error
    all_good, username = _verify_login_credentials(params)
    if not all_good:
        return username
    
    # It worked, so now we need to build the extra info for the return message
    all_good, extra_s3_info = get_extra_s3_info(username, reason)
    if not all_good:
        return extra_s3_info

    if reason == S3_REASON_UPLOAD_USER_PROFILE_IMAGE:
        all_good, ret = create_presigned_post(extra_s3_info[S3_IMAGE_DEST_STR])
    else:
        return error(ERROR_IMPOSSIBLE_ERROR, "get_s3_permissions (reason should already be good now because "
                                             "get_extra_s3_info should have checked it)")

    return ret if not all_good else return_message(data=ret)