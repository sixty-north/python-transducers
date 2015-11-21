"""Functions for creating transducers.

The functions in this module return transducers.
"""
from collections import deque
from functools import reduce

from transducer._util import UNSET
from transducer.functional import true
from transducer.infrastructure import Reduced, Transducer


# Functions for creating transducers, which are themselves
# functions which transform one reducer to another

# ---------------------------------------------------------------------

class Mapping(Transducer):

    def __init__(self, reducer, transform):
        super().__init__(reducer)
        self._transform = transform

    def step(self, result, item):
        return self._reducer(result, self._transform(item))


def mapping(transform):
    """Create a mapping transducer with the given transform.

    Args:
        transform: A single-argument function which will be applied to
            each input element to produce the corresponding output
            element.

    Returns: A mapping transducer: A single argument function which,
        when passed a reducing function, returns a new reducing function
        which applies the specified mapping transform function *before*
        delegating to the original reducer.
    """

    def mapping_transducer(reducer):
        return Mapping(reducer, transform)

    return mapping_transducer

# ---------------------------------------------------------------------


class Filtering(Transducer):

    def __init__(self, reducer, predicate):
        super().__init__(reducer)
        self._predicate = predicate

    def step(self, result, item):
        return self._reducer(result, item) if self._predicate(item) else result


def filtering(predicate):
    """Create a filtering transducer with the given predicate.

    Args:
        predicate: A single-argument function which will be used to
            test each element and which must return True or False. Only
            those elements for which this function returns True will be
            retained.

    Returns: A filtering transducer: A single argument function which,
        when passed a reducing function, returns a new reducing function
        which passes only those items in the input stream which match
        satisfy the predicate to the original reducer.
    """

    def filtering_transducer(reducer):
        return Filtering(reducer, predicate)

    return filtering_transducer


# ---------------------------------------------------------------------

class Reducing(Transducer):

    def __init__(self, reducer, reducer2, init=UNSET):
        super().__init__(reducer)
        self._reducer2 = reducer2
        self._accumulator = init  # TODO: Should we try to call reducer2.initial() here?

    def step(self, result, item):
        self._accumulator = item if self._accumulator is UNSET else self._reducer2(self._accumulator, item)
        return result

    def complete(self, result):
        result = self._reducer.step(result, self._accumulator)
        return self._reducer.complete(result)


def reducing(reducer, init=UNSET):
    """Create a reducing transducer with the given reducer.

    Args:
        reducer: A two-argument function which will be used to combine the
            partial cumulative result in the first argument with the next
            item from the input stream in the second argument.

    Returns: A reducing transducer: A single argument function which,
        when passed a reducing function, returns a new reducing function
        which entirely reduces the input stream using 'reducer' before
        passing the result to the reducing function passed to the
        transducer.
    """

    reducer2 = reducer

    def reducing_transducer(reducer):
        return Reducing(reducer, reducer2, init)

    return reducing_transducer

# ---------------------------------------------------------------------


class Scanning(Transducer):

    def __init__(self, reducer, reducer2, init=UNSET):
        super().__init__(reducer)
        self._reducer2 = reducer2
        self._accumulator = init  # TODO: Should we try to call reducer2.initial() here?

    def step(self, result, item):
        self._accumulator = item if self._accumulator is UNSET else self._reducer2(self._accumulator, item)
        return self._reducer.step(result, self._accumulator)


def scanning(reducer, init=UNSET):
    """Create a scanning reducer."""

    reducer2 = reducer

    def scanning_transducer(reducer):
        return Scanning(reducer, reducer2, init)

    return scanning_transducer


# ---------------------------------------------------------------------


class Enumerating(Transducer):

    def __init__(self, reducer, start):
        super().__init__(reducer)
        self._counter = start

    def step(self, result, item):
        index = self._counter
        self._counter += 1
        return self._reducer(result, (index, item))


def enumerating(start=0):
    """Create a transducer which enumerates items."""

    def enumerating_transducer(reducer):
        return Enumerating(reducer, start)

    return enumerating_transducer

# ---------------------------------------------------------------------


class Mapcatting(Transducer):

    def __init__(self, reducer, transform):
        super().__init__(reducer)
        self._transform = transform

    def step(self, result, item):
        return reduce(self._reducer, self._transform(item), result)


def mapcatting(transform):
    """Create a transducer which transforms items and concatenates the results"""

    def mapcatting_transducer(reducer):
        return Mapcatting(reducer, transform)

    return mapcatting_transducer

