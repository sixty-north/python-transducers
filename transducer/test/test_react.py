from functools import partial
import unittest
from transducer.functional import compose
from transducer.react import transduce, iterable_source, IterableSink, SingularSink
from transducer.reducers import sending
from transducer.transducers import (mapping, filtering, taking, dropping_while, distinct, first)


class TestSingleTransducers(unittest.TestCase):

    def test_first(self):
        result = SingularSink()

        transduce(transducer=first(),
                  source=partial(iterable_source, [2, 4, 6, 8, 10]),
                  sink=result)
        self.assertEqual(result.value(), 2)

    # def test_first_with_predicate(self):
    #     result = transduce(transducer=first(lambda x: x > 5),
    #                        reducer=sender,
    #                        iterable=[2, 4, 6, 8, 10],
    #                        init=[])
    #     self.assertEqual(result, [6])
    #
    # def test_last(self):
    #     result = transduce(transducer=last(),
    #                        reducer=sender,
    #                        iterable=[2, 4, 6, 8, 10],
    #                        init=[])
    #     self.assertEqual(result, [10])
    #
    # def test_last_with_predicate(self):
    #     result = transduce(transducer=last(lambda x: x < 7),
    #                        reducer=appender,
    #                        iterable=[2, 4, 6, 8, 10],
    #                        init=[])
    #     self.assertEqual(result, [6])


class TestComposedTransducers(unittest.TestCase):

    def test_chained_transducers(self):

        result = IterableSink()

        transduce(transducer=compose(
                         mapping(lambda x: x*x),
                         filtering(lambda x: x % 5 != 0),
                         taking(6),
                         dropping_while(lambda x: x < 15),
                         distinct()),
                     source=partial(iterable_source, range(20)),
                     sink=result)

        expected = [16, 36, 49]
        for r, e in zip(result, expected):
            self.assertEqual(r, e)


if __name__ == '__main__':
    unittest.main()
