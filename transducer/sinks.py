from collections.abc import Iterable, Sized
from collections import deque
import sys
from transducer._util import coroutine, pending_in, UNSET


@coroutine
def null_sink():
    while True:
        _ = (yield)


@coroutine
def rprint(sep='\n', end='\n', file=sys.stdout, flush=False):
    """A coroutine sink which prints received items stdout

    Args:
        sep: Optional separator to be printed between received items.
        end: Optional terminator to be printed after the last item.
        file: Optional stream to which to print.
        flush: Optional flag to force flushing after each item.
    """
    try:
        first_item = (yield)
        file.write(str(first_item))
        if flush:
            file.flush()
        while True:
            item = (yield)
            file.write(sep)
            file.write(str(item))
            if flush:
                file.flush()
    except GeneratorExit:
        file.write(end)
        if flush:
            file.flush()


class CollectingSink(Iterable, Sized):
    """Usage:

        sink = CollectingSink()

        # Do something to send items into the sink
        some_source(target=sink())

        for item in sink:
            print(item)
    """

    def __init__(self, maxlen=None):
        self._items = deque(maxlen=maxlen)

    @coroutine
    def __call__(self):
        while True:
            item = (yield)
            self._items.append(item)

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        yield from pending_in(self._items)

    def clear(self):
        self._items.clear()


class SingularSink:

    def __init__(self):
        self._item = UNSET

    @coroutine
    def __call__(self):
        while True:
            item = (yield)
            if self._item is not UNSET:
                break
            self._item = item

    @property
    def value(self):
        if self._item is UNSET:
            raise RuntimeError("Singular sink sent too few items.")
        return self._item

    @property
    def has_value(self):
        return self._item is not UNSET
