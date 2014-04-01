__author__ = 'vyakoviv'


from pymongo import MongoClient


class MyMongoClient(object):

    def __init__(self, hostname, port):
        self._client = MongoClient(hostname, port)

    def get_projects(self):
        return [dn.split('_', 1)[1] for dn in self._client.database_names() if dn.startswith('project_')]


class AggregationDB(MyMongoClient):

    def __init__(self, hostname, port, project):

        super(AggregationDB, self).__init__(hostname, port)

        self._db_name = 'project_%s' % project
        self._db = self._client[self._db_name]
        self._collection_name_tests = 'tests'
        self._collection_name_results = 'results_%s'

    def upsert_test(self, component, suite, test_id, **test_attributes):
        self._db[self._collection_name_tests].update(
            {'test_id': test_id, 'suite': suite, 'component': component},
            {'$set': test_attributes}, upsert=True)

    def upsert_test_result(self, sprint, component, suite, test_id, **result_attributes):
        sprint_collection_name = self._collection_name_results % sprint
        query = {'test_id': test_id, 'suite': suite, 'component': component}
        self._db[sprint_collection_name].remove(query)
        self._db[sprint_collection_name].update(query,
            {'$set': result_attributes}, upsert=True)

    def get_test_results(self, sprint, **query):
        sprint_collection_name = self._collection_name_results % sprint
        return list(self._db[sprint_collection_name].find(query))

    def get_sprint_names(self):
        return [cn.split('_', 1)[1] for cn in self._db.collection_names() if cn.startswith('results_')]


if __name__ == '__main__':

    project = 'proj'
    sprint = '2014_03'
    db = AggregationDB(hostname='localhost', port=27017, project=project)

    import pdb; pdb.set_trace()
    print db.get_sprint_names()

    print db.get_test_results(sprint)

    component = 'Abc'
    suite = 'AddMessage'

    for num in xrange(17, 20):

        db.upsert_test_result(sprint=sprint,
                              component=component,
                              suite=suite,
                              test_id='BAM-%s' % num,
                              title='Test %s if there is foo bar no more foo bbar no more...' % num,
                              description='Description more...\nfdfdfdf\n gfggfg',
                              result='failed',
                              error=\
"""
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
Exception: a
""")

    import pdb; pdb.set_trace()

    print db.get_test_results(sprint)

# EOF