# ---------------------------------------------------------------------


class Taking(Transducer):

    def __init__(self, reducer, n):
        super().__init__(reducer)
        self._counter = 0
        self._n = n

    def step(self, result, item):
        self._counter += 1
        result = self._reducer(result, item)
        return Reduced(result) if self._counter >= self._n else result


def taking(n):
    """Create a transducer which takes the first n items"""

    if n < 0:
        raise ValueError("Cannot take fewer than zero ({}) items".format(n))

    def taking_transducer(reducer):
        return Taking(reducer, n)

    return taking_transducer

# ---------------------------------------------------------------------


class TakingWhile(Transducer):

    def __init__(self, reducer, predicate):
        super().__init__(reducer)
        self._predicate = predicate

    def step(self, result, item):
        return self._reducer(result, item) if self._predicate(item) else Reduced(result)


def taking_while(predicate):
    """Create a transducer which takes leading items while they satisfy a predicate."""

    def taking_while_transducer(reducer):
        return TakingWhile(reducer, predicate)

    return taking_while_transducer

# ---------------------------------------------------------------------


class Dropping(Transducer):

    def __init__(self, reducer, n):
        super().__init__(reducer)
        self._counter = 0
        self._n = n

    def step(self, result, item):
        result = result if self._counter < self._n else self._reducer(result, item)
        self._counter += 1
        return result


def dropping(n):
    """Create a transducer which drops the first n items"""

    if n < 0:
        raise ValueError("Cannot drop fewer than zero ({}) items".format(n))

    def dropping_transducer(reducer):
        return Dropping(reducer, n)

    return dropping_transducer


class DroppingWhile(Transducer):

    def __init__(self, reducer, predicate):
        super().__init__(reducer)
        self._predicate = predicate
        self._dropping = True

    def step(self, result, item):
        self._dropping = self._dropping and self._predicate(item)
        return result if self._dropping else self._reducer(result, item)


def dropping_while(predicate):
    """Create a transducer which drops leading items while a predicate holds."""

    def dropping_while_transducer(reducer):
        return DroppingWhile(reducer, predicate)

    return dropping_while_transducer

# ---------------------------------------------------------------------


class Distinct(Transducer):

    def __init__(self, reducer):
        super().__init__(reducer)
        self._seen = set()

    def step(self, result, item):
        if item not in self._seen:
            self._seen.add(item)
            return self._reducer(result, item)
        return result


def distinct():
    """Create a transducer which filters distinct items"""

    def distinct_transducer(reducer):
        return Distinct(reducer)

    return distinct_transducer

# ---------------------------------------------------------------------


class Pairwise(Transducer):

    def __init__(self, reducer):
        super().__init__(reducer)
        self._previous_item = UNSET

    def step(self, result, item):
        if self._previous_item is UNSET:
            self._previous_item = item
            return result
        pair = (self._previous_item, item)
        self._previous_item = item
        return self._reducer.step(result, pair)


def pairwise():
    """Create a transducer which produces successive pairs"""

    def pairwise_transducer(reducer):
        return Pairwise(reducer)

    return pairwise_transducer

# ---------------------------------------------------------------------


class Batching(Transducer):

    def __init__(self, reducer, size):
        super().__init__(reducer)
        self._size = size
        self._pending = []

    def step(self, result, item):
        self._pending.append(item)
        if len(self._pending) == self._size:
            batch = self._pending
            self._pending = []
            return self._reducer(result, batch)
        return result

    def complete(self, result):
        r = self._reducer.step(result, self._pending) if len(self._pending) > 0 else result
        return self._reducer.complete(r)


def batching(size):
    """Create a transducer which produces non-overlapping batches."""

    if size < 1:
        raise ValueError("batching() size must be at least 1")

    def batching_transducer(reducer):
        return Batching(reducer, size)

    return batching_transducer

# ---------------------------------------------------------------------


class Windowing(Transducer):

    def __init__(self, reducer, size, padding, window_type):
        super().__init__(reducer)
        self._size = size
        self._padding = padding
        self._window = deque(maxlen=size) if padding is UNSET else deque([padding] * size, maxlen=size)
        self._window_type = window_type

    def step(self, result, item):
        self._window.append(item)
        return self._reducer.step(result, self._window_type(self._window))

    def complete(self, result):
        if self._padding is not UNSET:
            for _ in range(self._size - 1):
                result = self.step(result, self._padding)
        else:
            while len(self._window) > 1:
                self._window.popleft()
                result = self._reducer.step(result, self._window_type(self._window))
        return self._reducer.complete(result)


