__author__ = 'vyakoviv'

import json

from flask import Flask, render_template

from db import AggregationDB, MyMongoClient
from config import config


server = Flask(__name__)
server.config.update(config)


def get_db(project=None):

    if project:
        return AggregationDB(hostname=server.config['db_hostname'],
                             port=server.config['db_port'],
                             project=project)
    return MyMongoClient(hostname=server.config['db_hostname'],
                         port=server.config['db_port'])


@server.route('/')
def root():

    db = get_db()
    projects = db.get_projects()
    return render_template('base.html', projects=projects)


@server.route('/r/<project>/<sprint>')
def results(project, sprint):

    db = get_db(project)
    results = db.get_test_results(sprint)
    components = set([r['component'] for r in results])

    data = []
    for component in components:
        component_data = {'project': project, 'sprint': sprint, 'name': component}

        tests = [r for r in results if r['component'] == component]

        component_data['total'] = len(tests)
        component_data['passed'] = len([t for t in tests if t['result'] == 'passed'])
        component_data['failed'] = len([t for t in tests if t['result'] != 'passed'])
        data.append(component_data)

    totals = {}
    totals['total'] = len(results)
    totals['passed'] = len([t for t in results if t['result'] == 'passed'])
    totals['failed'] = len([t for t in results if t['result'] != 'passed'])

    return render_template('results.html', data=data, totals=totals)


@server.route('/rs/<project>/<sprint>/<component>')
def results_suites(project, sprint, component):

    db = get_db(project)
    results = db.get_test_results(sprint, component=component)
    suite_names = set([s['suite'] for s in results])

    data = []
    for suite_name in suite_names:

        suite_data = {}
        suite_data['name'] = suite_name
        tests = [r for r in results if r['suite'] == suite_name]
        tests.sort(key=lambda x: x['result'])
        suite_data['rows'] = tests
        suite_data['total'] = len(tests)
        suite_data['passed'] = len([t for t in tests if t['result'] == 'passed'])
        suite_data['failed'] = len([t for t in tests if t['result'] != 'passed'])
        data.append(suite_data)

    return render_template('results_suites.html', data=data)


@server.route('/sprints/<project>')
def sprints(project):

    db = get_db(project)
    sprints_list = db.get_sprint_names()
    return json.dumps([{'name': sprint} for sprint in sprints_list])


if __name__ == '__main__':

    server.run(debug=True)


# EOF
