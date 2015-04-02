from multiprocessing.pool import Pool
from transducer._util import UNSET
from transducer.infrastructure import Reduced, Transducer
import transducer.eager as eager


# Transducible processes
from transducer.reducers import appending
from transducer.transducers import geometric_partitioning


def transduce(transducer, series_reducer, iterable, parallel_reducer=None, init=UNSET):
    if parallel_reducer is None:
        parallel_reducer = series_reducer

    partitions = eager.transduce(transducer=geometric_partitioning(),
                                 reducer=appending(),
                                 iterable=iterable)

    r = transducer(series_reducer)

    pool = Pool()
    args = [(r, p, r.initial() if init is UNSET else init) for p in partitions]

    reduced_partitions = pool.starmap(series_transduce, args)

    combined_result = eager.transduce(transducer=Transducer,  # The identity transducer
                                      reducer=parallel_reducer,
                                      iterable=reduced_partitions)

    return r.complete(combined_result)


def series_transduce(reducer, iterable, accumulator):
    for item in iterable:
        accumulator = reducer.step(accumulator, item)
        if isinstance(accumulator, Reduced):
            accumulator = accumulator.value
            break
    return accumulator
