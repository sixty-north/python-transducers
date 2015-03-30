import random
from time import sleep
from transducer._util import empty_iter, prepend


def iterable_source(iterable, target):
    """Convert an iterable into a stream of events.

    Args:
        iterable: A series of items which will be sent to the target one by one.
        target: The target coroutine or sink.

    Returns:
        An iterator over any remaining items.
    """
    it = iter(iterable)
    for item in it:
        try:
            target.send(item)
        except StopIteration:
            return prepend(item, it)
    return empty_iter()


def poisson_source(rate, iterable, target):
    """Send events at random times with uniform probability.

    Args:
        rate: The average number of events to send per second.
        iterable: A series of items which will be sent to the target one by one.
        target: The target coroutine or sink.

    Returns:
        An iterator over any remaining items.
    """
    if rate <= 0.0:
        raise ValueError("poisson_source rate {} is not positive".format(rate))

    it = iter(iterable)
    for item in it:
        duration = random.expovariate(rate)
        sleep(duration)
        try:
            target.send(item)
        except StopIteration:
            return prepend(item, it)
    return empty_iter()
