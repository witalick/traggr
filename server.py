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
    projects = db.get_project_names()
    latest_sprints = dict((project, db.get_latest_sprint_name(project)) for project in projects)
    return render_template('base.html', projects=projects, latest_sprints=latest_sprints)


@server.route('/<project>/<sprint>')
def results(project, sprint):

    db = get_db(project)

    projects = db.get_project_names()
    if project not in projects:
        return 'I don\'t have results for this project... Sorry... :/', 404
    projects.remove(project)

    sprints = db.get_sprint_names()
    if sprint not in sprints:
        return 'I don\'t have results for this sprint... Sorry... :/', 404
    sprints.remove(sprint)

    test_results = db.get_test_results(sprint)
    components = set([r['component'] for r in test_results])

    components_data = []
    for component in components:
        component_data = {'name': component}

        tests = [r for r in test_results if r['component'] == component]

        component_data['total'] = len(tests)
        component_data['passed'] = len([t for t in tests if t['result'] == 'passed'])
        component_data['failed'] = len([t for t in tests if t['result'] != 'passed'])
        components_data.append(component_data)

    totals = dict()
    totals['total'] = len(test_results)
    totals['passed'] = len([t for t in test_results if t['result'] == 'passed'])
    totals['failed'] = len([t for t in test_results if t['result'] != 'passed'])

    return render_template('results.html',
                           components=components_data,
                           totals=totals,
                           project=project,
                           projects=projects,
                           sprint=sprint,
                           sprints=sprints)


@server.route('/<project>/<sprint>/<component>')
def results_suites(project, sprint, component):

    db = get_db(project)
    test_results = db.get_test_results(sprint, component=component)
    suite_names = set([s['suite'] for s in test_results])

    projects = db.get_project_names()
    if project not in projects:
        return 'I don\'t have results for this project... Sorry... :/', 404
    projects.remove(project)

    sprints = db.get_sprint_names()
    if sprint not in sprints:
        return 'I don\'t have results for this sprint... Sorry... :/', 404
    sprints.remove(sprint)

    components = db.get_component_names(sprint)
    if component not in components:
        return 'I don\'t have results for this component... Sorry... :/', 404
    components.remove(component)

    data = []
    for suite_name in suite_names:

        suite_data = dict()
        suite_data['name'] = suite_name
        tests = [r for r in test_results if r['suite'] == suite_name]
        tests.sort(key=lambda x: x['result'])
        suite_data['rows'] = tests
        suite_data['total'] = len(tests)
        suite_data['passed'] = len([t for t in tests if t['result'] == 'passed'])
        suite_data['failed'] = len([t for t in tests if t['result'] != 'passed'])
        suite_data['has_errors'] = any('error' in test for test in tests)
        suite_data['has_comments'] = any('comment' in test for test in tests)
        suite_data['has_attributes'] = any('attributes' in test for test in tests)

        data.append(suite_data)

    return render_template('results_suites.html',
                           data=data,
                           project=project,
                           projects=projects,
                           sprint=sprint,
                           sprints=sprints,
                           component=component,
                           components=components)


@server.route('/<project>')
def project_sprints(project):

    db = get_db(project)
    projects = db.get_project_names()
    sprints = db.get_sprint_names()

    if project not in projects:
        return 'I don\'t have results for this project... Sorry... :/', 404
    projects.remove(project)

    return render_template('project_sprints.html',
                           project=project,
                           projects=projects,
                           sprints=sprints)


if __name__ == '__main__':

    server.run(host='0.0.0.0', port=5000, debug=True)


# EOF
