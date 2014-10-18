from transducers.transducer import _UNSET, Reduced


# Transducible processes

def transduce(transducer, reducer, iterable, init=_UNSET):
    r = transducer(reducer)
    accumulator = r.inital() if init is _UNSET else init
    for item in iterable:
        accumulator = r.step(accumulator, item)
        if isinstance(accumulator, Reduced):
            accumulator = accumulator.value
            break
    return r.complete(accumulator)