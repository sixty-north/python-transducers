from collections import deque
from transducer.infrastructure import Reduced
from transducer.reducers import appender


# Transducible processes

def transduce(transducer, iterable):
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