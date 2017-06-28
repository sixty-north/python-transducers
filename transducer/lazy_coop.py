from collections import deque

from transducer.infrastructure import Reduced
from transducer.reducers import appending


# Transducible processes

async def transduce(transducer, aiterable):
    r = transducer(appending())
    accumulator = deque()
    reduced = False
    async for item in aiterable:
        accumulator = r.step(accumulator, item)
        if isinstance(accumulator, Reduced):
            accumulator = accumulator.value
            reduced = True

        while accumulator:
            yield accumulator.popleft()

        if reduced:
            break

    completed_result = r.complete(accumulator)
    assert completed_result is accumulator

    while accumulator:
        yield accumulator.popleft()
