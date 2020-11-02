"""
Test cases for the lambda API
"""
from tests.LambdaTestUtils import *
from lambda_code.errors import *
from BuildConstants import *


class TestLambda:
    """
    If you want to add a test method to this class, make sure the method name starts with "test_" and takes no args
    so that the test_all() function will find it and test it, and make sure nothing else in this class starts with
    "test_" so there are no collisions
    """

    @staticmethod
    def assert_true(b, message='No message'):
        """
        If b is not true, then raise an error
        """
        if not b:
            raise ValueError('%s is not True:\n%s' % (b, message))

    @staticmethod
    def assert_equal(a, b, message='No message'):
        """
        If a != b, then raise an error
        """
        if a != b:
            raise ValueError('%s != %s:\n %s' % (a, b, message))

    @staticmethod
    def _cpy_params(params, error_tup, param_str):
        """
        Copies and updates the params input for a few tests that need it
        """
        _params = params.copy()
        _params['error_tup'] = error_tup
        if param_str in _params:
            del _params[param_str]
        return _params

    def assert_no_server_error(self, **params):
        """
        Asserts there is no error from the server
        """
        response = request(**params)
        self.assert_true(RETURN_ERROR_CODE_STR not in response, "Error from server with params %s:\n%s" %
                         (params, response))

    def assert_server_error(self, error_tup=None, **params):
        """
        Asserts a server-side error response
        """
        response = request(**params)
        self.assert_true(RETURN_ERROR_CODE_STR in response,
                         "No error from params: %s, \nFull message: %s" % (params, response))

        if error_tup is not None:
            err_str = "Error codes not equal for expected code '%s', instead got '%s'\nFull Error: %s"
            self.assert_equal(response[RETURN_ERROR_CODE_STR], error_tup[0],
                              err_str % (ALL_ERROR_NAMES_BY_CODE[error_tup[0]],
                                         ALL_ERROR_NAMES_BY_CODE[response[RETURN_ERROR_CODE_STR]], response))

    def assert_server_handles_bad_username(self, **params):
        """
        Asserts the server knows how to handle bad usernames no matter the event that is using them
        """
        _params = self._cpy_params(params, ERROR_INVALID_USERNAME, USERNAME_STR)

        # Incorrect size
        _params[USERNAME_STR] = ''
        self.assert_server_error(**_params)

        _params[USERNAME_STR] = random_str(MAX_USERNAME_SIZE + 1)
        self.assert_server_error(**_params)

        _params[USERNAME_STR] = random_str(MAX_USERNAME_SIZE * 7)
        self.assert_server_error(**_params)

        # Invalid characters
        _params[USERNAME_STR] = ' '
        self.assert_server_error(**_params)

        _params[USERNAME_STR] = 'good_user_name_ohno!'
        self.assert_server_error(**_params)

        _params[USERNAME_STR] = random_str(MAX_USERNAME_SIZE, all_ascii=True)[:-1] + "`"
        self.assert_server_error(**_params)

        _params[USERNAME_STR] = '\"\';'
        self.assert_server_error(**_params)

    def assert_server_handles_bad_email(self, **params):
        """
        Asserts the server knows how to handle bad emails no matter the event that is using them
        """
        _params = self._cpy_params(params, ERROR_INVALID_EMAIL, EMAIL_STR)

        # Doesn't have @
        _params[EMAIL_STR] = ""
        self.assert_server_error(**_params)

        _params[EMAIL_STR] = "apples.com"
        self.assert_server_error(**_params)

        _params[EMAIL_STR] = random_str(64, all_ascii=False).replace('@', '')
        self.assert_server_error(**_params)

        # Has multiple @
        _params[EMAIL_STR] = "apples@j@gmail.com"
        self.assert_server_error(**_params)

        # Nothing before/after @
        _params[EMAIL_STR] = "@gmail.com"
        self.assert_server_error(**_params)

        _params[EMAIL_STR] = "good@"
        self.assert_server_error(**_params)

        # Multiple periods after @ (adjacent)
        _params[EMAIL_STR] = "good@gmail..com"
        self.assert_server_error(**_params)

    def assert_server_handles_bad_password(self, **params):
        """
        Asserts the server knows how to handle bad passwords
        """
        _params = self._cpy_params(params, ERROR_INVALID_PASSWORD, PASSWORD_STR)

        # Password too small/empty
        _params[PASSWORD_STR] = ''
        self.assert_server_error(**_params)

        _params[PASSWORD_STR] = random_str(MIN_PASSWORD_SIZE - 1, all_ascii=False)
        self.assert_server_error(**_params)

    def assert_server_handles_invalid_inputs(self, **params):
        """
        Used to more easily call the bad username, email, password_hash so it is done correctly
        Each value passed in params will be tested for invalid input (if it has a test below)
        """
        # Check not enough/correct args
        self.assert_server_missing_params(**params)

        # Check invalid individual args
        if USERNAME_STR in params:
            self.assert_server_handles_bad_username(**params)
        if EMAIL_STR in params:
            self.assert_server_handles_bad_email(**params)
        if PASSWORD_STR in params:
            self.assert_server_handles_bad_password(**params)

    def assert_server_missing_params(self, **params):
        """
        Switches through permutations of missing parameters to make sure the server only accepts if all params
            are accounted for. Assumes error_code: 'ERROR_MISSING_PARAMS'
        """
        keys = [k for k in params.keys() if k != EVENT_TYPE_STR]

        # Go through every permutation using binary (except the last one because that should work)
        for s in get_binary_permutations(len(keys))[:-1]:
            # Get all the params that have a '1' in their index
            curr_params = {keys[i]: params[keys[i]] for i, b in enumerate(s) if b == '1'}
            curr_params[EVENT_TYPE_STR] = params[EVENT_TYPE_STR]
            self.assert_server_error(error_tup=ERROR_MISSING_PARAMS, **curr_params)

    def test_account_creation_fails(self):
        """
        Testing the user account creation API
        """

        # The full set of parameters that could theoretically pass invalid checks
        password = random_valid_password()
        username = random_valid_username()
        params = {
            EVENT_TYPE_STR: EVENT_CREATE_ACCOUNT_STR,
            USERNAME_STR: username,
            EMAIL_STR: random_valid_email(),
            PASSWORD_STR: password
        }

        # Check inputs are missing/invalid
        self.assert_server_handles_invalid_inputs(**params)

        # Doing usernames that have already been taken (including caps/no caps/periods in email)
        params['error_tup'] = ERROR_USERNAME_ALREADY_EXISTS

        #           Lowercase
        params[USERNAME_STR] = TEST_ACCOUNT_VERIFIED_USERNAME
        self.assert_server_error(**params)

        #           Uppercase
        params[USERNAME_STR] = TEST_ACCOUNT_VERIFIED_USERNAME.upper()
        self.assert_server_error(**params)

        # Doing emails that have already been taken
        params['error_tup'] = ERROR_EMAIL_ALREADY_IN_USE
        params[USERNAME_STR] = username

        #           Normal email
        params[EMAIL_STR] = TEST_ACCOUNT_VERIFIED_EMAIL
        self.assert_server_error(**params)

        #           No periods
        params[EMAIL_STR] = TEST_ACCOUNT_VERIFIED_EMAIL.split('@')[0].replace('.', '') \
                            + '@' + TEST_ACCOUNT_VERIFIED_EMAIL.split('@')[1]
        self.assert_server_error(**params)

        #           Lots of periods
        params[EMAIL_STR] = TEST_ACCOUNT_VERIFIED_EMAIL[:4] + "......" + TEST_ACCOUNT_VERIFIED_EMAIL[4:]
        self.assert_server_error(**params)

    def test_account_login(self):
        """
        Testing login to an existing user account
        """
        params = {
            EVENT_TYPE_STR: EVENT_LOGIN_STR,
            EMAIL_STR: random_valid_email(),
            PASSWORD_STR: random_valid_password()
        }

        # Check not enough/correct args for both username and email
        self.assert_server_handles_invalid_inputs(**params)

        del params[EMAIL_STR]
        params[USERNAME_STR] = random_valid_username()
        self.assert_server_handles_invalid_inputs(**params)

        # Check incorrect username/email, but a functional password
        params = {EVENT_TYPE_STR: EVENT_LOGIN_STR, 'error_tup': ERROR_USERNAME_DOES_NOT_EXIST,
                  PASSWORD_STR: TEST_ACCOUNT_PASSWORD, USERNAME_STR: random_valid_username()}
        self.assert_server_error(**params)

        params = {EVENT_TYPE_STR: EVENT_LOGIN_STR, 'error_tup': ERROR_EMAIL_DOES_NOT_EXIST,
                  PASSWORD_STR: TEST_ACCOUNT_PASSWORD, EMAIL_STR: random_valid_email()}
        self.assert_server_error(**params)

        # Check correct username/email, but wrong password
        params = {EVENT_TYPE_STR: EVENT_LOGIN_STR, 'error_tup': ERROR_INCORRECT_PASSWORD,
                  PASSWORD_STR: random_valid_password(), USERNAME_STR: TEST_ACCOUNT_VERIFIED_USERNAME}
        self.assert_server_error(**params)

        params = {EVENT_TYPE_STR: EVENT_LOGIN_STR, 'error_tup': ERROR_INCORRECT_PASSWORD,
                  PASSWORD_STR: random_valid_password(), EMAIL_STR: TEST_ACCOUNT_VERIFIED_EMAIL}
        self.assert_server_error(**params)

        # Check correct everything, but an unverified account
        params = {EVENT_TYPE_STR: EVENT_LOGIN_STR, 'error_tup': ERROR_ACCOUNT_UNVERIFIED,
                  PASSWORD_STR: TEST_ACCOUNT_PASSWORD, EMAIL_STR: TEST_ACCOUNT_UNVERIFIED_EMAIL}
        self.assert_server_error(**params)

        params = {EVENT_TYPE_STR: EVENT_LOGIN_STR, 'error_tup': ERROR_ACCOUNT_UNVERIFIED,
                  PASSWORD_STR: TEST_ACCOUNT_PASSWORD, USERNAME_STR: TEST_ACCOUNT_UNVERIFIED_USERNAME}
        self.assert_server_error(**params)

        # Check logging in with email and username both work
        params = {EVENT_TYPE_STR: EVENT_LOGIN_STR, PASSWORD_STR: TEST_ACCOUNT_PASSWORD,
                  EMAIL_STR: TEST_ACCOUNT_VERIFIED_EMAIL}
        self.assert_no_server_error(**params)

        params = {EVENT_TYPE_STR: EVENT_LOGIN_STR, PASSWORD_STR: TEST_ACCOUNT_PASSWORD,
                  USERNAME_STR: TEST_ACCOUNT_VERIFIED_USERNAME}
        self.assert_no_server_error(**params)

    def test_misc(self):
        """
        Test miscellaneous things
        """
        # Check that there is an error if there is no event_type in params,
        #   even if all other params are sent for a function
        params = {'error_tup': ERROR_NO_EVENT_TYPE, USERNAME_STR: 'a', EMAIL_STR: 'a@b.c'}
        self.assert_server_error(**params)

        # Error if an unknown event type is passed
        params = {'error_tup': ERROR_UNKNOWN_EVENT_TYPE, EVENT_TYPE_STR: "uhfn01q7hrn0dfq9und-q"}
        self.assert_server_error(**params)

    def test_all(self):
        """
        Runs all methods in this test class that start with the string "test_"
        """
        tests_run = 0
        for s in [s for s in dir(self) if s.startswith('test_') and s != 'test_all']:
            print("Testing: %s()..." % s)
            self.__getattribute__(s)()
            tests_run += 1
            print("Test Passed!")
        print("\nPassed all %d tests!\n" % tests_run)
