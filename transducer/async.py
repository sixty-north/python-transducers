import asyncio
from transducer._util import UNSET
from transducer.infrastructure import Reduced


@asyncio.coroutine
def transduce(transducer, reducer, iterable, init=UNSET):
    r = transducer(reducer)
    accumulator = r.initial() if init is UNSET else init
    for item in iterable:
        accumulator = r.step(accumulator, item)
        if isinstance(accumulator, Reduced):
            accumulator = accumulator.value
            break
        yield  # Yield to the event-loop once per step
    return r.complete(accumulator)
