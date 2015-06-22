__author__ = 'vyakoviv, vhomchak, rmaksymiv'


import re
import json
import threading

from flask import Flask, render_template, request, jsonify

from db import AggregationDB, MyMongoClient
from config import config
from model import TestResult, regroup_results, compare_sprints, common_results


server = Flask(__name__)
server.config.update(config)


def get_db(project=None):

    if project:
        return AggregationDB(hostname=server.config['db_hostname'],
                             port=server.config['db_port'],
                             project=project)
    return MyMongoClient(hostname=server.config['db_hostname'],
                         port=server.config['db_port'])


def get_manual_db(project=None):
    if project:
        return AggregationDB(hostname=server.config['db_hostname'],
                             port=server.config['db_port'],
                             project='manual_' + project)
    return MyMongoClient(hostname=server.config['db_hostname'],
                         port=server.config['db_port'])

def group_results(tests):
    result = {}
    grouped = regroup_results(tests, 'component', 'suite')
    for keytuple, resultset in grouped:
        if result.get(keytuple[0]) is None:
            result[keytuple[0]] = {}
        result[keytuple[0]][keytuple[1]] = list(resultset)
    return result

@server.route('/')
def root():
    db = get_db()
    projects = db.get_project_names()
    latest_sprints = dict((project, db.get_latest_sprint_name(project)) for project in projects)
    return render_template('base.html', projects=projects, latest_sprints=latest_sprints)


@server.route('/compare/<project>/<sprint>')
def compare_sprints_action(project, sprint):
    db = get_db(project)

    projects = db.get_project_names()
    if project not in projects:
        return 'I don\'t have results for this project... Sorry... :/', 404

    sprints = db.get_sprint_names()
    if sprint not in sprints:
        return 'I don\'t have results for this sprint... Sorry... :/', 404
    sprints.remove(sprint)

    mysprints = request.args.getlist('sprint')
    common = common_results(db, sprint,
                            *mysprints, result={ '$in': ('failed', 'error') })
    grouped_common_results = group_results(common)
    common_size = len(common)
    comparison = compare_sprints(db, sprint, *mysprints, result={ '$in': ('failed', 'error') })
    comparison_length = sum([len(x) for x in comparison.itervalues()])
    comparison_sizes = {}
    for s in comparison.iterkeys():
        comparison_sizes[s] = len(comparison[s])
        comparison[s] = group_results(comparison[s])

    return render_template(
        'compare.html',
        project=project,
        projects=projects,
        sprints=sprints,
        sprint=sprint,
        compared_sprints=mysprints,
        comparison_length=comparison_length,
        comparison_sizes=comparison_sizes,
        common_results=common_size,
        grouped_common_results=grouped_common_results,
        comparison=comparison
    )

@server.route('/side-by-side/<project>/<sprint>')
def sidebyside_sprints_action(project, sprint):
    db = get_db(project)

    projects = db.get_project_names()
    if project not in projects:
        return 'I don\'t have results for this project... Sorry... :/', 404

    sprints = db.get_sprint_names()
    if sprint not in sprints:
        return 'I don\'t have results for this sprint... Sorry... :/', 404
    sprints.remove(sprint)

    mysprints = request.args.getlist('sprint')
    mysprints.append(sprint)
    common = common_results(db, *mysprints, result={'$in': ('failed', 'error')})
    common_size = len(common)
    comparison = compare_sprints(db, *mysprints, result={'$in': ('failed', 'error') })
    comparison_length = sum([len(x) for x in comparison.itervalues()])
    comparison_sizes = {}
    suites = set()
    for s in comparison.iterkeys():
        comparison_sizes[s] = len(comparison[s])
        grouped = regroup_results(comparison[s], 'suite')
        groupedres = {}
        for k, v in grouped:
            groupedres[k[0]] = list(v)
            suites.add(k[0])
        comparison[s] = groupedres

    return render_template(
        'sidebyside.html',
        project=project,
        projects=projects,
        sprints=sprints,
        sprint=sprint,
        suites=list(suites),
        compared_sprints=mysprints,
        comparison_length=comparison_length,
        comparison_sizes=comparison_sizes,
        common_results=common_size,
        comparison=comparison
    )

