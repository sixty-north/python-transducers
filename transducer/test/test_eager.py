import operator
import unittest
from transducer.eager import transduce
from transducer.functional import compose
from transducer.reducers import appender
from transducer.transducers import (mapping, filtering, reducing, enumerating, first, last,
                                   reversing, ordering, counting, scanning, taking, dropping_while, distinct)


class TestSingleTransducers(unittest.TestCase):

    def test_mapping(self):
        result = transduce(transducer=mapping(lambda x: x*x),
                           reducer=appender,
                           iterable=range(5),
                           init=[])
        self.assertListEqual(result, [0, 1, 4, 9, 16])

    def test_filtering(self):
        result = transduce(transducer=filtering(lambda w: 'x' in w),
                           reducer=appender,
                           iterable='socks in box fox on clocks'.split(),
                           init=[])
        self.assertListEqual(result, ['box', 'fox'])

    def test_reducing(self):
        result = transduce(transducer=reducing(operator.add),
                           reducer=appender,
                           iterable=range(10),
                           init=[])
        self.assertEqual(result, 45)

    def test_reducing_with_init(self):
        result = transduce(transducer=reducing(operator.add, 10),
                           reducer=appender,
                           iterable=range(10),
                           init=[])
        self.assertEqual(result, 55)

    def test_scanning(self):
        result = transduce(transducer=scanning(operator.add),
                           reducer=appender,
                           iterable=range(5),
                           init=[])
        self.assertListEqual(result, [0, 1, 3, 6, 10])

    def test_scanning_within_init(self):
        result = transduce(transducer=scanning(operator.add, 3),
                           reducer=appender,
                           iterable=range(5),
                           init=[])
        self.assertListEqual(result, [3, 4, 6, 9, 13])

    def test_enumerating(self):
        result = transduce(transducer=enumerating(),
                           reducer=appender,
                           iterable=[2, 4, 6, 8, 10],
                           init=[])
        self.assertListEqual(result, [(0, 2), (1, 4), (2, 6), (3, 8), (4, 10)])

    def test_enumerating_with_start(self):
        result = transduce(transducer=enumerating(start=3),
                           reducer=appender,
                           iterable=[2, 4, 6, 8, 10],
                           init=[])
        self.assertListEqual(result, [(3, 2), (4, 4), (5, 6), (6, 8), (7, 10)])

    def test_first(self):
        result = transduce(transducer=first(),
                           reducer=appender,
                           iterable=[2, 4, 6, 8, 10],
                           init=[])
        self.assertEqual(result, 2)

    def test_first_with_predicate(self):
        result = transduce(transducer=first(lambda x: x > 5),
                           reducer=appender,
                           iterable=[2, 4, 6, 8, 10],
                           init=[])
        self.assertEqual(result, 6)

    def test_last(self):
        result = transduce(transducer=last(),
                           reducer=appender,
                           iterable=[2, 4, 6, 8, 10],
                           init=[])
        self.assertEqual(result, 10)

    def test_last_with_predicate(self):
        result = transduce(transducer=last(lambda x: x < 7),
                           reducer=appender,
                           iterable=[2, 4, 6, 8, 10],
                           init=[])
        self.assertEqual(result, 6)

    def test_reversing(self):
        result = transduce(transducer=reversing(),
                           reducer=appender,
                           iterable=[2, 4, 6, 8, 10],
                           init=[])
        self.assertSequenceEqual(result, [10, 8, 6, 4, 2])

    def test_ordering(self):
        result = transduce(transducer=ordering(),
                           reducer=appender,
                           iterable=[4, 2, 6, 10, 8],
                           init=[])
        self.assertSequenceEqual(result, [2, 4, 6, 8, 10])

    def test_ordering_reverse(self):
        result = transduce(transducer=ordering(reverse=True),
                           reducer=appender,
                           iterable=[4, 2, 6, 10, 8],
                           init=[])
        self.assertSequenceEqual(result, [10, 8, 6, 4, 2])

    def test_ordering_with_key(self):
        result = transduce(transducer=ordering(key=lambda x: len(x)),
                           reducer=appender,
                           iterable="The quick brown fox jumped".split(),
                           init=[])
        self.assertSequenceEqual(result, ['The', 'fox', 'quick', 'brown', 'jumped'])

    def test_ordering_reverse_with_key(self):
        result = transduce(transducer=ordering(key=lambda x: len(x), reverse=True),
                           reducer=appender,
                           iterable="The quick brown fox jumped".split(),
                           init=[])
        self.assertSequenceEqual(result, ['jumped', 'quick', 'brown', 'The', 'fox'])

    def test_counting(self):
        result = transduce(transducer=counting(),
                           reducer=appender,
                           iterable="The quick brown fox jumped".split(),
                           init=[])
        self.assertEqual(result, 5)

    def test_counting_with_predicate(self):
        result = transduce(transducer=counting(lambda w: 'o' in w),
                           reducer=appender,
                           iterable="The quick brown fox jumped".split(),
                           init=[])
        self.assertEqual(result, 2)


class TestComposedTransducers(unittest.TestCase):

    def test_chained_transducers(self):
        result = transduce(transducer=compose(
                          mapping(lambda x: x*x),
                          filtering(lambda x: x % 5 != 0),
                          taking(6),
                          dropping_while(lambda x: x < 15),
                          distinct()),
                      reducer=appender,
                      iterable=range(20),
                      init=[])
        self.assertSequenceEqual(result, [16, 36, 49])


if __name__ == '__main__':
    unittest.main()
