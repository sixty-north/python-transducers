from collections import deque
from transducer.infrastructure import Reduced
from transducer.reducers import appending


# Transducible processes

def transduce(transducer, iterable):
    r = transducer(appending())
    accumulator = deque()
    reduced = False
    for item in iterable:
        accumulator = r.step(accumulator, item)
        if isinstance(accumulator, Reduced):
            accumulator = accumulator.value
            reduced = True

        yield from pending_in(accumulator)

        if reduced:
            break

    completed_result = r.complete(accumulator)
    assert completed_result is accumulator

    yield from pending_in(accumulator)


def pending_in(queue):
    while queue:
        yield queue.popleft()
