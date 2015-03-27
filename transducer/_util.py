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