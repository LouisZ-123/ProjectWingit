import requests
from lambda_code.constants import *

print(requests.post(API_URL, data=json.dumps({'username': 'john', 'password': 'ashfuiashn'})).json())