@server.route('/<project>/<sprint>')
def results(project, sprint):

    db = get_db(project)

    projects = db.get_project_names()
    if project not in projects:
        return 'I don\'t have results for this project... Sorry... :/', 404

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

    # Failed tests.
    failed_tests = [TestResult(**tr) for tr in test_results if tr['result'] != 'passed']

    grouped_failed_tests = group_results(failed_tests)

    return render_template('results.html',
                           components=components_data,
                           totals=totals,
                           project=project,
                           projects=projects,
                           sprint=sprint,
                           sprints=sprints,
                           failed_tests=grouped_failed_tests)


@server.route('/<project>/<sprint>/<component>')
def results_suites(project, sprint, component):

    db = get_db(project)
    test_results = db.get_test_results(sprint, component=component)
    suite_names = set([s['suite'] for s in test_results])

    projects = db.get_project_names()
    if project not in projects:
        return 'I don\'t have results for this project... Sorry... :/', 404

    sprints = db.get_sprint_names()
    if sprint not in sprints:
        return 'I don\'t have results for this sprint... Sorry... :/', 404

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

    data.sort(key=lambda e: e['name'])

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
    if 'favicon' in project:
        return '', 200
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


@server.route('/_delete_suite/<project>/<sprint>/<component>/<suite>', methods=['DELETE'])
def delete_suite(project, sprint, component, suite):

    db = get_db(project)
    db.remove_suite(sprint, component, suite)

    return '', 200


@server.route('/_delete_component/<project>/<sprint>/<component>', methods=['DELETE'])
def delete_component(project, sprint, component):

    db = get_db(project)
    db.remove_component(sprint, component)

    return '', 200


@server.route('/_delete_results/<project>/<sprint>', methods=['DELETE'])
def delete_results(project, sprint):

    db = get_db(project)
    db.remove_results(sprint)

    return '', 200


@server.route('/_rename_results/<project>/<results>/<new_results>', methods=['PUT'])
def rename_results(project, results, new_results):

    db = get_db(project)
    db.rename_results(results, new_results)

    return '', 200


@server.route('/_get_sprint_totals/<project>/<sprint>', methods=['GET'])
def get_sprint_totals(project, sprint):

    db = get_db(project)
    test_results = db.get_test_results(sprint)
    totals = dict()
    totals['total'] = len(test_results)
    totals['passed'] = len([t for t in test_results if t['result'] == 'passed'])
    totals['failed'] = len([t for t in test_results if t['result'] != 'passed'])

    return json.dumps(totals), 200


@server.route('/_get_results_names/<project>', methods=['GET'])
def get_results_names(project):

    db = get_db(project)
    results_names = db.get_sprint_names()

    return json.dumps(results_names), 200

# Manual Tests Related Methods


@server.route('/manual', methods=['POST', 'GET'])
def manual_base():
    db = get_manual_db()
    m_projects = db.get_m_projects()

    if request.method == 'GET':
        return render_template('manual_projects.html', projects=m_projects)
    elif request.method == 'POST':
        project_data = json.loads(request.get_data())
        db = get_manual_db(project_data['project_name'])
        db.get_manual_component_names()
        return jsonify({})


@server.route('/manual/<m_project>', methods=['POST', 'GET', 'DELETE'])
def manual_components(m_project):
    db = get_manual_db(m_project)
    m_projects = db.get_m_projects()
    components = db.get_manual_component_names()
    m_sprints = db.get_manual_sprints()
    if request.method == 'GET':
        return render_template('manual_components.html',
                               projects=m_projects,
                               project=m_project,
                               sprints=m_sprints,
                               components=components)

    elif request.method == 'POST':
        test_data = json.loads(request.get_data())
        lock = threading.Lock()
        with lock:
            test_id = db.create_manual_test_case(component=test_data['component'],
                                                 suite=test_data['suite'],
                                                 **test_data['other_attributes'])
        return jsonify({'test_id': test_id})

    elif request.method == 'DELETE':
        test_data = json.loads(request.get_data())
        db.remove_manual_component(component=test_data['component'])
        return jsonify({})


