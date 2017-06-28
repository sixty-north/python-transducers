import unittest
from transducer._util import iterator_or_none

from transducer.sinks import CollectingSink, SingularSink
from transducer.sources import iterable_source, poisson_source


class TestIterableSource(unittest.TestCase):

    def test_empty_iterable_sends_no_items(self):
        collection = CollectingSink()
        sink = collection()
        iterable_source([], sink)
        self.assertEqual(len(collection), 0)

    def test_three_item_iterable_sends_three_items(self):
        items = [4, 7, 2, 1, 4]
        collection = CollectingSink()
        sink = collection()
        iterable_source(items, sink)
        result = list(collection)
        self.assertListEqual(result, items)

    def test_closed_target_exits_with_remaining_items(self):
        items = [4, 7, 2, 1, 4]
        collection = SingularSink()
        sink = collection()
        remaining = iterable_source(items, sink)
        self.assertListEqual(list(remaining), [7, 2, 1, 4])

    def test_all_consumed_exits_with_empty_iterator(self):
        items = [4, 7, 2, 1, 4]
        collection = CollectingSink()
        sink = collection()
        remaining = iterable_source(items, sink)
        self.assertIsNone(iterator_or_none(remaining))


class TestPoissonSource(unittest.TestCase):

    def test_empty_iterable_sends_no_items(self):
        collection = CollectingSink()
        sink = collection()
        poisson_source(1e6, [], sink)
        self.assertEqual(len(collection), 0)

    def test_three_item_iterable_sends_three_items(self):
        items = [4, 7, 2, 1, 4]
        collection = CollectingSink()
        sink = collection()
        poisson_source(1e6, items, sink)
        result = list(collection)
        self.assertListEqual(result, items)

    def test_closed_target_exits_with_remaining_items(self):
        items = [4, 7, 2, 1, 4]
        collection = SingularSink()
        sink = collection()
        remaining = poisson_source(1e6, items, sink)
        self.assertListEqual(list(remaining), [7, 2, 1, 4])

    def test_all_consumed_exits_with_empty_iterator(self):
        items = [4, 7, 2, 1, 4]
        collection = CollectingSink()
        sink = collection()
        remaining = poisson_source(1e6, items, sink)
        self.assertIsNone(iterator_or_none(remaining))

    def test_non_positive_rate_raises_value_error(self):
        with self.assertRaises(ValueError):
            poisson_source(0.0, [], None)


if __name__ == '__main__':
    unittest.main()
