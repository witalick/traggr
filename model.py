__author__ = 'yfedevych'

from itertools import groupby
import re
import copy

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
        'component_modified',
        'unique'
    )

    _normalize_regex = re.compile('[\'\"\(\)\[\]\.,\+\s\*@#\$%\^&\?=]')

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
        self.unique = False

    def __str__(self):
        return "<TestResult(%s, %s, %s.%s) = %s>" % (
            self.sprint,
            self.component,
            self.suite,
            self.test_id,
            self.result
        )

    def __repr__(self):
        return "<TestResult(%s, %s, %s.%s) = %s>" % (
            self.sprint,
            self.component,
            self.suite,
            self.test_id,
            self.result
        )

    def __hash__(self):
        return hash("{0}.{1} = {2}".format(
            self.suite,
            self.test_id,
            self.result
        ))

    def __eq__(self, other):
        return (
            self.result == other.result and
            self.suite == other.suite and
            self.test_id == other.test_id
        )

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except AttributeError:
            raise IndexError(item)

    def __setitem__(self, item, value):
        return setattr(self, item, value)


class TestResultsComparison(object):

    def __init__(self, left, right):
        self.left = left
        self.right = right
        self._iter = None
        lsuites = set([x.suite for x in self.left])
        rsuites = set([x.suite for x in self.right])
        self.suites = sorted(list(lsuites.union(rsuites)))
        self.left_by_suite = {}
        self.right_by_suite = {}
        self.all_left_by_suite = {}
        self.all_right_by_suite = {}
        self.components = {}

        self.unique_left = []
        self.unique_right = []

        component_counter = 0

        for result in self.left + self.right:
            x = self.components.setdefault(result.component, component_counter)
            if x == component_counter:
                component_counter += 1

        for suite in self.suites:
            onleft = set([x for x in self.left if x.suite == suite])
            onright = set([x for x in self.right if x.suite == suite])
            uniqleft = onleft.difference(onright)
            uniqright = onright.difference(onleft)
            self.left_by_suite[suite] = list(uniqleft)
            self.right_by_suite[suite] = list(uniqright)
            self.all_left_by_suite[suite] = list(onleft)
            self.all_right_by_suite[suite] = list(onright)
            [setattr(x, 'unique', True) for x in self.all_left_by_suite[suite] if x in uniqleft]
            [setattr(x, 'unique', True) for x in self.all_right_by_suite[suite] if x in uniqright]
            self.unique_left += self.left_by_suite[suite]
            self.unique_right += self.right_by_suite[suite]

    def suite_components(self, suite):
        l = set([x.component for x in self.all_left_by_suite[suite]])
        r = set([x.component for x in self.all_right_by_suite[suite]])
        return list(l), list(r)

    def used_components(self, sprint):
        current = self.unique_left
        if sprint != 0:
            current = self.unique_right
        return sorted(list(set([x.component for x in current])))

    def __iter__(self):
        for suite in self.suites:
            yield suite, self.left_by_suite[suite], self.right_by_suite[suite]

    def next(self):
        if self._iter is None:
            self._iter = iter(self)
        return next(self._iter)

    def reset(self):
        self._iter = None

    def iter_all(self):
        for suite in self.suites:
            yield suite, self.all_left_by_suite[suite], self.all_right_by_suite[suite]



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
        return list([TestResult(sprint=sprint, **rec) for rec in result])

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
