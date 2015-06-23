__author__ = 'yfedevych'

from itertools import groupby
import re

class TestResult(object):

    __slots__ = (
        '_id',
        'suite',
        'test_id',
        'title',
        'description',
        'component',
        'result',
        'error',
        'sprint',
        'attributes',
        'component_modified'
    )

    _normalize_regex = re.compile('[\'\"\(\)\[\]\.,\+\s\*@#\$%\^&\?]')

    @property
    def component_normalized(self):
        if self.component is None:
            return None
        return TestResult._normalize_regex.sub('-', self.component)

    @property
    def sprint_normalized(self):
        if self.sprint is None:
            return None
        return TestResult._normalize_regex.sub('-', self.sprint)

    def __init__(self, **kwargs):
        for x in self.__slots__:
            setattr(self, x, kwargs.get(x, None))

    def __hash__(self):
        return hash(tuple([
            self.result,
            self.test_id,
            self.suite
        ]))

    def __eq__(self, other):
        return (
            self.result == other.result and
            self.test_id == other.test_id and
            self.suite == other.suite
        )

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, item, value):
        return setattr(self, item, value)

def compare_sprints(db, *sprints, **query):
    """
    Returns a dictionary containing items unique to each sprint
    result, keyed by sprint.
    """
    def _get_results(db, sprint, **query):
        """
        A helper function that hydrates database results into a collection of
        objects
        """
        return set([TestResult(sprint=sprint, **rec) for rec in db.get_test_results(sprint, **query)])

    ressets = {}
    result = {}

    for sprint in sprints:
        ressets[sprint] = _get_results(db, sprint, **query)

    for sprint in sprints:
        #
        # strip the result sets to only elements that are not
        # present elsewhere. others is a set containing results
        # from elsewhere.
        #
        othersprints = [x for x in sprints if x != sprint]
        others = set([x for key in othersprints for x in ressets[key]])
        result[sprint] = set([x for x in ressets[sprint] if x not in others])
    return result

def common_results(db, *sprints, **query):
    """
    Returns a set containing items common to all sprints.
    """
    def _get_results(db, sprint, **query):
        """
        A helper function that hydrates database results into a collection of
        objects
        """
        result = db.get_test_results(sprint, **query)
        return set([TestResult(sprint=sprint, **rec) for rec in result])

    ressets = {}
    for sprint in sprints:
        ressets[sprint] = _get_results(db, sprint, **query)

    sprint = sprints[0]
    othersprints = sprints[1:]
    others = set([x for key in othersprints for x in ressets[key]])
    result = others.intersection(ressets[sprint])

    return result



def regroup_results(results, *keys):

    def keyfunc(x):
        return tuple([getattr(x, k) for k in keys])
    res = list(results)
    res.sort(key=keyfunc)
    return groupby(res, keyfunc)
