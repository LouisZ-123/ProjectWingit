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
    all_good, rest = get_cleaned_params(body, USERNAME_STR, EMAIL_STR, PASSWORD_HASH_STR)
    if not all_good:
        return rest
    username, email, password_hash = rest[USERNAME_STR], rest[EMAIL_STR], rest[PASSWORD_HASH_STR]

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
    all_good, rest = get_cleaned_params(params, USERNAME_STR, VERIFICATION_CODE_STR)
    if not all_good:
        return rest
    username, verification_code = rest[USERNAME_STR], rest[VERIFICATION_CODE_STR]

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
    all_good, ret_dict = get_cleaned_params(params, (USERNAME_STR, EMAIL_STR), (PASSWORD_HASH_STR, PASSWORD_CHANGE_CODE_STR))

    if not all_good:
        return False, ret_dict

    username = ret_dict[USERNAME_STR] if USERNAME_STR in ret_dict else None
    email = ret_dict[EMAIL_STR] if EMAIL_STR in ret_dict else None
    password_hash = ret_dict[PASSWORD_HASH_STR] if PASSWORD_HASH_STR in ret_dict else None
    change_code = ret_dict[PASSWORD_CHANGE_CODE_STR] if PASSWORD_CHANGE_CODE_STR in ret_dict else None

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
        if password_hash is not None and not password_correct(password_hash, result[PASSWORD_HASH_STR]):
            return False, error(ERROR_INCORRECT_PASSWORD)

        elif change_code is not None and (change_code != result[PASSWORD_CHANGE_CODE_STR] or
                                          current_time() - result[PASSWORD_CHANGE_CODE_CREATION_TIME_STR] > CHANGE_PASSWORD_TIMEOUT):
            return False, error(ERROR_INVALID_PASSWORD_CHANGE_CODE)

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
    all_good, username = _verify_login_credentials(body, require_verified=False)
    if not all_good:
        return username

    try:
        conn = get_new_db_conn()
        cursor = conn.cursor()
        cursor.execute(DELETE_ACCOUNT_SQL, [username])
        conn.commit()

        return return_message(good_message="Account Deleted!")
    except Exception as e:
        return error(ERROR_UNKNOWN_ERROR, repr(e))


def get_s3_permissions(params):
    """
    Gets a presigned url for an s3 bucket so a user can upload a file
    """
    # Make sure we have correct params
    all_good, rest = get_cleaned_params(params, PASSWORD_HASH_STR, S3_REASON_STR)
    if not all_good:
        return rest
    password_hash, reason = rest[PASSWORD_HASH_STR], rest[S3_REASON_STR]

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


def change_password(body):
    """
    Updates the user's password in the database.
    """
    # Make sure we have correct params
    all_good, rest = get_cleaned_params(body, NEW_PASSWORD_HASH_STR)
    if not all_good:
        return rest

    new_hash = rest[NEW_PASSWORD_HASH_STR]

    # Attempt to login with the given credentials, and if it fails, return the login error
    all_good, username = _verify_login_credentials(body, require_verified=False)
    if not all_good:
        return username

    try:
        conn = get_new_db_conn()
        cursor = conn.cursor()
        cursor.execute(UPDATE_PASSWORD_SQL, [gen_crypt(new_hash), username])
        conn.commit()

        return return_message(good_message="Password changed!")
    except Exception as e:
        return error(ERROR_UNKNOWN_ERROR, repr(e))


def get_password_change_code(params):
    """
    Sends a password change code to the username
    """
    all_good, ret_dict = get_cleaned_params(params, (USERNAME_STR, EMAIL_STR))
    if not all_good:
        return ret_dict
    username = ret_dict[USERNAME_STR] if USERNAME_STR in ret_dict else None
    email = ret_dict[EMAIL_STR] if EMAIL_STR in ret_dict else None

    try:
        conn = get_new_db_conn()
        cursor = conn.cursor()

        if username is not None:
            cursor.execute(GET_WHERE_USERNAME_LIKE_SQL, [username])
        else:
            cursor.execute(GET_WHERE_EMAIL_LIKE_SQL, [email])

        result = cursor.fetchone()

        if result is None:
            if username is not None:
                return error(ERROR_USERNAME_DOES_NOT_EXIST, username)
            return error(ERROR_EMAIL_DOES_NOT_EXIST, email)

        code = random_password_change_code()
        cursor.execute(UPDATE_PASSWORD_CHANGE_CODE_SQL.replace('%d', str(current_time())), [code, result[USERNAME_STR]])
        conn.commit()

        return send_password_change_code_email(username, result[EMAIL_STR], code)
    except Exception as e:
        return error(ERROR_UNKNOWN_ERROR, repr(e))