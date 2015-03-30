import unittest
from transducer.eager import transduce
from transducer.reducers import expecting_single
from transducer.transducers import mapping


class TestExpectingSingle(unittest.TestCase):

    def test_too_few_items(self):
        with self.assertRaises(RuntimeError):
            transduce(mapping(lambda x: x*x),
                      expecting_single(),
                      [1, 2])

    def test_exactly_one_item(self):
        result = transduce(mapping(lambda x: x*x),
                           expecting_single(),
                           [42])
        self.assertEqual(result, 1764)

    def test_too_many_items(self):
        with self.assertRaises(RuntimeError):
            transduce(mapping(lambda x: x*x),
                      expecting_single(),
                      [])


