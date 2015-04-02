import unittest

import transducer.parallel as parallel
from transducer.reducers import appending, extending
from transducer.transducers import mapping


def square(x):
    return x*x


class TestParallel(unittest.TestCase):

    def test_mapping_square(self):


        items = list(range(1000))

        result = parallel.transduce(
            transducer=mapping(square),
            series_reducer=appending(),
            parallel_reducer=extending(),
            iterable=items)

        self.assertListEqual(result, [square(x) for x in items])
