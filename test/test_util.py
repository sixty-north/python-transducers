import unittest
from transducer._util import prepend, empty_iter, iterator_or_none


class TestPrepend(unittest.TestCase):

    def test_non_empty_iterable(self):
        result = list(prepend(42, [1, 2, 3]))
        self.assertListEqual(result, [42, 1, 2, 3])

    def test_empty_iterable(self):
        result = list(prepend(42, []))
        self.assertListEqual(result, [42])


class TestEmptyIter(unittest.TestCase):

    def test_is_empty(self):
        self.assertEqual(len(list(empty_iter())), 0)


class TestIteratorOrNone(unittest.TestCase):

    def test_empty_iterator_returns_none(self):
        self.assertIsNone(iterator_or_none(empty_iter()))

    def test_non_empty_iterator_returns_iterator(self):
        items = [1, 4, 7, 2, 4]
        it = iter(items)
        remaining = iterator_or_none(it)
        result = list(remaining)
        self.assertListEqual(result, items)
