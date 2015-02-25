__author__ = 'vyakoviv, vhomchak, rmaksymiv'


import time
from bson.objectid import ObjectId
from pymongo import MongoClient


class MyMongoClient(object):

    def __init__(self, hostname, port):
        self._client = MongoClient(hostname, port)
        self._project_db_name = 'project_%s'
        self._cn_last_update = 'last_update'

    def get_project_db(self, project):
        name = self._project_db_name % project
        return self._client[name]

    def get_project_names(self):
        project_names = [dn.split('_', 1)[1] for dn in self._client.database_names()
                                             if dn.startswith('project_') and 'manual' not in dn]
        project_names.sort()
        return project_names

    def get_latest_sprint_name(self, project):
        project_db = self.get_project_db(project)
        last_updates = list(project_db[self._cn_last_update].find())
        if last_updates:
            last_updates.sort(key=lambda r: r['timestamp'])
            return last_updates[-1]['sprint_name']

    def get_m_projects(self):
        project_names = [dn.split('_', 2)[-1] for dn in self._client.database_names()
                                             if dn.startswith('project_manual_')]
        project_names.sort()
        return project_names


class AggregationDB(MyMongoClient):

    def __init__(self, hostname, port, project):
        super(AggregationDB, self).__init__(hostname, port)
        self._db = self.get_project_db(project)
        self._cn_tests = 'tests'
        self._cn_results = 'results_%s'

    def _normalize_name(self, result):
        for i, result_dict in enumerate(result):
            if '_id' in result_dict:
                result[i]['name'] = result[i].pop('_id')

        return result

    def upsert_test(self, component, suite, test_id, **test_attributes):
        self._db[self._cn_tests].update(
            {'test_id': test_id, 'suite': suite, 'component': component},
            {'$set': test_attributes}, upsert=True)

    def upsert_test_result(self, sprint, component, suite, test_id, **result_attributes):
        sprint_collection_name = self._cn_results % sprint
        query = {'test_id': test_id, 'suite': suite, 'component': component}
        self._db[sprint_collection_name].remove(query)
        self._db[sprint_collection_name].update(query,
            {'$set': result_attributes}, upsert=True)

        # Update "last_update".
        self._db[self._cn_last_update].update({'sprint_name': sprint},
                                              {'$set': {'timestamp': time.time()}}, upsert=True)

    def get_test_results(self, sprint, **query):
        sprint_collection_name = self._cn_results % sprint
        return list(self._db[sprint_collection_name].find(query))

    def get_sprint_names(self):
        return [cn.split('_', 1)[1] for cn in self._db.collection_names() if cn.startswith('results_')]

    def get_component_names(self, sprint):
        sprint_collection_name = self._cn_results % sprint
        return self._db[sprint_collection_name].distinct('component')

    def remove_suite(self, sprint, component, suite):
        sprint_collection_name = self._cn_results % sprint
        self._db[sprint_collection_name].remove({'component': component, 'suite': suite})

    def remove_component(self, sprint, component):
        sprint_collection_name = self._cn_results % sprint
        self._db[sprint_collection_name].remove({'component': component})

    def remove_results(self, name):
        results_collection_name = self._cn_results % name
        self._db.drop_collection(results_collection_name)
        self._db[self._cn_last_update].remove({'sprint_name': name})

    def rename_results(self, name, new_name):
        results_collection_name = self._cn_results % name
        new_results_collection_name = self._cn_results % new_name
        self._db[results_collection_name].rename(new_results_collection_name)
        self._db[self._cn_last_update].update({'sprint_name': name},
                                              {'$set': {'sprint_name': new_name}},
                                              upsert=False)

    # Manual Tests Methods

    def get_manual_tests(self, component):
        db_result = self._db[self._cn_tests].aggregate([
            {
                '$match': {'component': component}
            },
            {'$sort': {'_id': 1}},
            {

                '$group': {
                    '_id': "$suite",
                    'rows': {'$push': {'test_id': "$test_id",
                                       'steps': "$steps",
                                       'title': "$title",
                                       'component': '$component',
                                       'suite': '$component',
                                       'expected_results': '$expected_results'}
                             },
                    'total': {'$sum': 1}
                }
            },
            {'$sort': {'_id': 1}}

        ])
        result = db_result['result']
        if not result:
            return False
        result = self._normalize_name(result)

        return result

    def get_manual_component_names(self):
        res = self._db[self._cn_tests].aggregate([
            {
                '$group': {'_id': "$component",
                           'total': {'$sum': 1}}
            },
            {'$sort': {'_id': 1}}
        ])
        return [{'name': row['_id'], 'total': row['total']}
                for row in res['result']]

    def get_new_test_id(self):
        res = self._db[self._cn_tests].find_one(sort=[('_id', -1)])
        if not res:
            test_id = self._db.name.split('_')[-1].upper() + '-1'
        else:
            test_id = res['test_id']
            test_id = '-'.join([test_id.split('-')[0], str(int(test_id.split('-')[1]) + 1)])
        return test_id

    def get_manual_sprints(self):
        return [cn.split('_', 1)[1] for cn in self._db.collection_names() if cn.startswith('results_')]

    def get_sprint_totals(self, sprint_name):
        sprint_collection_name = self._cn_results % sprint_name
        res = self._db[sprint_collection_name].aggregate([
            {
                '$group': {'_id': "id",
                           'passed': {'$sum': {'$cond': [{'$eq': ['$result', 'passed']}, 1, 0]}},
                           'failed': {'$sum': {'$cond': [{'$eq': ['$result', 'failed']}, 1, 0]}},
                           'total': {'$sum': {"$cond": [{"$ne": ["$result", 'null']}, 1, 0]}}}

            }
        ])

        if res['result']:
            return res['result'][0]
        else:
            return

    def get_sprint_details(self, sprint_name):
        sprint_collection_name = self._cn_results % sprint_name
        db_result = self._db[sprint_collection_name].aggregate([
            {
                '$group': {'_id': "$component",
                           'passed': {'$sum': {'$cond': [{'$eq': ['$result', 'passed']}, 1, 0]}},
                           'failed': {'$sum': {'$cond': [{'$eq': ['$result', 'failed']}, 1, 0]}},
                           'total': {'$sum': {"$cond": [{"$ne": ["$result", 'null']}, 1, 0]}}}
            }
        ])
        result = db_result['result']
        if not result:
            return False
        result = self._normalize_name(result)

        return result

    def get_sprint_failed(self, sprint_name):
        sprint_collection_name = self._cn_results % sprint_name
        db_result = self._db[sprint_collection_name].find(
            {'result': 'failed'},
            {'test_id': 1, 'steps': 1, 'title': 1, 'component': 1,
             'suite': 1, 'expected_results': 1, 'result': 1, 'attributes': 1, 'error': 1})

        return list(db_result)

    def get_tests_result(self, sprint_name, component):
        sprint_collection_name = self._cn_results % sprint_name
        db_result = self._db[sprint_collection_name].aggregate([
            {
                '$match': {'component': component}
            },
            {'$sort': {'_id': 1}},
            {

                '$group': {
                    '_id': "$suite",
                    'rows': {'$push': {'test_id': "$test_id",
                                       'steps': "$steps",
                                       'title': "$title",
                                       'component': '$component',
                                       'suite': '$component',
                                       'expected_results': '$expected_results',
                                       'result': '$result',
                                       'error': '$error'}
                             },
                    'total': {'$sum': 1},
                    'passed': {'$sum': {'$cond': [{'$eq': ['$result', 'passed']}, 1, 0]}},
                    'failed': {'$sum': {'$cond': [{'$eq': ['$result', 'failed']}, 1, 0]}},
                }
            },
            {'$sort': {'_id': 1}}

        ])
        result = db_result['result']
        if not result:
            return False
        result = self._normalize_name(result)

        return result

    def get_manual_sprint_component(self, sprint_name):
        sprint_collection_name = self._cn_results % sprint_name
        res = self._db[sprint_collection_name].aggregate([
            {
                '$group': {'_id': "$component",
                           'total': {'$sum': 1}}
            },
            {'$sort': {'_id': 1}}
        ])
        return [{'name': row['_id'], 'total': row['total']}
                for row in res['result']]

    def create_sprint(self, sprint_name):
        sprint_collection_name = self._cn_results % sprint_name
        self._db.eval('db.tests.copyTo("{0}")'.format(sprint_collection_name))
        self._db[sprint_name].update({}, {'$set': {"result": ''}},
                                     upsert=False, multi=False)
        return

    def sync_sprint(self, sprint_name):
        sprint_collection_name = self._cn_results % sprint_name
        new_tc = self._db[self._cn_tests].find()
        for tc in new_tc:
            tc_id = tc.pop('_id')
            print tc_id, tc
            self._db[sprint_collection_name].update({'_id': tc_id},
                                                    {'$set': tc},
                                                    upsert=True, multi=False)
        return

    def remove_manual_test(self, component, suite, test_id):
        self._db[self._cn_tests].remove({'component': component, 'suite': suite, 'test_id': test_id})

    def remove_manual_suite(self, component, suite):
        self._db[self._cn_tests].remove({'component': component, 'suite': suite})

    def remove_manual_component(self, component):
        self._db[self._cn_tests].remove({'component': component})

    def remove_manual_results_suite(self, component, suite, sprint_name):
        sprint_collection_name = self._cn_results % sprint_name
        self._db[sprint_collection_name].remove({'component': component, 'suite': suite})

    def remove_manual_results_component(self, component, sprint_name):
        sprint_collection_name = self._cn_results % sprint_name
        self._db[sprint_collection_name].remove({'component': component})

    def remove_manual_results(self, sprint_name):
        sprint_collection_name = self._cn_results % sprint_name
        self._db.drop_collection(sprint_collection_name)

    def remove_manual_results_test(self, component, suite, test_id, sprint_name):
        sprint_collection_name = self._cn_results % sprint_name
        self._db[sprint_collection_name].remove({'component': component, 'suite': suite, 'test_id': test_id})

    def set_manual_result(self, sprint, component, suite, test_id, result, error=None, **result_attributes):
        assert result in ['passed', 'failed']
        sprint_collection_name = self._cn_results % sprint
        if result_attributes:
            result_attributes = {"attributes": map(list, result_attributes.items())}
        query = {'test_id': test_id, 'suite': suite, 'component': component}
        result_dict = {'result': result}
        if not result_attributes:
            result_attributes['attributes'] = []
        if not error:
            error = ""
        result_dict.update({'error': error})
        result_dict.update({"attributes": result_attributes['attributes']})

        self._db[sprint_collection_name].update(query,
                                                {'$set': result_dict}, upsert=True)

    def edit_manual_test(self, test_id, title, steps, expected_results):
        self._db[self._cn_tests].update(
            {'test_id': test_id},
            {'$set': {'title': title, 'steps': steps, 'expected_results': expected_results}})

    def fetch_manual_test(self, component, test_id):
        test = list(self._db[self._cn_tests].find({'test_id': test_id, 'component': component}, {'_id': 0}))
        if not test:
            test = {}
        else:
            test = test[0]
        return test

    def rename_manual_suite(self, component, suite, suite_new):
        self._db[self._cn_tests].update({'component': component, 'suite': suite},
            {'$set': {'suite': suite_new}}, upsert=False, multi=True)

    def rename_manual_component(self, component, component_new):
        self._db[self._cn_tests].update({'component': component},
            {'$set': {'component': component_new}}, upsert=False, multi=True)

if __name__ == '__main__':

    project = 'proj'
    sprint = 'v.1'
    db = AggregationDB(hostname='localhost', port=27017, project=project)

    # import pdb; pdb.set_trace()
    print db.get_sprint_names()

    print db.get_test_results(sprint)

    component = 'Abc'
    suite = 'AddMessage'

    error = \
"""
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
Exception: a
"""

    for num in xrange(17, 20):

        db.upsert_test_result(attributes=[('is_test_for', 'FOOBAR-1'), ('type', 'Functional')],
                              comment='foo-1,23',
                              sprint=sprint,
                              component=component,
                              suite=suite,
                              test_id='BAM-%s' % num,
                              title='Test %s if there is foo bar no more foo bbar no more...' % num,
                              description='Description more...\nfdfdfdf\n gfggfg',
                              result='failed')

    # import pdb; pdb.set_trace()

    print db.get_test_results(sprint)

# EOF
