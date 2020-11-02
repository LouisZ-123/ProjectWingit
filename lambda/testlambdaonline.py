"""
Run the same tests we have in buildlambda.py, but does them for the online lambda API
"""
from tests.TestLambda import TestLambda
from tests.LambdaTestUtils import set_request_type_online

if __name__ == "__main__":
    print("Running online tests...")
    set_request_type_online(True)
    TestLambda().test_all()
