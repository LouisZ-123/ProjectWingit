"""
Test cases for the lambda API
"""
from LambdaUtils import *
import unittest
import hashlib

ERROR_CODES = get_error_codes()
REVERSE_ERROR_CODES = {val: key for key, val in ERROR_CODES.items()}


class TestLambda(unittest.TestCase):

    def assertNoServerError(self, **params):
        """
        Asserts there is no error from the server
        :param params: a kwargs list of params
        """
        response = request(**params)
        self.assertTrue('error' not in response, "Error from server: %s" % params)

    def assertServerError(self, error_code=None, **params):
        """
        Asserts a server-side error response
        :param error_code: if not None: the name of the error that should occur
        :param params: a kwargs list of params
        """
        response = request(**params)
        self.assertTrue('error' in response, "No error from params: %s" % params)

        if error_code is not None:
            err_str = "Error codes not equal for expected code '%s', instead got '%s'\nFull Error: %s"
            self.assertEqual(response['error_code'], ERROR_CODES[error_code],
                             err_str % (error_code, REVERSE_ERROR_CODES[response['error_code']], response))

    def assertServerHandlesBadUsername(self, event_type, **params):
        """
        Asserts the server knows how to handle bad usernames no matter the event that is using them
        :param event_type: the event type calling for username/password usage
        :param params: a kwargs list of extra params that should be passed in the call so no ERROR_MISSING_PARAMS
        """
        params.update({'error_code': 'ERROR_INVALID_USERNAME', 'event_type': event_type})

        # Incorrect size
        self.assertServerError(username='', **params)
        self.assertServerError(username=random_str(65), **params)
        self.assertServerError(username=random_str(200), **params)

        # Invalid characters
        self.assertServerError(username=' ', **params)
        self.assertServerError(username='good_user_name_ohno!', **params)
        self.assertServerError(username=random_64(all_hex=False)[:63] + "`", **params)
        self.assertServerError(username='\"\'', **params)

    def assertServerHandlesBadPasswordHash(self, event_type, **params):
        """
        Asserts the server knows how to handle bad password hashes no matter the event that is using them
        :param event_type: the event type calling for username/password usage
        :param params: a kwargs list of extra params that should be passed in the call so no ERROR_MISSING_PARAMS
        """
        params.update({'error_code': 'ERROR_INVALID_PASSWORD_HASH', 'event_type': event_type})

        # Incorrect size
        self.assertServerError(password_hash='', **params)
        self.assertServerError(password_hash='a', **params)
        self.assertServerError(password_hash='78dh1739f7', **params)
        self.assertServerError(password_hash=random_str(65), **params)
        self.assertServerError(password_hash=random_str(200), **params)

        # Bad characters
        for i in range(10):
            self.assertServerError(password_hash=random_64(all_hex=False), **params)
        self.assertServerError(password_hash=random_64(all_hex=False)[:63] + 'g', **params)

    def assertServerHandlesBadEmail(self, event_type, **params):
        """
        Asserts the server knows how to handle bad emails no matter the event that is using them
        :param event_type: the event type calling for username/password usage
        :param params: a kwargs list of extra params that should be passed in the call so no ERROR_MISSING_PARAMS
        """
        params.update({'error_code': 'ERROR_INVALID_EMAIL', 'event_type': event_type})

        # Doesn't have @
        self.assertServerError(email="", **params)
        self.assertServerError(email="apples.com", **params)
        self.assertServerError(email=random_64(all_hex=False).replace('@', ''), **params)

        # Has multiple @
        self.assertServerError(email="apples@j@gmail.com", **params)

        # Nothing before/after @
        self.assertServerError(email="@gmail.com", **params)
        self.assertServerError(email="good@", **params)

    def assertServerHandlesBadUEP(self, event_type, username=False, email=False, password_hash=False, _all=False):
        """
        Used to more easily call the bad username, email, password_hash so it is done correctly
        """
        if username or _all:
            self.assertServerHandlesBadUsername(event_type, email='e@a.com', password_hash=random_64())
        if email or _all:
            self.assertServerHandlesBadEmail(event_type, username='a', password_hash=random_64())
        if password_hash or _all:
            self.assertServerHandlesBadPasswordHash(event_type, email='e@a.com', username='a')

    def assertServerMissingParams(self, event_type, **params):
        """
        Switches through permutations of missing parameters to make sure the server only accepts if all params
            are accounted for. Assumes error_code: 'ERROR_MISSING_PARAMS'
        """
        keys = list(params.keys())

        # Go through every permutation using binary (except the last one because that should work)
        for s in get_binary_permutations(len(params.keys()))[:-1]:
            # Get all the params that have a '1' in their index
            curr_params = {keys[i]: params[keys[i]] for i, b in enumerate(s) if b == '1'}
            curr_params['event_type'] = event_type
            self.assertServerError(error_code='ERROR_MISSING_PARAMS', **curr_params)

    def test_account_creation_fails(self):
        """
        Testing the user account creation API
        """
        event_type = 'create_account'

        # Check not enough/correct args
        self.assertServerMissingParams(event_type, username='a', email='a@b.com', password_hash=random_64())

        # Check bad usernames, emails, and password hashes show error
        self.assertServerHandlesBadUEP(event_type, _all=True)

        # Doing email/usernames that have already been taken (including caps/no caps/periods in email)
        password_hash = hashlib.sha256(b'testpassword').hexdigest()
        self.assertServerError(event_type='create_account', error_code='ERROR_USERNAME_ALREADY_EXISTS',
                               username='wingit_testing_account_1',
                               email='idncvahneufn9ahf8eh2n8f9n0agdfcv79w3hf@gmail.com', password_hash=password_hash)
        self.assertServerError(event_type='create_account', error_code='ERROR_USERNAME_ALREADY_EXISTS',
                               username='WinGit_tesTing_ACcount_1',
                               email='idncvahneufn9ahf8eh2n8f9n0agdfcv79w3hf@gmail.com', password_hash=password_hash)
        self.assertServerError(event_type='create_account', error_code='ERROR_EMAIL_ALREADY_IN_USE',
                               username='hafuebsadkjbfioasbfduiasbdfioub',
                               email='wingit.testing.account.2@gmail.com', password_hash=password_hash)
        self.assertServerError(event_type='create_account', error_code='ERROR_EMAIL_ALREADY_IN_USE',
                               username='hafuebsadkjbfioasbfduiasbdfioub',
                               email='wingit.testingaccount.2@gmail.com', password_hash=password_hash)
        self.assertServerError(event_type='create_account', error_code='ERROR_EMAIL_ALREADY_IN_USE',
                               username='hafuebsadkjbfioasbfduiasbdfioub',
                               email='wi.ngit.te..s.ting.acco..unt.....2@gmail.com', password_hash=password_hash)

    def test_account_login(self):
        """
        Testing login to an existing user account
        """
        event_type = 'login'

        # Check not enough/correct args
        self.assertServerMissingParams(event_type, email='test@gmail.com', password_hash=random_64())

        # Check invalid username/email and password_hash
        #   (have to do username/email separately)
        self.assertServerHandlesBadUEP(event_type, email=True, password_hash=True)
        self.assertServerHandlesBadUEP(event_type, username=True, password_hash=True)

        # Check incorrect username/email, but a functional password
        password_hash = hashlib.sha256(b'testpassword2').hexdigest()
        self.assertServerError('ERROR_USERNAME_DOES_NOT_EXIST', event_type=event_type,
                               username="inawufnawpoeifhnqwin80123hr8n", password_hash=password_hash)
        self.assertServerError('ERROR_EMAIL_DOES_NOT_EXIST', event_type=event_type,
                               email="ijsadfhb798oeabfiuowaebfiuasehf@gmail.com", password_hash=password_hash)

        # Check correct username/email, but wrong password
        password_hash = hashlib.sha256(b'oiusdnfuiwae').hexdigest()
        self.assertServerError('ERROR_INCORRECT_PASSWORD', event_type=event_type,
                               username="wingit_testing_account_1", password_hash=password_hash)
        self.assertServerError('ERROR_INCORRECT_PASSWORD', event_type=event_type,
                               email="largestinfinity@gmail.com", password_hash=password_hash)

        # Check correct everything, but an unverified account
        password_hash = hashlib.sha256(b'testpassword2').hexdigest()
        self.assertServerError('ERROR_ACCOUNT_UNVERIFIED', event_type=event_type,
                               username="wingit_testing_account_2", password_hash=password_hash)
        self.assertServerError('ERROR_ACCOUNT_UNVERIFIED', event_type=event_type,
                               email="wingit.testing.account.2@gmail.com", password_hash=password_hash)

        # Check logging in with email and username both work
        password_hash = hashlib.sha256(b'testpassword').hexdigest()
        self.assertNoServerError(event_type=event_type, username="wingit_testing_account_1",
                                 password_hash=password_hash)
        self.assertNoServerError(event_type=event_type, email="largestinfinity@gmail.com",
                                 password_hash=password_hash)

    def test_misc(self):
        """
        Test miscellaneous things
        """
        # Check that there is an error if there is no event_type in params,
        #   even if all other params are sent for a function
        err = {'error_code': 'ERROR_NO_EVENT_TYPE'}
        self.assertServerError(test='True', **err)
        self.assertServerError(username='a', email='d@g.d', password_hash=random_64(), **err)

        # Error if an unknown event type is passed
        self.assertServerError(event_type="ijafn3980fn-1q0nf", error_code='ERROR_UNKNOWN_EVENT_TYPE')


# Initiate the testing class
if __name__ == '__main__':
    unittest.main()