@server.route('/manual/<m_project>/<m_component>', methods=['POST', 'GET', 'DELETE'])
def manual_tests_suites(m_project, m_component):
    db = get_manual_db(m_project)
    projects = db.get_m_projects()
    m_components = db.get_manual_component_names()
    tests = db.get_manual_tests(component=m_component)
    if not tests:
        return 'I don\'t have tests for this component... Sorry... :/', 404

    if request.method == 'GET':
        return render_template('manual_test_suites.html',
                               data=tests,
                               project=m_project,
                               projects=projects,
                               component=m_component,
                               components=m_components)

    elif request.method == 'DELETE':
        test_data = json.loads(request.get_data())
        if 'test_id' in test_data:
            db.remove_manual_test(component=m_component,
                                  suite=test_data['suite'],
                                  test_id=test_data['test_id'])
        else:
            db.remove_manual_suite(component=m_component,
                                   suite=test_data['suite'])
        return jsonify({})

    elif request.method == 'POST':
        suite_data = json.loads(request.get_data())
        db.rename_manual_suite(component=m_component,
                               suite=suite_data['suite'],
                               suite_new=suite_data['suite_new'])
        return jsonify({})


@server.route('/manual/<m_project>/sprint', methods=['POST', 'GET', 'DELETE'])
def manual_sprints(m_project):
    db = get_manual_db(m_project)
    projects = db.get_m_projects()
    sprints = db.get_manual_sprints()
    totals = [db.get_sprint_totals(sprint_name=m_sprint) for m_sprint in sprints]
    data = dict()
    for i, v in zip(sprints, totals):
        data[i] = v

    if request.method == 'GET':
        return render_template('manual_sprints.html',
                               project=m_project,
                               projects=projects,
                               sprints=data)

    if request.method == 'POST':
        data = json.loads(request.get_data())
        db.create_sprint(data['sprint_name'])
        return jsonify({})

    if request.method == 'DELETE':
        data = json.loads(request.get_data())
        db.remove_manual_results(data['sprint_name'])
        return jsonify({})


@server.route('/manual/<m_project>/sprint/<m_sprint>', methods=['POST', 'GET', 'DELETE'])
def manual_sprint_components(m_project, m_sprint):
    db = get_manual_db(m_project)
    projects = db.get_m_projects()
    sprints = db.get_manual_sprints()
    sprints.remove(m_sprint)
    totals = db.get_sprint_totals(sprint_name=m_sprint)
    components_data = db.get_sprint_details(sprint_name=m_sprint)
    failed_tests = db.get_sprint_failed(sprint_name=m_sprint)
    # db.sync_sprint(m_sprint)
    if request.method == 'GET':
        return render_template('manual_sprint_components.html',
                               project=m_project,
                               projects=projects,
                               sprints=sprints,
                               sprint=m_sprint,
                               components=components_data,
                               totals=totals,
                               failed_tests=failed_tests)

    if request.method == 'DELETE':
        results_data = json.loads(request.get_data())
        db.remove_manual_results_component(component=results_data['component'],
                                           sprint_name=m_sprint)
        return jsonify({})


