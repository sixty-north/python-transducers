import random
from time import sleep


def iterable_source(iterable, target):
    """Convert an iterable into a stream of events."""
    result = None
    for item in iterable:
        try:
            target.send(item)
        except StopIteration as e:
            result = e.value
            break
    return result


def poisson_source(rate, iterable, target):
    """Send events at random times with uniform probability.

    Args:
        rate: The average number of events to send per second
        iterable: A series of items which will be sent to the target one by one.
        target: The target coroutine or sink.

    Returns:
        The completed value or None if iterable was exhausted and the target was closed.
    """
    for item in iterable:
        duration = random.expovariate(rate)
        sleep(duration)
        try:
            target.send(item)
        except StopIteration as e:
            return e.value
    return None
