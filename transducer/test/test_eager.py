from collections import deque
import operator
import unittest
from transducer.eager import transduce
from transducer.functional import compose
from transducer.infrastructure import Transducer
from transducer.reducers import appending, expecting_single, conjoining, adding
from transducer.transducers import (mapping, filtering, reducing, enumerating, first, last,
                                    reversing, ordering, counting, scanning, taking, dropping_while, distinct,
                                    taking_while, dropping, element_at, mapcatting, pairwise, batching, windowing,
                                    repeating)


class TestSingleTransducers(unittest.TestCase):

    def test_identity(self):
        result = transduce(transducer=Transducer,
                           reducer=appending(),
                           iterable=range(5))
        self.assertListEqual(result, [0, 1, 2, 3, 4])

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

    def test_scanning_with_init(self):
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

    def test_mapcatting(self):
        result = transduce(transducer=mapcatting(list),
                           reducer=appending(),
                           iterable=['new', 'found', 'land'])
        self.assertListEqual(result, list("newfoundland"))

    def test_taking(self):
        result = transduce(transducer=taking(3),
                           reducer=appending(),
                           iterable=[2, 4, 5, 8, 10])
        self.assertListEqual(result, [2, 4, 5])

    def test_taking_validation(self):
        with self.assertRaises(ValueError):
            transduce(transducer=taking(-3),
                      reducer=appending(),
                      iterable=[2, 4, 5, 8, 10])

    def test_taking_while(self):
        result = transduce(transducer=taking_while(lambda x: x < 6),
                           reducer=appending(),
                           iterable=[2, 4, 5, 8, 10])
        self.assertListEqual(result, [2, 4, 5])

    def test_dropping(self):
        result = transduce(transducer=dropping(3),
                           reducer=appending(),
                           iterable=[2, 4, 5, 8, 10])
        self.assertListEqual(result, [8, 10])

    def test_dropping_validation(self):
        with self.assertRaises(ValueError):
            transduce(transducer=dropping(-3),
                      reducer=appending(),
                      iterable=[2, 4, 5, 8, 10])

    def test_dropping_while(self):
        result = transduce(transducer=dropping_while(lambda x: x < 6),
                           reducer=appending(),
                           iterable=[2, 4, 5, 8, 10])
        self.assertListEqual(result, [8, 10])

    def test_distinct(self):
        result = transduce(transducer=distinct(),
                           reducer=appending(),
                           iterable=[1, 1, 3, 5, 5, 2, 1, 2])
        self.assertListEqual(result, [1, 3, 5, 2])

    def test_pairwise_at_least_two(self):
        result = transduce(transducer=pairwise(),
                           reducer=appending(),
                           iterable=[1, 3, 5, 7, 2, 1, 9])
        self.assertListEqual(result, [(1, 3), (3, 5), (5, 7), (7, 2), (2, 1), (1, 9)])

    def test_pairwise_single(self):
        """A single item fed into pairwise is discarded."""
        result = transduce(transducer=pairwise(),
                           reducer=appending(),
                           iterable=[42])
        self.assertListEqual(result, [])

    def test_batching_exact(self):
        result = transduce(transducer=batching(3),
                           reducer=appending(),
                           iterable=[42, 12, 45, 9, 18, 3, 34, 13, 12])
        self.assertListEqual(result, [[42, 12, 45], [9, 18, 3], [34, 13, 12]])

    def test_batching_inexact_1(self):
        result = transduce(transducer=batching(3),
                           reducer=appending(),
                           iterable=[42, 12, 45, 9, 18, 3, 34])
        self.assertListEqual(result, [[42, 12, 45], [9, 18, 3], [34]])

    def test_batching_inexact_2(self):
        result = transduce(transducer=batching(3),
                           reducer=appending(),
                           iterable=[42, 12, 45, 9, 18, 3, 34, 13])
        self.assertListEqual(result, [[42, 12, 45], [9, 18, 3], [34, 13]])

    def test_batching_validation(self):
        with self.assertRaises(ValueError):
            transduce(transducer=batching(0),
                      reducer=appending(),
                      iterable=[42, 12, 45, 9, 18, 3, 34, 13])

    def test_windowing_no_padding(self):
        result = transduce(transducer=windowing(3, window_type=list),
                           reducer=appending(),
                           iterable=[42, 12, 45, 9, 18, 3, 34, 13])
        self.assertListEqual(result,
                             [[42],
                              [42, 12],
                              [42, 12, 45],
                              [12, 45, 9],
                              [45, 9, 18],
                              [9, 18, 3],
                              [18, 3, 34],
                              [3, 34, 13],
                              [34, 13],
                              [13]])

    def test_windowing_padding(self):
        result = transduce(transducer=windowing(3, padding=0, window_type=list),
                           reducer=appending(),
                           iterable=[42, 12, 45, 9, 18, 3, 34, 13])
        self.assertListEqual(result,
                             [[0, 0, 42],
                              [0, 42, 12],
                              [42, 12, 45],
                              [12, 45, 9],
                              [45, 9, 18],
                              [9, 18, 3],
                              [18, 3, 34],
                              [3, 34, 13],
                              [34, 13, 0],
                              [13, 0, 0]])

    def test_windowing_validation(self):
        with self.assertRaises(ValueError):
            transduce(transducer=windowing(0),
                      reducer=appending(),
                      iterable=[42, 12, 45, 9, 18, 3, 34, 13])

    def test_element_at(self):
        result = transduce(transducer=element_at(3),
                           reducer=expecting_single(),
                           iterable=[1, 3, 5, 7, 9])
        self.assertEqual(result, 7)

    def test_element_at_validation(self):
        with self.assertRaises(IndexError):
            transduce(transducer=element_at(-1),
                               reducer=expecting_single(),
                               iterable=[1, 3, 5, 7, 9])

    def test_element_at_too_short(self):
        with self.assertRaises(IndexError):
            transduce(transducer=element_at(3),
                      reducer=expecting_single(),
                      iterable=[1, 3, 5])

    def test_repeating(self):
        result = transduce(transducer=repeating(3),
                           reducer=appending(),
                           iterable=[1, 3, 5])
        self.assertListEqual(result, [1, 1, 1, 3, 3, 3, 5, 5, 5])

    def test_repeating_zero(self):
        result = transduce(transducer=repeating(0),
                           reducer=appending(),
                           iterable=[1, 3, 5])
        self.assertListEqual(result, [])

    def test_repeating_validation(self):
        with self.assertRaises(ValueError):
            transduce(transducer=repeating(-1),
                      reducer=appending(),
                      iterable=[1, 3, 5])

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

    def test_mutable_inits(self):
        """Tests that the same mutable init object isn't shared across invocations."""
        result = transduce(transducer=mapping(lambda x: x), reducer=appending(), iterable=range(3))
        self.assertListEqual(result, [0, 1, 2])
        result = transduce(transducer=mapping(lambda x: x), reducer=appending(), iterable=range(3))
        self.assertListEqual(result, [0, 1, 2])

    def test_adding_reducer(self):
        result = transduce(
            transducer=mapping(lambda x: x * x),
            reducer=adding(),
            iterable=list(range(3)) * 2)
        self.assertListEqual(list(result), [0, 1, 4])


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
