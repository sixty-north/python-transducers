from functools import partial
import unittest
from transducers.react import transduce, sender, iterable_source, IterableSink
from transducers.transducer import (mapping, filtering, compose, taking, dropping_while, distinct)


class TestComposedTransducers(unittest.TestCase):

    def test_chained_transducers(self):

        result = IterableSink()

        transduce(transducer=compose(
                         mapping(lambda x: x*x),
                         filtering(lambda x: x % 5 != 0),
                         taking(6),
                         dropping_while(lambda x: x < 15),
                         distinct()),
                     reducer=sender,
                     source=partial(iterable_source, range(20)),
                     sink=result)

        expected = [16, 36, 49]
        for r, e in zip(result, expected):
            self.assertEqual(r, e)


if __name__ == '__main__':
    unittest.main()
