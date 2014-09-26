"""Transducers in Python

http://blog.cognitect.com/blog/2014/8/6/transducers-are-coming
"""
from abc import abstractmethod, ABCMeta
from collections import deque

from functools import reduce


def compose(*fs):
    """Compose functions right to left.

    compose(f, g, h)(x) -> f(g(h(x)))

    Args:
        *fs: The rightmost function passed can accept any arguments and
            the returned function will have the same signature as
            this last provided function.  All preceding functions
            must be unary.

    Returns:
        The composition of the argument functions. The returned
        function will accept the same arguments as the rightmost
        passed in function.
    """
    if len(fs) < 1:
        raise TypeError("Cannot compose fewer than one functions")
    rfs = list(reversed(fs))

    def composed(*args, **kwargs):
        i = iter(rfs)
        f0 = next(i)
        result = f0(*args, **kwargs)
        for fn in i:
            result = fn(result)
        return result

    return composed


def identity(x):
    return x


# Example reducers

def appender(result, item):
    """A reducer for appending to a list"""
    result.append(item)
    return result


# Transducer infrastructure

_UNSET = object()


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
        if not callable(reducer):
            raise TypeError("Transducer callable {!r} is not callable".format(reducer))
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
    previous_item = _UNSET

    class PairwiseTransducer(Transducer):

        def step(self, result, item):
            nonlocal previous_item
            if previous_item is _UNSET:
                previous_item = item
                return result
            pair = (previous_item, item)
            previous_item = item
            return self._reducer(result, pair)

    return PairwiseTransducer


def batching(size):
    """Create a transducer which produced non-overlapping batches."""

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


def windowing(size, padding=_UNSET):
    """Create a transducer which produces a moving window over items."""

    if size < 1:
        raise ValueError("windowing() size must be at least 1")

    window = deque(maxlen=size) if padding is _UNSET else deque([padding] * size, maxlen=size)

    class WindowingTransducer(Transducer):

        def step(self, result, item):
            window.append(item)
            return self._reducer(result, list(window))

        def terminate(self, result):
            for _ in range(size - 1):
                result = self.step(result, padding)
            return result

    return WindowingTransducer


def first():
    """Create a transducer which obtains the first item, then terminates."""

    class FirstTransducer(Transducer):

        def step(self, result, item):
            return Reduced(item)

    return FirstTransducer

# Transducible processes

def transduce(transducer, reducer, iterable, init=_UNSET):
    r = transducer(reducer)
    accumulator = r.inital() if init is _UNSET else init
    for item in iterable:
        accumulator = r.step(accumulator, item)
        if isinstance(accumulator, Reduced):
            accumulator = accumulator.value
            break
    return r.complete(accumulator)


def generate(transducer, iterable):
    """Lazy application of a transducer to an iterable."""
    r = transducer(appender)
    pending = deque()
    accumulator = pending
    reduced = False
    for item in iterable:
        accumulator = r.step(accumulator, item)
        if isinstance(accumulator, Reduced):
            accumulator = accumulator.value
            reduced = True

        while len(pending) > 0:
            p = pending.popleft()
            yield p

        if reduced:
            break

    r.complete(accumulator)

    while len(pending) > 0:
        p = pending.popleft()
        yield p


# Functions to exercise the above


def test_windowing():
    r = transduce(transducer=windowing(3, padding=None),
                  reducer=appender,
                  iterable=range(20),
                  init=[])
    print(r)


def test_lazy():
    r = generate(transducer=compose(
                                 mapping(lambda x: x*x),
                                 filtering(lambda x: x % 5 != 0),
                                 taking(6),
                                 dropping_while(lambda x: x < 15),
                                 distinct()),
                  iterable=range(20))
    print(list(r))

def test_transduce():
    r = transduce(transducer=compose(
                                 mapping(lambda x: x*x),
                                 filtering(lambda x: x % 5 != 0),
                                 taking(6),
                                 dropping_while(lambda x: x < 15),
                                 distinct()),
                  reducer=appender,
                  iterable=range(20),
                  init=[])
    print(r)

if __name__ == '__main__':
    test_windowing()
