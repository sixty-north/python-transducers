import unittest

from transducer.functional import compose, true, identity, false


class TestComposition(unittest.TestCase):

    def test_single(self):
        """
        compose(f)(x) -> f(x)
        """
        f = lambda x: x * 2
        c = compose(f)

        # We can't test the equivalence of functions completely, so...
        self.assertSequenceEqual([f(x) for x in range(1000)],
                                 [c(x) for x in range(1000)])

    def test_double(self):
        """
        compose(f, g)(x) -> f(g(x))
        """
        f = lambda x: x * 2
        g = lambda x: x + 1
        c = compose(f, g)

        self.assertSequenceEqual([f(g(x)) for x in range(100)],
                                 [c(x) for x in range(100)])

    def test_triple(self):
        """
        compose(f, g, h)(x) -> f(g(h(x)))
        """
        f = lambda x: x * 2
        g = lambda x: x + 1
        h = lambda x: x - 7
        c = compose(f, g, h)

        self.assertSequenceEqual([f(g(h(x))) for x in range(100)],
                                 [c(x) for x in range(100)])


class TestFunctions(unittest.TestCase):

    def test_true(self):
        self.assertTrue(true())

    def test_false(self):
        self.assertFalse(false())

    def test_identity(self):
        self.assertEqual(identity(42), 42)


if __name__ == '__main__':
    unittest.main()
