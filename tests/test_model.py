# -*- coding: utf-8 -*-
from .. import model
from unittest import TestCase

class TestTraggrModel(TestCase):

    def test_initialization(self):
        m = model.TestResult(
            suite='dinosaurs',
            test_id='t-rex',
            result='failed',
            component='jurassic',
            sprint='01'
        )
        self.assertEqual(m.sprint, '01')
        self.assertEqual(m.component, 'jurassic')
        self.assertEqual(m.suite, 'dinosaurs')
        self.assertEqual(m.test_id, 't-rex')
        self.assertEqual(m.result, 'failed')
        m = model.TestResult(nonexistent=123)
        with self.assertRaises(AttributeError):
            foo = m.nonexistent

    def test_equality(self):
        """
        Test that model objects compare right.

        The model objects are equal if and only if their suite, test_id, and result are equal.
        """
        m1 = model.TestResult(
            sprint='s01',
            component='component 1',
            suite='TestSuite',
            test_id='test_01',
            result='passed'
        )
        m2 = model.TestResult(
            sprint='s02',
            component='utterly other component',
            suite='TestSuite',
            test_id='test_01',
            result='passed'
        )
        self.assertEqual(m1, m2, 'The results are equal when their suite, result, and id are the same')
        m2 = model.TestResult(
            sprint='s02',
            component='utterly other component',
            suite='TestSuite',
            test_id='test_01',
            result='failed'
        )
        self.assertNotEqual(m1, m2, 'The results are different when results are not the same')
        m2 = model.TestResult(
            sprint='s02',
            component='utterly other component',
            suite='TestSuite',
            test_id='test_02',
            result='passed'
        )
        self.assertNotEqual(m1, m2, 'The results are different when test_ids are not the same')
        m2 = model.TestResult(
            sprint='s02',
            component='utterly other component',
            suite='AnotherTestSuite',
            test_id='test_01',
            result='passed'
        )
        self.assertNotEqual(m1, m2, 'The results are different when suites are not the same')

    def test_sets(self):
        """
        Test results behavior when used in sets.
        """
        testset = set([
            model.TestResult(
                sprint='s01',
                component='component 1',
                suite='TestSuite',
                test_id='test_01',
                result='passed'
            ),
            model.TestResult(
                sprint='s02',
                component='utterly other component',
                suite='TestSuite',
                test_id='test_01',
                result='failed'
            ),
            model.TestResult(
                sprint='s03',
                component='utterly other component',
                suite='TestSuite',
                test_id='test_01',
                result='failed'
            )
        ])
        self.assertEqual(len(testset), 2)
        self.assertTrue(model.TestResult(
            sprint='A completely different sprint',
            component=None,
            suite='TestSuite',
            test_id='test_01',
            result='failed'
        ) in testset, 'set contains operation')
        self.assertFalse(model.TestResult(
            sprint='s01',
            component='component 1',
            suite='TestSuite',
            test_id='test_02',
            result='failed'
        ) in testset, 'set contains operation')



    def test_dictinterface(self):
        m1 = model.TestResult(
            sprint='s01',
            component='component 1',
            suite='TestSuite',
            test_id='test_01',
            result='passed'
        )
        self.assertEqual(m1['sprint'], 's01')
        m1['sprint'] = 'Something else'
        self.assertEqual(m1['sprint'], 'Something else')
        with self.assertRaises(AttributeError):
            m1['nonexistent'] = 'foo'
        with self.assertRaises(IndexError):
            a = m1['othernonexistent']

    def test_comparison(self):
        m1 = model.TestResultsComparison([
            model.TestResult(sprint='s01', component='s01c01', suite='FirstSuite', test_id='test_01', result='failed'),
            model.TestResult(sprint='s01', component='s01c01', suite='FirstSuite', test_id='test_02', result='error'),
            model.TestResult(sprint='s01', component='s01c01', suite='SecondSuite', test_id='test_01', result='failed'),
            model.TestResult(sprint='s02', component='s01c01', suite='FourthSuite', test_id='test_01', result='passed'),
        ], [
            model.TestResult(sprint='s02', component='s02c01', suite='FirstSuite', test_id='test_01', result='failed'),
            model.TestResult(sprint='s02', component='s02c01', suite='FirstSuite', test_id='test_02', result='error'),
            model.TestResult(sprint='s02', component='s02c01', suite='SecondSuite', test_id='test_01', result='failed'),
            model.TestResult(sprint='s02', component='s02c01', suite='SecondSuite', test_id='test_02', result='passed'),
            model.TestResult(sprint='s02', component='s02c01', suite='ThirdSuite', test_id='test_01', result='passed'),
        ])
        self.assertEqual(len(m1.suites), 4)
        self.assertEqual(len(m1.left), 4)
        self.assertEqual(len(m1.right), 5)
        self.assertEqual(len(m1.left_by_suite['FirstSuite']), 0)
        self.assertEqual(len(m1.all_left_by_suite['FirstSuite']), 2)
        self.assertEqual(len(m1.right_by_suite['FirstSuite']), 0)
        self.assertEqual(len(m1.all_right_by_suite['FirstSuite']), 2)
        self.assertEqual(len(m1.left_by_suite['SecondSuite']), 0)
        self.assertEqual(len(m1.all_left_by_suite['SecondSuite']), 1)
        self.assertEqual(len(m1.right_by_suite['SecondSuite']), 1)
        self.assertEqual(len(m1.all_right_by_suite['SecondSuite']), 2)
        self.assertEqual(len(m1.left_by_suite['ThirdSuite']), 0)
        self.assertEqual(len(m1.all_left_by_suite['ThirdSuite']), 0)
        self.assertEqual(len(m1.right_by_suite['ThirdSuite']), 1)
        self.assertEqual(len(m1.all_right_by_suite['ThirdSuite']), 1)
        self.assertEqual(len(m1.left_by_suite['FourthSuite']), 1)
        self.assertEqual(len(m1.all_left_by_suite['FourthSuite']), 1)
        self.assertEqual(len(m1.right_by_suite['FourthSuite']), 0)
        self.assertEqual(len(m1.all_right_by_suite['FourthSuite']), 0)
        self.assertEqual(len(m1.components.keys()), 2)
        suites = m1.suite_components('FirstSuite')
        self.assertEqual(set(suites[0]), set(['s01c01']))
        self.assertEqual(set(suites[1]), set(['s02c01']))

    def test_comparison_iteration(self):
        m1 = model.TestResultsComparison([
            model.TestResult(sprint='s01', component='s01c01', suite='FirstSuite', test_id='test_01', result='failed'),
            model.TestResult(sprint='s01', component='s01c01', suite='FirstSuite', test_id='test_02', result='error'),
            model.TestResult(sprint='s01', component='s01c01', suite='SecondSuite', test_id='test_01', result='failed'),
            model.TestResult(sprint='s02', component='s01c01', suite='FourthSuite', test_id='test_01', result='passed'),
        ], [
            model.TestResult(sprint='s02', component='s02c01', suite='FirstSuite', test_id='test_01', result='failed'),
            model.TestResult(sprint='s02', component='s02c01', suite='FirstSuite', test_id='test_02', result='error'),
            model.TestResult(sprint='s02', component='s02c01', suite='SecondSuite', test_id='test_01', result='failed'),
            model.TestResult(sprint='s02', component='s02c01', suite='SecondSuite', test_id='test_02', result='passed'),
            model.TestResult(sprint='s02', component='s02c01', suite='ThirdSuite', test_id='test_01', result='passed'),
        ])
        suite, left, right = next(m1)
        self.assertEqual(suite, 'FirstSuite')
        self.assertEqual(len(left), 0)
        self.assertEqual(len(right), 0)
        suite, left, right = next(m1)
        self.assertEqual(suite, 'FourthSuite')
        self.assertEqual(len(left), 1)
        self.assertEqual(len(right), 0)
        suite, left, right = next(m1)
        self.assertEqual(suite, 'SecondSuite')
        self.assertEqual(len(left), 0)
        self.assertEqual(len(right), 1)
        suite, left, right = next(m1)
        self.assertEqual(suite, 'ThirdSuite')
        self.assertEqual(len(left), 0)
        self.assertEqual(len(right), 1)

