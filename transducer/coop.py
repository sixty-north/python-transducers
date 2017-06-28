from transducer._util import UNSET
from transducer.infrastructure import Reduced


# Transducible processes

async def transduce(transducer, reducer, aiterable, init=UNSET):
    r = transducer(reducer)
    accumulator = r.initial() if init is UNSET else init
    async for item in aiterable:
        accumulator = r.step(accumulator, item)
        if isinstance(accumulator, Reduced):
            accumulator = accumulator.value
            break
    return r.complete(accumulator)
