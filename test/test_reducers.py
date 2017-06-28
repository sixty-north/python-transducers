import unittest
from transducer._util import empty_iter
from transducer.eager import transduce
from transducer.infrastructure import Transducer
from transducer.reducers import expecting_single, appending, conjoining, adding, sending, completing
from transducer.sinks import CollectingSink, SingularSink
from transducer.transducers import mapping


class TestAppending(unittest.TestCase):

    def test_zero_items_returns_initial_empty_list(self):
        result = transduce(Transducer,
                           appending(),
                           empty_iter())
        self.assertEqual(result, [])

    def test_two_items_returns_two_element_list(self):
        result = transduce(Transducer,
                           appending(),
                           (23, 78))
        self.assertEqual(result, [23, 78])

    def test_appending_to_immutable_sequence_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            transduce(Transducer,
                      appending(),
                      (23, 78),
                      init=tuple())


class TestConjoining(unittest.TestCase):

    def test_zero_items_returns_initial_empty_tuple(self):
        result = transduce(Transducer,
                           conjoining(),
                           empty_iter())
        self.assertEqual(result, tuple())

    def test_two_items_returns_two_element_tuple(self):
        result = transduce(Transducer,
                           conjoining(),
                           [23, 78])
        self.assertEqual(result, (23, 78))

    def test_conjoining_to_non_sequence_raises_type_error(self):
        with self.assertRaises(TypeError):
            transduce(Transducer,
                      conjoining(),
                      (23, 78),
                      init=set())

    def test_conjoining_preserves_initial_sequence_type(self):
        result = transduce(Transducer,
                           conjoining(),
                           (23, 78),
                           init=[])
        self.assertEqual(result, [23, 78])


class TestAdding(unittest.TestCase):

    def test_zero_items_returns_initial_empty_set(self):
        result = transduce(Transducer,
                           adding(),
                           empty_iter())
        self.assertEqual(result, set())

    def test_two_items_returns_two_element_list(self):
        result = transduce(Transducer,
                           adding(),
                           [23, 78])
        self.assertEqual(result, {23, 78})

    def test_adding_to_non_set_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            transduce(Transducer,
                      adding(),
                      (23, 78),
                      init=tuple())


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


class TestSending(unittest.TestCase):

    def test_zero_items_returns_initial_empty_collection(self):
        collection = CollectingSink()

        transduce(Transducer,
                  sending(),
                  empty_iter(),
                  init=collection())

        self.assertEqual(len(collection), 0)

    def test_two_items_returns_two_element_list(self):
        collection = CollectingSink()

        transduce(Transducer,
                  sending(),
                  [23, 78],
                  init=collection())

        self.assertEqual(list(collection), [23, 78])

    def test_sending_to_non_sink_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            transduce(Transducer,
                      sending(),
                      (23, 78),
                      init=set())

    def test_two_items_causes_completion(self):
        singular_sink = SingularSink()

        transduce(Transducer,
                  sending(),
                  [23, 78],
                  init=singular_sink())

        self.assertTrue(singular_sink.has_value)


class TestCompleting(unittest.TestCase):

    def test_completing_with_summing_zero_items_returns_identity(self):

        def add(a, b):
            return a + b

        summing = completing(add, identity=0)

        result = transduce(Transducer,
                           summing,
                           [])
        self.assertEqual(result, 0)

    def test_completing_with_summing_four_items(self):

        def add(a, b):
            return a + b

        summing = completing(add, identity=0)

        result = transduce(Transducer,
                           summing,
                           [4, 2, 1, 9])
        self.assertEqual(result, 16)

    def test_completing_with_multiplying_zero_items_returns_identity(self):

        def multiply(a, b):
            return a * b

        multiplying = completing(multiply, identity=1)

        result = transduce(Transducer,
                           multiplying,
                           [])
        self.assertEqual(result, 1)

    def test_completing_with_multiplying_four_items(self):

        def multiply(a, b):
            return a * b

        multiplying = completing(multiply, identity=1)

        result = transduce(Transducer,
                           multiplying,
                           [4, 2, 1, 9])
        self.assertEqual(result, 72)
