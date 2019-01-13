# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import unittest
from .. import utils


class TestUtils(unittest.TestCase):

    def test_safe_to_integer(self):
        self.assertEqual(utils.safe_to_integer(''), None)
        self.assertEqual(utils.safe_to_integer(False), 0)
        self.assertEqual(utils.safe_to_integer('abc'), None)
        self.assertEqual(utils.safe_to_integer('10.0'), None)
        self.assertEqual(utils.safe_to_integer('0'), 0)
        self.assertEqual(utils.safe_to_integer('10'), 10)

    def test_safe_to_float(self):
        self.assertEqual(utils.safe_to_float(''), None)
        self.assertEqual(utils.safe_to_float(False), 0.0)
        self.assertEqual(utils.safe_to_float('abc'), None)
        self.assertEqual(utils.safe_to_float('10,0'), None)
        self.assertEqual(utils.safe_to_float('10.0'), 10.0)
        self.assertEqual(utils.safe_to_float('0'), 0.0)
        self.assertEqual(utils.safe_to_float('10'), 10.0)

    def test_safe_to_date(self):
        self.assertEqual(utils.safe_to_date(''), None)
        self.assertEqual(utils.safe_to_date('2019-01-13'), '2019-01-13')

    def test_string_to_bool(self):
        for val in ('on', 'yes', 'ok', 'true', True, 1, '1', ):
            self.assertTrue(utils.string_to_bool(val))
        for val in ('', ' ', '2', 'no', 'whatever is not true'):
            self.assertFalse(utils.string_to_bool(val))

    def test_data_merge(self):
        a = {'a': 1, 'b': {'foo': 'bar'}, 'd': [1, 2], 'e': [5, 6]}
        b = {'a': 2, 'b': {'baz': 'taz'}, 'c': 'yo', 'd': [3, 4], 'e': 8}
        expected = {
            'a': 2,
            'b': {'foo': 'bar', 'baz': 'taz'},
            'c': 'yo',
            'd': [1, 2, 3, 4],
            'e': [5, 6, 8],
        }
        self.assertEqual(utils.data_merge(a, b), expected)
        with self.assertRaises(ValueError):
            utils.data_merge({'a': {'x': 1, 'y': 2}}, {'a': ['not', 'compat']})
        with self.assertRaises(NotImplementedError):
            utils.data_merge({'a': set([1, 2, 3])}, {'a': set([4, ])})
