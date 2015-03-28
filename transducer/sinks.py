from collections import deque
import sys
from transducer._util import coroutine, pending_in, UNSET


@coroutine
def null_sink():
    while True:
        _ = (yield)


@coroutine
def rprint(sep='\n', end=''):
    """A coroutine sink which prints received items stdout

    Args:
        sep: Optional separator to be printed between received items.
        end: Optional terminator to be printed after the last item.
    """
    try:
        first_item = (yield)
        sys.stdout.write(str(first_item))
        sys.stdout.flush()
        while True:
            item = (yield)
            sys.stdout.write(sep)
            sys.stdout.write(str((item)))
            sys.stdout.flush()
    except GeneratorExit:
        sys.stdout.write(end)
        sys.stdout.flush()


class CollectingSink:
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

    def __iter__(self):
        yield from pending_in(self._items)


class SingularSink:

    def __init__(self):
        self._item = UNSET

    @coroutine
    def __call__(self):
        item = (yield)
        if self._item is not UNSET:
            raise RuntimeError("SingularSink sent more than one item {!r}".format(item))
        self._item = item

    @property
    def value(self):
        return self._item
