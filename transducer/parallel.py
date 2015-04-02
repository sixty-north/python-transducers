from contextlib import closing
from functools import reduce
from multiprocessing.pool import Pool
from transducer._util import UNSET, null_context_manager
from transducer.infrastructure import Reduced
import transducer.eager as eager


# Transducible processes
from transducer.reducers import appending
from transducer.transducers import geometric_partitioning


def transduce(transducer, reducer, iterable, init=UNSET, pool=None):

    r = transducer(reducer)

    def make_initial():
        return r.initial() if init is UNSET else init

    if r.combine(make_initial(), make_initial()) is NotImplemented:
        raise TypeError("transducer(reducer) cannot be parallelized.")

    partitions = eager.transduce(transducer=geometric_partitioning(),
                                 reducer=appending(),
                                 iterable=iterable)

    def make_pool():
        return Pool() if (pool is None) else pool

    manager = null_context_manager if (pool is not None) else closing

    with manager(make_pool()) as pool:
        args = [(r, p, make_initial()) for p in partitions]
        reduced_partitions = pool.starmap(series_transduce, args)
        combined_result = reduce(r.combine, reduced_partitions, make_initial())
        return r.complete(combined_result)


def series_transduce(reducer, iterable, accumulator):
    for item in iterable:
        accumulator = reducer.step(accumulator, item)
        if isinstance(accumulator, Reduced):
            accumulator = accumulator.value
            break
    return accumulator
