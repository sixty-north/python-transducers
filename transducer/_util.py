
#  A sentinel for indicating unset function arguments in places
#  where None would be a legitimate value.
UNSET = object()


def pending_in(queue):
    while queue:
        yield queue.popleft()


def coroutine(func):
    def start(*args, **kwargs):
        g = func(*args, **kwargs)
        next(g)
        return g
    return start