def windowing(size, padding=UNSET, window_type=tuple):
    """Create a transducer which produces a moving window over items."""

    if size < 1:
        raise ValueError("windowing() size {} is not at least 1".format(size))

    def windowing_transducer(reducer):
        return Windowing(reducer, size, padding, window_type)

    return windowing_transducer

# ---------------------------------------------------------------------


class First(Transducer):

    def __init__(self, reducer, predicate):
        super().__init__(reducer)
        self._predicate = predicate

    def step(self, result, item):
        return Reduced(self._reducer.step(result, item)) if self._predicate(item) else result


def first(predicate=None):
    """Create a transducer which obtains the first item, then terminates."""

    predicate = true if predicate is None else predicate

    def first_transducer(reducer):
        return First(reducer, predicate)

    return first_transducer

# ---------------------------------------------------------------------


class Last(Transducer):

    def __init__(self, reducer, predicate):
        super().__init__(reducer)
        self._predicate = predicate
        self._last_seen = UNSET

    def step(self, result, item):
        if self._predicate(item):
            self._last_seen = item
        return result

    def complete(self, result):
        if self._last_seen is not UNSET:
            result = self._reducer.step(result, self._last_seen)
        return self._reducer.complete(result)


def last(predicate=None):
    """Create a transducer which obtains the last item."""

    predicate = true if predicate is None else predicate

    def last_transducer(reducer):
        return Last(reducer, predicate)

    return last_transducer

# ---------------------------------------------------------------------


class ElementAt(Transducer):

    def __init__(self, reducer, index):
        super().__init__(reducer)
        self._index = index
        self._counter = -1

    def step(self, result, item):
        self._counter += 1
        if self._counter == self._index:
            return Reduced(self._reducer.step(result, item))
        return result

    def complete(self, result):
        if self._counter < self._index:
            raise IndexError("Too few elements in series of length {} "
                             "to find element at index {}".format(self._counter, self._index))
        return result


def element_at(index):
    """Create a transducer which obtains the item at the specified index."""

    if index < 0:
        raise IndexError("element_at used with illegal index {}".format(index))

    def element_at_transducer(reducer):
        return ElementAt(reducer, index)

    return element_at_transducer

# ---------------------------------------------------------------------


class Repeating(Transducer):

    def __init__(self, reducer, num_times):
        super().__init__(reducer)
        self._num_times = num_times

    def step(self, result, item):
        for i in range(self._num_times):
            result = self._reducer.step(result, item)
        return result


def repeating(num_times):

    if num_times < 0:
        raise ValueError("num_times value {} is not non-negative".format(num_times))

    def repeating_transducer(reducer):
        return Repeating(reducer, num_times)

    return repeating_transducer

# ---------------------------------------------------------------------


class Reversing(Transducer):

    def __init__(self, reducer):
        super().__init__(reducer)
        self._items = deque()

    def step(self, result, item):
        self._items.appendleft(item)
        return result

    def complete(self, result):
        for item in self._items:
            result = self._reducer.step(result, item)

        self._items.clear()

        return self._reducer.complete(result)


def reversing():

    def reversing_transducer(reducer):
        return Reversing(reducer)

    return reversing_transducer

# ---------------------------------------------------------------------


class Ordering(Transducer):

    def __init__(self, reducer, key, reverse):
        super().__init__(reducer)
        self._key = key
        self._reverse = reverse
        self._items = []

    def step(self, result, item):
        self._items.append(item)
        return result

    def complete(self, result):
        self._items.sort(key=self._key, reverse=self._reverse)

        for item in self._items:
            result = self._reducer.step(result, item)

        self._items.clear()

        return self._reducer.complete(result)


def ordering(key=None, reverse=False):

    def ordering_transducer(reducer):
        return Ordering(reducer, key, reverse)

    return ordering_transducer

# ---------------------------------------------------------------------


class Counting(Transducer):

    def __init__(self, reducer, predicate):
        super().__init__(reducer)
        self._predicate = predicate
        self._count = 0

    def step(self, result, item):
        if self._predicate(item):
            self._count += 1
        return result

    def complete(self, result):
        result = self._reducer.step(result, self._count)
        return self._reducer.complete(result)


def counting(predicate=None):

    predicate = true if predicate is None else predicate

    def counting_transducer(reducer):
        return Counting(reducer, predicate)

    return counting_transducer
