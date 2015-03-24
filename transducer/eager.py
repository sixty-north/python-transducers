from transducer._util import UNSET
from transducer.infrastructure import Reduced


# Transducible processes

def transduce(transducer, reducer, iterable, init=UNSET):
    r = transducer(reducer)
    accumulator = r.initial() if init is UNSET else init
    for item in iterable:
        accumulator = r.step(accumulator, item)
        if isinstance(accumulator, Reduced):
            accumulator = accumulator.value
            break
    return r.complete(accumulator)
