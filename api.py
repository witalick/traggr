__author__ = 'vyakoviv'

import json

from flask import Flask, request, make_response

from db import AggregationDB
from config import config


api = Flask(__name__)
api.config.update(config)


def get_db(project):

    return AggregationDB(hostname=api.config['db_hostname'],
                         port=api.config['db_port'],
                         project=project)


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
                              **result['result_attributes'])

    return make_response('', 200)


if __name__ == '__main__':

    api.run(debug=True)


# EOF