"""Transducers in Python

http://blog.cognitect.com/blog/2014/8/6/transducers-are-coming
"""
from abc import abstractmethod, ABCMeta
from collections import deque
from functools import reduce
from transducer._util import UNSET
from transducer.functional import identity, true


# Example reducers

def appender(result, item):
    """A reducer for appending to a list"""
    result.append(item)
    return result


# Transducer infrastructure

class Reduced:
    """A sentinel 'box' used to return the final value of a reduction."""

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value


class Transducer(metaclass=ABCMeta):
    """An Abstract Base Class for Transducers.

    At least the step() method must be overridden.
    """

    def __init__(self, reducer):
        self._reducer = reducer

    def __call__(self, result, item):
        """Transducers are callable, so they can be used as reducers."""
        return self.step(result, item)

    def initial(self):
        return self._reducer.initial()

    @abstractmethod
    def step(self, result, item):
        """Reduce one item.

        Called once for each item. Overrides should invoke the callable self._reducer
        directly as self._reducer(...) rather than as self._reducer.step(...) so that
        any 2-arity reduction callable can be used.

        Args:
            result: The reduced result thus far.
            item: The new item to be combined with result to give the new result.

        Returns:
            The newly reduced result; that is, result combined in some way with
            item to produce a new result.  If reduction needs to be terminated,
            this method should return the sentinel Reduced(result).
        """
        raise NotImplementedError

    def complete(self, result):
        """Called at exactly once when reduction is complete.

        Called on completion of a transducible process.
        Consider overriding terminate() rather than this method for convenience.
        """
        result = self.terminate(result)

        try:
            return self._reducer.complete(result)
        except AttributeError:
            return result

    def terminate(self, result):
        """Optionally override to terminate the result."""
        return result


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

    accumulator = init

    class ReducingTransducer(Transducer):

        def step(self, result, item):
            nonlocal accumulator
            accumulator = item if accumulator is UNSET else reducer(accumulator, item)
            return result

        def terminate(self, result):
            return accumulator

    return ReducingTransducer


def scanning(reducer, init=UNSET):
    """Create a scanning reducer."""

    accumulator = init

    class ScanningTransducer(Transducer):

        def step(self, result, item):
            nonlocal accumulator
            accumulator = item if accumulator is UNSET else reducer(accumulator, item)
            return self._reducer(result, accumulator)

    return ScanningTransducer


def enumerating(start=0):
    """Create a transducer which enumerates items."""

    counter = start

    class EnumeratingTransducer(Transducer):

        def step(self, result, item):
            nonlocal counter
            index = counter
            counter += 1
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
    counter = 0

    class TakingTransducer(Transducer):

        def step(self, result, item):
            nonlocal counter
            if counter < n:
                counter += 1
                return self._reducer(result, item)
            return result

    return TakingTransducer


def dropping_while(predicate):
    """Create a transducer which drops leading items while a predicate holds"""
    dropping = True

    class DroppingWhileTransducer(Transducer):

        def step(self, result, item):
            nonlocal dropping
            dropping = dropping and predicate(item)
            return result if dropping else self._reducer(result, item)

    return DroppingWhileTransducer


def distinct():
    """Create a transducer which filters distinct items"""
    seen = set()

    class DistinctTransducer(Transducer):

        def step(self, result, item):
            if item not in seen:
                seen.add(item)
                return self._reducer(result, item)
            return result

    return DistinctTransducer


def pairwise():
    """Create a transducer which produces successive pairs"""
    previous_item = UNSET

    class PairwiseTransducer(Transducer):

        def step(self, result, item):
            nonlocal previous_item
            if previous_item is UNSET:
                previous_item = item
                return result
            pair = (previous_item, item)
            previous_item = item
            return self._reducer(result, pair)

    return PairwiseTransducer


def batching(size):
    """Create a transducer which produces non-overlapping batches."""

    if size < 1:
        raise ValueError("batching() size must be at least 1")

    pending = []

    class BatchingTransducer(Transducer):

        def step(self, result, item):
            nonlocal pending
            pending.append(item)
            if len(pending) == size:
                batch = pending
                pending = []
                return self._reducer(result, batch)
            return result

        def terminate(self, result):
            return self._reducer(result, pending)

    return BatchingTransducer


def windowing(size, padding=UNSET):
    """Create a transducer which produces a moving window over items."""

    if size < 1:
        raise ValueError("windowing() size must be at least 1")

    window = deque(maxlen=size) if padding is UNSET else deque([padding] * size, maxlen=size)

    class WindowingTransducer(Transducer):

        def step(self, result, item):
            window.append(item)
            return self._reducer(result, list(window))

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
    last_seen = None

    class LastTransducer(Transducer):

        def step(self, result, item):
            nonlocal last_seen
            if predicate(item):
                last_seen = item
            return result

        def terminate(self, result):
            return last_seen

    return LastTransducer


def reversing():

    items = deque()

    class ReversingTransducer(Transducer):

        def step(self, result, item):
            items.appendleft(item)
            return result

        def terminate(self, result):
            return items

    return ReversingTransducer


def ordering(key=None, reverse=False):

    key = identity if key is None else key
    items = []

    class OrderingTransducer(Transducer):

        def step(self, result, item):
            items.append(item)
            return result

        def terminate(self, result):
            items.sort(key=key, reverse=reverse)
            return items

    return OrderingTransducer


def counting(predicate=None):

    predicate = true if predicate is None else predicate

    count = 0

    class CountingTransducer(Transducer):

        def step(self, result, item):
            nonlocal count
            if predicate(item):
                count += 1
            return result

        def terminate(self, result):
            return count

    return CountingTransducer


def grouping(key=None):

    key = identity if key is None else key

    groups = {}

    class GroupingTransducer(Transducer):

        def step(self, result, item):
            k = key(item)
            if k not in groups:
                groups[k] = []
            groups[k].append(item)
            return result

        def terminate(self, result):
            return groups

    return GroupingTransducer







