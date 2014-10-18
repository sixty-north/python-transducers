import unittest
from transducers.transducer import (mapping, filtering, generate, compose, taking, dropping_while, distinct)


class TestComposedTransducers(unittest.TestCase):

    def test_chained_transducers(self):
        result = generate(transducer=compose(
                         mapping(lambda x: x*x),
                         filtering(lambda x: x % 5 != 0),
                         taking(6),
                         dropping_while(lambda x: x < 15),
                         distinct()),
                     iterable=range(20))

        expected = [16, 36, 49]
        for r, e in zip(result, expected):
            self.assertEqual(r, e)

if __name__ == '__main__':
    unittest.main()
