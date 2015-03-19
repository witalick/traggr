__author__ = 'vyakoviv'

import json
import threading
import re

from flask import Flask, request, make_response

from db import AggregationDB
from config import config


api = Flask(__name__)
api.config.update(config)

proj_patt = re.compile(r"[A-Za-z0-9_\-\s]+[A-Za-z0-9]$")
suite_patt = re.compile(r"[A-Za-z0-9_\-\s]+")
sub_spaces_patt = re.compile(r'\s{2,}')

def get_db(project):
    return AggregationDB(hostname=api.config['db_hostname'],
                         port=api.config['db_port'],
                         project=project)


def get_manual_db(project):
    return AggregationDB(hostname=api.config['db_hostname'],
                         port=api.config['db_port'],
                         project='manual_' + project)


def validate_manual_test(test_data):
    invalid_data = False
    if suite_patt.match(test_data['component']):
        test_data['component'] = sub_spaces_patt.sub(' ', test_data['component']).strip()
    else:
        invalid_data = True
    if suite_patt.match(test_data['suite']):
        test_data['suite'] = sub_spaces_patt.sub(' ', test_data['suite']).strip()
    else:
        invalid_data = True

    if not invalid_data:
        return test_data


@api.route('/ping')
def ping():
    return make_response('pong', 200)


@api.route('/results/<project>/<sprint>', methods=['POST'])
def add_results(project, sprint):
    db = get_db(project)
    results = json.loads(request.get_data())
    for result in results:
        db.upsert_test(component=result['component'],
                       suite=result['suite'],
                       test_id=result['test_id'],
                       **result['other_attributes'])

        db.upsert_test_result(sprint=sprint,
                              component=result['component'],
                              suite=result['suite'],
                              test_id=result['test_id'],
                              **dict(result['result_attributes'].items() +
                                     result['other_attributes'].items()))
    return make_response('', 200)


@api.route('/manual/<project>', methods=['POST'])
def add_manual_tests(project):
    if proj_patt.match(project):
        project = sub_spaces_patt.sub(' ', project).strip().replace(' ', '_')
        db = get_manual_db(project)
        tests = json.loads(request.get_data())
        for test in tests:
            test = validate_manual_test(test)
            if test:
                lock = threading.Lock()
                with lock:
                    db.create_manual_test_case(component=test['component'],
                                               suite=test['suite'],
                                               **test['other_attributes'])
        return make_response('Ok', 200)
    else:
        return make_response('Invalid Project name.'
                             ' Only ASCI Char, Number, Space, `_` or `-`.Also should end with ASCI Char or Number',
                             400)


@api.route('/manual/results/<project>/<sprint>', methods=['POST'])
def add_manual_results(project, sprint):
    if proj_patt.match(project) and proj_patt.match(sprint):
        project = sub_spaces_patt.sub(' ', project).strip().replace(' ', '_')
        sprint = sub_spaces_patt.sub(' ', sprint).strip().replace(' ', '_')
        db = get_manual_db(project)
        results = json.loads(request.get_data())

        if not all('result_attributes'in result for result in results) or\
                not all('result'in result['result_attributes'] for result in results):
            return make_response('`result` key has to be set in `result_attributes`', 400)

        for result in results:
            result = validate_manual_test(result)
            if result:
                db.upsert_test_result(sprint=sprint,
                                      component=result['component'],
                                      suite=result['suite'],
                                      test_id=result['test_id'],
                                      **dict(result['result_attributes'].items() +
                                             result['other_attributes'].items()))
        return make_response('Ok', 200)
    else:
        return make_response('Invalid Project or Sprint name.'
                             ' Only ASCI Char, Number, Space, `_` or `-`.Also should end with ASCI Char or Number',
                             400)

if __name__ == '__main__':

    api.run(host='0.0.0.0', port=5001, debug=True)


# EOF
