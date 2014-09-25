from functools import partial
import operator
import random
import sys
from time import sleep
from coroutine import coroutine
from chrono import now
from transducer import compose, mapping, filtering, taking, dropping_while, distinct, identity, pairwise, batching


@coroutine
def rmap(func, target):
    try:
        while True:
            event = (yield)
            result = func(event)
            target.send(result)
    except GeneratorExit:
        target.close()
        raise StopIteration


@coroutine
def rfilter(pred, target):
    try:
        while True:
            event = (yield)
            if pred(event):
                target.send(event)
    except GeneratorExit:
        target.close()
        raise StopIteration


@coroutine
def rreduce(func, target, initializer=None):
    try:
        accumulator = (yield) if initializer is None else initializer
        while True:
            accumulator = func(accumulator, (yield))
    except GeneratorExit:
        target.send(accumulator)
        target.close()
        raise StopIteration


@coroutine
def rprint(sep='\n', end=''):
    try:
        sys.stdout.write(str((yield)))
        while True:
            sys.stdout.write(sep)
            sys.stdout.write(str((yield)))
    except GeneratorExit:
        sys.stdout.write(end)
        raise StopIteration


class Only:
    _NOT_SET = object()

    def __init__(self):
        self._value = Only._NOT_SET

    def send(self, item):
        self._value = item

    @property
    def value(self):
        if self._value is Only._NOT_SET:
            raise ValueError("Only value not set")
        return self._value

    def close(self):
        return


def make_stream(iterable, target):
    for item in iterable:
        target.send(item)
    target.close()


def is_odd(x):
    return x % 2 != 0

@coroutine
def timestamp(target):
    try:
        while True:
            _ = (yield)
            target.send(now())
    except GeneratorExit:
        target.close()
        raise StopIteration


@coroutine
def timedelta(target):  # Generalise to moving window
    try:
        previous = (yield)
        while True:
            current = (yield)
            delta = current - previous
            target.send(delta)
            previous = current
    except GeneratorExit:
        target.close()
        raise StopIteration


def poisson_source(rate, event, target):
    while True:
        duration = random.expovariate(rate)
        sleep(duration)
        target.send(event(duration))


def sender(result, item):
    result.send(item)
    return result


def transduce(transducer, reducer, source, sink):
    source(rreduce(transducer(reducer), target=sink, initializer=sink))


def main2():
    transduce(transducer=compose(
                  mapping(lambda x: x > 0.5),
                  pairwise(),
                  filtering(lambda x: x[0]),
                  mapping(lambda x: x[1]),
                  batching(3)),
              reducer=sender,
              source=partial(poisson_source, 2.0, identity),
              sink=rprint())


def main():
    poisson_source(2.0, bool,
    timestamp(
    timedelta(
    rfilter(lambda d: d.microseconds < 100000,
    rprint(
    )))))

    #a = [1, 2, 5, 3, 1, 4, 6, 2, 3, 4, 5, 1, 2, 8]
    #only = Only()
    #make_stream(a,
    #            rfilter(is_odd,
    #            rreduce(operator.add, rprint())))
    #print(only.value)


class NullSink:

    def send(self, item):
        pass

    def close(self, item):
        pass


if __name__ == '__main__':
    main2()

