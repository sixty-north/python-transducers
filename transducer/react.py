from collections import deque
import random
import sys
from time import sleep

from transducer._util import UNSET
from transducer.infrastructure import Reduced
from transducer.reducers import sending


# Coroutine infrastructure

def coroutine(func):
    def start(*args, **kwargs):
        g = func(*args, **kwargs)
        next(g)
        return g
    return start


# Sinks

@coroutine
def rprint(sep='\n', end=''):
    """A coroutine sink which prints received items stdout

    Args:
        sep: Optional separator to be printed between received items.
        end: Optional terminator to be printed after the last item.
    """
    try:
        sys.stdout.write(str((yield)))
        while True:
            sys.stdout.write(sep)
            sys.stdout.write(str((yield)))
    except GeneratorExit:
        sys.stdout.write(end)
        raise StopIteration


class NullSink:
    """The /dev/null of coroutine sinks."""

    def send(self, item):
        pass

    def close(self):
        pass


class IterableSink:

    def __init__(self):
        self._items = deque()

    def send(self, item):
        self._items.append(item)

    def close(self):
        pass

    def __iter__(self):
        while len(self._items) > 0:
            yield self._items.popleft()


class SingularSink:

    def __init__(self):
        self._item = UNSET

    def send(self, item):
        if self._item is not UNSET:
            raise RuntimeError("SingularSink sent more than one item {!r}".format(item))
        self._item = item

    def close(self):
        pass

    def value(self):
        return self._item


# Sources

def iterable_source(iterable, target):
    """Convert an iterable into a stream of events."""
    result = None
    for item in iterable:
        try:
            target.send(item)
        except StopIteration as e:
            result = e.value
            break
    target.close()
    return result


def poisson_source(rate, event, target):
    """Send events at random times with uniform probability.

    Args:
        rate: The average number of events to send per second
        event: A function or type used to construct the item to send from a
            float duration.
        target: The target coroutine or sink.

    Returns:
        The completed value.
    """
    while True:
        duration = random.expovariate(rate)
        sleep(duration)
        try:
            target.send(event(duration))
        except StopIteration as e:
            return e.value


# A reactive reduce co-routine. We can build everything else in terms of reduce

@coroutine
def rreduce(reducer, target):
    """Reduce for coroutines.

    Args:
        reducer: The reducing object, which should support the initial(), step()
            and complete() methods.

        target: The coroutine or sink to which results will be sent.

    """
    accumulator = target
    try:
        while True:

            accumulator = reducer.step(accumulator, (yield))
            if isinstance(accumulator, Reduced):
                accumulator = accumulator.value
                break
    except GeneratorExit:
        pass

    result = reducer.complete(accumulator)
    target.close()
    return result

# Transducible processes


def transduce(transducer, source, sink):
    return source(rreduce(reducer=transducer(sending()),
                          target=sink))
