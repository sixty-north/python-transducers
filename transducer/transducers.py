"""Functions for creating transducers.

The functions in this module return transducers.
"""
from collections import deque
from functools import reduce
from transducer._util import UNSET
from transducer.functional import identity, true
from transducer.infrastructure import Reduced, Transducer


# Functions for creating transducers, which are themselves
# functions which transform one reducer to another

def mapping(transform):
    """Create a mapping transducer with the given transform"""

    class MappingTransducer(Transducer):

        def step(self, result, item):
            return self._reducer(result, transform(item))

    return MappingTransducer


def filtering(predicate):
    """Create a filtering transducer with the given predicate"""

    class FilteringTransducer(Transducer):

        def step(self, result, item):
            return self._reducer(result, item) if predicate(item) else result

    return FilteringTransducer


def reducing(reducer, init=UNSET):
    """Create a reducing transducer with the given reducer"""

    class ReducingTransducer(Transducer):

        accumulator = init

        def step(self, result, item):
            ReducingTransducer.accumulator = item if ReducingTransducer.accumulator is UNSET else reducer(ReducingTransducer.accumulator, item)
            return result

        def terminate(self, result):
            return ReducingTransducer.accumulator

    return ReducingTransducer


def scanning(reducer, init=UNSET):
    """Create a scanning reducer."""

    class ScanningTransducer(Transducer):

        accumulator = init

        def step(self, result, item):
            ScanningTransducer.accumulator = item if ScanningTransducer.accumulator is UNSET else reducer(ScanningTransducer.accumulator, item)
            return self._reducer(result, ScanningTransducer.accumulator)

    return ScanningTransducer


def enumerating(start=0):
    """Create a transducer which enumerates items."""

    class EnumeratingTransducer(Transducer):

        counter = start

        def step(self, result, item):
            index = EnumeratingTransducer.counter
            EnumeratingTransducer.counter += 1
            return self._reducer(result, (index, item))

    return EnumeratingTransducer


def mapcatting(transform):
    """Create a transducer which transforms items and concatenates the results"""

    class MapcattingTransducer(Transducer):

        def step(self, result, item):
            return reduce(self._reducer, result, transform(item))

    return MapcattingTransducer


def taking(n):
    """Create a transducer which takes the first n items"""

    class TakingTransducer(Transducer):

        counter = 0

        def step(self, result, item):
            if TakingTransducer.counter < n:
                TakingTransducer.counter += 1
                return self._reducer(result, item)
            return result

    return TakingTransducer


def dropping_while(predicate):
    """Create a transducer which drops leading items while a predicate holds"""

    class DroppingWhileTransducer(Transducer):

        dropping = True

        def step(self, result, item):
            DroppingWhileTransducer.dropping = DroppingWhileTransducer.dropping and predicate(item)
            return result if DroppingWhileTransducer.dropping else self._reducer(result, item)

    return DroppingWhileTransducer


def distinct():
    """Create a transducer which filters distinct items"""

    class DistinctTransducer(Transducer):

        seen = set()

        def step(self, result, item):
            if item not in DistinctTransducer.seen:
                DistinctTransducer.seen.add(item)
                return self._reducer(result, item)
            return result

    return DistinctTransducer


def pairwise():
    """Create a transducer which produces successive pairs"""

    class PairwiseTransducer(Transducer):

        previous_item = UNSET

        def step(self, result, item):
            if PairwiseTransducer.previous_item is UNSET:
                PairwiseTransducer.previous_item = item
                return result
            pair = (PairwiseTransducer.previous_item, item)
            PairwiseTransducer.previous_item = item
            return self._reducer(result, pair)

    return PairwiseTransducer


def batching(size):
    """Create a transducer which produces non-overlapping batches."""

    if size < 1:
        raise ValueError("batching() size must be at least 1")

    class BatchingTransducer(Transducer):

        pending = []

        def step(self, result, item):
            BatchingTransducer.pending.append(item)
            if len(BatchingTransducer.pending) == size:
                batch = BatchingTransducer.pending
                BatchingTransducer.pending = []
                return self._reducer(result, batch)
            return result

        def terminate(self, result):
            return self._reducer(result, BatchingTransducer.pending)

    return BatchingTransducer


def windowing(size, padding=UNSET):
    """Create a transducer which produces a moving window over items."""

    if size < 1:
        raise ValueError("windowing() size must be at least 1")

    class WindowingTransducer(Transducer):

        window = deque(maxlen=size) if padding is UNSET else deque([padding] * size, maxlen=size)

        def step(self, result, item):
            WindowingTransducer.window.append(item)
            return self._reducer(result, list(WindowingTransducer.window))

        def terminate(self, result):
            for _ in range(size - 1):
                result = self.step(result, padding)
            return result

    return WindowingTransducer


def first(predicate=None):
    """Create a transducer which obtains the first item, then terminates."""

    predicate = true if predicate is None else predicate

    class FirstTransducer(Transducer):

        def step(self, result, item):
            return Reduced(item) if predicate(item) else result

    return FirstTransducer


def last(predicate=None):
    """Create a transducer which obtains the last item."""

    predicate = true if predicate is None else predicate

    class LastTransducer(Transducer):

        last_seen = None

        def step(self, result, item):
            if predicate(item):
                LastTransducer.last_seen = item
            return result

        def terminate(self, result):
            return LastTransducer.last_seen

    return LastTransducer


def reversing():

    class ReversingTransducer(Transducer):

        items = deque()

        def step(self, result, item):
            ReversingTransducer.items.appendleft(item)
            return result

        def terminate(self, result):
            return ReversingTransducer.items

    return ReversingTransducer


def ordering(key=None, reverse=False):

    key = identity if key is None else key

    class OrderingTransducer(Transducer):

        items = []

        def step(self, result, item):
            OrderingTransducer.items.append(item)
            return result

        def terminate(self, result):
            OrderingTransducer.items.sort(key=key, reverse=reverse)
            return OrderingTransducer.items

    return OrderingTransducer


def counting(predicate=None):

    predicate = true if predicate is None else predicate

    class CountingTransducer(Transducer):

        count = 0

        def step(self, result, item):
            if predicate(item):
                CountingTransducer.count += 1
            return result

        def terminate(self, result):
            return CountingTransducer.count

    return CountingTransducer


def grouping(key=None):

    key = identity if key is None else key

    class GroupingTransducer(Transducer):

        groups = {}

        def step(self, result, item):
            k = key(item)
            if k not in GroupingTransducer.groups:
                GroupingTransducer.groups[k] = []
            GroupingTransducer.groups[k].append(item)
            return result

        def terminate(self, result):
            return GroupingTransducer.groups

    return GroupingTransducer
