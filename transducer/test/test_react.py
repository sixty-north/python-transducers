import unittest
from transducer.functional import compose
from transducer.react import transduce
from transducer.sinks import CollectingSink
from transducer.sources import iterable_source
from transducer.transducers import (mapping, pairwise, filtering)


class TestComposedTransducers(unittest.TestCase):

    def test_chained_transducers(self):


        input = [0.0,
                 0.2,
                 0.8,
                 0.9,
                 1.1,
                 2.3,
                 2.6,
                 3.0,
                 4.1]

        output = CollectingSink()

        iterable_source(iterable=input,
                        target=transduce(
                            compose(pairwise(),
                                    mapping(lambda p: p[1] - p[0]),
                                    filtering(lambda d: d < 0.5),
                                    mapping(lambda _: "double-click")),
                            target=output()))

        pass


if __name__ == '__main__':
    unittest.main()
