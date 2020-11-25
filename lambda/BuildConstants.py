from lambda_code.constants import *
from lambda_code.utils import gen_crypt, generate_verification_code, fix_email
import hashlib

# Test account info
TEST_ACCOUNT_VERIFIED_USERNAME = 'wingit_testing_account_verified'
TEST_ACCOUNT_VERIFIED_EMAIL = 'wingit.testing.account.verified@gmail.com'
TEST_ACCOUNT_PASSWORD_HASH = hashlib.sha256(b"TestPassword!1").hexdigest()

TEST_ACCOUNT_UNVERIFIED_USERNAME = 'wingit_testing_account_unverified'
TEST_ACCOUNT_UNVERIFIED_EMAIL = 'wingit.testing.account.unverified@gmail.com'

TEST_ACCOUNT_VERIFIED_KWARGS = {
    USERNAME_STR: TEST_ACCOUNT_VERIFIED_USERNAME,
    EMAIL_STR: fix_email(TEST_ACCOUNT_VERIFIED_EMAIL),
    VERIFICATION_CODE_STR: '',
    CREATION_TIME_STR: -1,
    PASSWORD_HASH_STR: gen_crypt(TEST_ACCOUNT_PASSWORD_HASH)
}

TEST_ACCOUNT_UNVERIFIED_KWARGS = {
    USERNAME_STR: TEST_ACCOUNT_UNVERIFIED_USERNAME,
    EMAIL_STR: fix_email(TEST_ACCOUNT_UNVERIFIED_EMAIL),
    VERIFICATION_CODE_STR: generate_verification_code(),
    CREATION_TIME_STR: -1,
    PASSWORD_HASH_STR: gen_crypt(TEST_ACCOUNT_PASSWORD_HASH)
}

# SQL info
DELETE_USERS_TABLE_SQL = "DROP TABLE IF EXISTS %s" % USERS_TABLE_NAME

# Data for making the sql database
_VARCHAR_SIZE = 255
_SERVER_PASSWORD_HASH_SIZE = len(gen_crypt("dfaonefdkaj"))

# Just need to input a tuple here with the string name for the column, and what datatype should be
_CREATE_USERS_TABLE_ARGS = [
    (USERNAME_STR, "varchar(%d) not null" % _VARCHAR_SIZE),
    (EMAIL_STR, "varchar(%d) not null" % _VARCHAR_SIZE),
    (VERIFICATION_CODE_STR, "char(%d)" % VERIFICATION_CODE_SIZE),
    (CREATION_TIME_STR, "bigint"),
    (PASSWORD_HASH_STR, "char(%d) not null" % _SERVER_PASSWORD_HASH_SIZE),
]

CREATE_USERS_TABLE_SQL = """CREATE TABLE %s (
%s);""" % (USERS_TABLE_NAME, ''.join(_str + " " + _type + ",\n" for _str, _type in _CREATE_USERS_TABLE_ARGS)[:-2])


def make_insert_sql(table_name, **kwargs):
    """
    Makes the sql and sql_args to insert all values in kwargs into table_name
    """
    column_names = ''.join(key + ", " for key, val in kwargs.items())[:-2]
    values_str = ''.join('%s, ' for key, val in kwargs.items())[:-2]
    return "INSERT INTO {0} ({1}) VALUES ({2})".format(table_name, column_names, values_str), \
           [val for key, val in kwargs.items()]


##################
# Java Constants #
##################


JAVA_CONSTANTS_FILE_DIR = "../app/src/main/java/com/wingit/projectwingit/utils"
JAVA_CONSTANTS_CLASS_NAME = "WingitLambdaConstants"
JAVA_CONSTANTS_FILE_PATH = "../app/src/main/java/com/wingit/projectwingit/utils/%s.java" % JAVA_CONSTANTS_CLASS_NAME
JAVA_PACKAGE_PATH = JAVA_CONSTANTS_FILE_DIR.replace('../app/src/main/java/', '').replace('/', '.')

JAVA_CONSTANTS_FILE_DATA = """package %(package)s;

/*
 * An automatically generated list of constants from the lambda API
 */

public class %(classname)s {
    public static final String API_URL = "%(API_URL)s";
    public static final String RETURN_SUCCESS_STR = "%(RETURN_SUCCESS_STR)s";
    public static final String RETURN_GOOD_MESSAGE_STR = "%(RETURN_GOOD_MESSAGE_STR)s";
    public static final String RETURN_ERROR_MESSAGE_STR = "%(RETURN_ERROR_MESSAGE_STR)s";
    public static final String RETURN_ERROR_CODE_STR = "%(RETURN_ERROR_CODE_STR)s";
    public static final String EVENT_TYPE_STR = "%(EVENT_TYPE_STR)s";
    public static final String EVENT_CREATE_ACCOUNT_STR = "%(EVENT_CREATE_ACCOUNT_STR)s";
    public static final String EVENT_LOGIN_STR = "%(EVENT_LOGIN_STR)s";
    public static final String PASSWORD_HASH_STR = "%(PASSWORD_HASH_STR)s";
    public static final String USERNAME_STR = "%(USERNAME_STR)s";
    public static final String EMAIL_STR = "%(EMAIL_STR)s";
}
""" % {
    'package': JAVA_PACKAGE_PATH,
    'classname': JAVA_CONSTANTS_CLASS_NAME,
    'API_URL': API_URL,
    'RETURN_SUCCESS_STR': RETURN_SUCCESS_STR,
    'RETURN_GOOD_MESSAGE_STR': RETURN_GOOD_MESSAGE_STR,
    'RETURN_ERROR_MESSAGE_STR': RETURN_ERROR_MESSAGE_STR,
    'RETURN_ERROR_CODE_STR': RETURN_ERROR_CODE_STR,
    'EVENT_TYPE_STR': EVENT_TYPE_STR,
    'EVENT_CREATE_ACCOUNT_STR': EVENT_CREATE_ACCOUNT_STR,
    'EVENT_LOGIN_STR': EVENT_LOGIN_STR,
    'PASSWORD_HASH_STR': PASSWORD_HASH_STR,
    'USERNAME_STR': USERNAME_STR,
    'EMAIL_STR': EMAIL_STR,
}


###############
# MISC THINGS #
###############


IMPLEMENTED_HTTP_METHODS = [GET_REQUEST_STR, POST_REQUEST_STR, DELETE_REQUEST_STR]
