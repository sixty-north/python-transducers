from functools import wraps


#  A sentinel for indicating unset function arguments in places
#  where None would be a legitimate value.
UNSET = object()


def pending_in(queue):
    """Yield items from the left of a queue.
    """
    while queue:
        yield queue.popleft()


def coroutine(func):
    """Decorator for priming generator-based coroutines.
    """
    @wraps(func)
    def start(*args, **kwargs):
        g = func(*args, **kwargs)
        next(g)
        return g

    return start


def prepend(item, iterable):
    yield item
    yield from iterable


_EMPTY = tuple()


def empty_iter():
    return iter(_EMPTY)


def iterator_or_none(iterator):
    try:
        first = next(iterator)
    except StopIteration:
        return None
    return prepend(first, iterator)
