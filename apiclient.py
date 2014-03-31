__author__ = 'vyakoviv'

import json
import requests


url = 'http://localhost:5000/results/proj/2014_04'

results = [{'component': 'API', 'suite': 'Functions', 'test_id': 'A-1',
            'other_attributes': {'title': 'Test for Login', 'description': 'F o o B a r', 'types': ['Functional']},
            'result_attributes': {'result': 'passed', 'date': 'oo'}}]

response = requests.post(url, data=json.dumps(results), headers={'Content-Type': 'text/json'})

print response
print response.text
