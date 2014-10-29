from transducer._util import UNSET
from transducer.infrastructure import Reduced


# Transducible processes

def transduce(transducer, reducer, iterable, init=UNSET):
    if init is UNSET:
        return transduce(transducer, reducer, iterable, init=reducer.initial())
    r = transducer(reducer)
    accumulator = init
    for item in iterable:
        accumulator = r.step(accumulator, item)
        if isinstance(accumulator, Reduced):
            accumulator = accumulator.value
            break
    return r.complete(accumulator)