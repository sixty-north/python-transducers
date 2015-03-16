from collections import deque
import operator
import unittest
from transducer.eager import transduce
from transducer.functional import compose
from transducer.reducers import appending, expecting_single, conjoining
from transducer.transducers import (mapping, filtering, reducing, enumerating, first, last,
                                    reversing, ordering, counting, scanning, taking, dropping_while, distinct)


class TestSingleTransducers(unittest.TestCase):

    def test_mapping(self):
        result = transduce(transducer=mapping(lambda x: x*x),
                           reducer=appending(),
                           iterable=range(5))
        self.assertListEqual(result, [0, 1, 4, 9, 16])

    def test_filtering(self):
        result = transduce(transducer=filtering(lambda w: 'x' in w),
                           reducer=appending(),
                           iterable='socks in box fox on clocks'.split())
        self.assertListEqual(result, ['box', 'fox'])

    def test_reducing(self):
        result = transduce(transducer=reducing(operator.add),
                           reducer=expecting_single(),
                           iterable=range(10))
        self.assertEqual(result, 45)

    def test_reducing_with_init(self):
        result = transduce(transducer=reducing(operator.add, 10),
                           reducer=expecting_single(),
                           iterable=range(10))
        self.assertEqual(result, 55)

    def test_scanning(self):
        result = transduce(transducer=scanning(operator.add),
                           reducer=appending(),
                           iterable=range(5))
        self.assertListEqual(result, [0, 1, 3, 6, 10])

    def test_scanning_within_init(self):
        result = transduce(transducer=scanning(operator.add, 3),
                           reducer=appending(),
                           iterable=range(5))
        self.assertListEqual(result, [3, 4, 6, 9, 13])

    def test_enumerating(self):
        result = transduce(transducer=enumerating(),
                           reducer=appending(),
                           iterable=[2, 4, 6, 8, 10])
        self.assertListEqual(result, [(0, 2), (1, 4), (2, 6), (3, 8), (4, 10)])

    def test_enumerating_with_start(self):
        result = transduce(transducer=enumerating(start=3),
                           reducer=appending(),
                           iterable=[2, 4, 6, 8, 10])
        self.assertListEqual(result, [(3, 2), (4, 4), (5, 6), (6, 8), (7, 10)])

    def test_first(self):
        result = transduce(transducer=first(),
                           reducer=expecting_single(),
                           iterable=[2, 4, 6, 8, 10])
        self.assertEqual(result, 2)

    def test_first_with_predicate(self):
        result = transduce(transducer=first(lambda x: x > 5),
                           reducer=expecting_single(),
                           iterable=[2, 4, 6, 8, 10])
        self.assertEqual(result, 6)

    def test_last(self):
        result = transduce(transducer=last(),
                           reducer=expecting_single(),
                           iterable=[2, 4, 6, 8, 10])
        self.assertEqual(result, 10)

    def test_last_with_predicate(self):
        result = transduce(transducer=last(lambda x: x < 7),
                           reducer=expecting_single(),
                           iterable=[2, 4, 6, 8, 10])
        self.assertEqual(result, 6)

    def test_reversing(self):
        result = transduce(transducer=reversing(),
                           reducer=appending(),
                           iterable=[2, 4, 6, 8, 10])
        self.assertSequenceEqual(result, [10, 8, 6, 4, 2])

    def test_reversing_preserves_mutable_sequence_type(self):
        result = transduce(transducer=reversing(),
                           reducer=appending(),
                           iterable=[2, 4, 6, 8, 10])
        self.assertIsInstance(result, list)
        self.assertSequenceEqual(result, [10, 8, 6, 4, 2])

# TODO: Test batching, etc

    def test_ordering(self):
        result = transduce(transducer=ordering(),
                           reducer=appending(),
                           iterable=[4, 2, 6, 10, 8])
        self.assertSequenceEqual(result, [2, 4, 6, 8, 10])

    def test_ordering_preserves_mutable_sequence_type(self):
        result = transduce(transducer=ordering(),
                           reducer=appending(),
                           iterable=[4, 2, 6, 10, 8],
                           init=deque())
        self.assertIsInstance(result, deque)
        self.assertSequenceEqual(result, deque([2, 4, 6, 8, 10]))

    def test_ordering_preserves_immutable_sequence_type(self):
        result = transduce(transducer=ordering(),
                           reducer=conjoining(),
                           iterable=[4, 2, 6, 10, 8])
        self.assertIsInstance(result, tuple)
        self.assertSequenceEqual(result, (2, 4, 6, 8, 10))

    def test_ordering_reverse(self):
        result = transduce(transducer=ordering(reverse=True),
                           reducer=appending(),
                           iterable=[4, 2, 6, 10, 8])
        self.assertSequenceEqual(result, [10, 8, 6, 4, 2])

    def test_ordering_with_key(self):
        result = transduce(transducer=ordering(key=lambda x: len(x)),
                           reducer=appending(),
                           iterable="The quick brown fox jumped".split())
        self.assertSequenceEqual(result, ['The', 'fox', 'quick', 'brown', 'jumped'])

    def test_ordering_reverse_with_key(self):
        result = transduce(transducer=ordering(key=lambda x: len(x), reverse=True),
                           reducer=appending(),
                           iterable="The quick brown fox jumped".split())
        self.assertSequenceEqual(result, ['jumped', 'quick', 'brown', 'The', 'fox'])

    def test_counting(self):
        result = transduce(transducer=counting(),
                           reducer=expecting_single(),
                           iterable="The quick brown fox jumped".split())
        self.assertEqual(result, 5)

    def test_counting_with_predicate(self):
        result = transduce(transducer=counting(lambda w: 'o' in w),
                           reducer=expecting_single(),
                           iterable="The quick brown fox jumped".split())
        self.assertEqual(result, 2)


class TestComposedTransducers(unittest.TestCase):

    def test_chained_transducers(self):
        result = transduce(transducer=compose(
                          mapping(lambda x: x*x),
                          filtering(lambda x: x % 5 != 0),
                          taking(6),
                          dropping_while(lambda x: x < 15),
                          distinct()),
                      reducer=appending(),
                      iterable=range(20))
        self.assertSequenceEqual(result, [16, 36, 49])


if __name__ == '__main__':
    unittest.main()
