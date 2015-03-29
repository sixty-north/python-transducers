from transducer._util import UNSET, coroutine
from transducer.infrastructure import Reduced
from transducer.reducers import sending

@coroutine
def transduce(transducer, target=UNSET):
    reducer = transducer(sending())
    accumulator = target if target is not UNSET else reducer.initial()
    try:
        while True:
            item = (yield)
            accumulator = reducer.step(accumulator, item)
            if isinstance(accumulator, Reduced):
                accumulator = accumulator.value
                break
            assert accumulator is target
    except GeneratorExit:
        pass
    assert accumulator is target
    return reducer.complete(accumulator)