@server.route('/manual/<m_project>/sprint/<m_sprint>/<m_component>', methods=['POST', 'GET', 'DELETE'])
def manual_sprint_suites(m_project, m_sprint, m_component):
    db = get_manual_db(m_project)
    projects = db.get_m_projects()
    sprints = db.get_manual_sprints()
    m_components = db.get_manual_sprint_component(sprint_name=m_sprint)
    tests_results = db.get_tests_result(sprint_name=m_sprint, component=m_component)
    for ts in tests_results:
        ts['has_attributes'] = any(row['attributes'] for row in ts["rows"] if 'attributes' in row)
    if request.method == 'GET':
        return render_template('manual_sprint_suites.html',
                               project=m_project,
                               projects=projects,
                               sprints=sprints,
                               sprint=m_sprint,
                               components=m_components,
                               component=m_component,
                               data=tests_results)

    if request.method == 'DELETE':
        results_data = json.loads(request.get_data())
        if 'test_id' in results_data:
            db.remove_manual_results_test(suite=results_data['suite'],
                                          component=m_component,
                                          sprint_name=m_sprint,
                                          test_id=results_data['test_id'])
        else:
            db.remove_manual_results_suite(suite=results_data['suite'],
                                           component=m_component,
                                           sprint_name=m_sprint)
        return jsonify({})


@server.route('/manual/_edit_manual_test/<m_project>', methods=['POST'])
def manual_edit_test(m_project):
    db = get_manual_db(m_project)
    if request.method == 'POST':
        test_data = json.loads(request.get_data())
        db.edit_manual_test(test_id=test_data['test_id'],
                            title=test_data['other_attributes']['title'],
                            steps=test_data['other_attributes']['steps'],
                            expected_results=test_data['other_attributes']['expected_results'])
        return jsonify({})


@server.route('/manual/_get_manual_test/<m_project>', methods=['POST'])
def manual_get_test(m_project):
    db = get_manual_db(m_project)
    if request.method == 'POST':
        test_data = json.loads(request.get_data())
        return jsonify(db.fetch_manual_test(component=test_data['component'],
                             test_id=test_data['test_id']))


@server.route('/manual/_get_manual_result/<m_project>', methods=['POST'])
def manual_get_result(m_project):
    db = get_manual_db(m_project)
    if request.method == 'POST':
        test_data = json.loads(request.get_data())
        return jsonify(db.fetch_manual_result(component=test_data['component'],
                                              test_id=test_data['test_id'],
                                              sprint=test_data['sprint']))


@server.route('/manual/_edit_manual_test_result/<m_project>', methods=['POST'])
def manual_set_test_result(m_project):
    db = get_manual_db(m_project)
    if request.method == 'POST':
        test_data = json.loads(request.get_data())
        if 'result_attributes' in test_data:
            result_attributes = test_data['result_attributes']
        else:
            result_attributes = {}
        if 'error' in test_data:
            error = test_data['error']
        else:
            error = None
        db.set_manual_result(sprint=test_data['sprint'],
                             component=test_data['component'],
                             suite=test_data['suite'],
                             test_id=test_data['test_id'],
                             result=test_data['result'],
                             error=error,
                             **result_attributes)
        return jsonify({})


@server.route('/manual/_sync_sprint/<m_project>/<m_sprint>', methods=['POST'])
def manual_sync_sprint_data(m_project, m_sprint):
    db = get_manual_db(m_project)
    if request.method == 'POST':
        db.sync_sprint(m_sprint)
        return '', 200


@server.route('/manual/_edit_manual_component/<m_project>', methods=['POST'])
def manual_edit_component_name(m_project):
    db = get_manual_db(m_project)
    if request.method == 'POST':
        suite_data = json.loads(request.get_data())
        db.rename_manual_component(component=suite_data['component'],
                               component_new=suite_data['component_new'])
        return jsonify({})


@server.route('/manual/_edit_manual_sprint/<m_project>', methods=['POST'])
def manual_edit_sprint_name(m_project):
    db = get_manual_db(m_project)
    if request.method == 'POST':
        sprint_data = json.loads(request.get_data())
        db.rename_manual_sprint(sprint_name=sprint_data['sprint'],
                                sprint_name_new=sprint_data['sprint_new'])
        return jsonify({})

if __name__ == '__main__':

    server.run(host='0.0.0.0', port=5000, debug=True)


# EOF
