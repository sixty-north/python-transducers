from functools import reduce
from itertools import chain


def compose(f, *fs):
    """Compose functions right to left.

    compose(f, g, h)(x) -> f(g(h(x)))

    Args:
        f, *fs: The head and rest of a sequence of callables. The
                rightmost function passed can accept any arguments and
                the returned function will have the same signature as
                this last provided function.  All preceding functions
                must be unary.

    Returns:
        The composition of the argument functions. The returned
        function will accept the same arguments as the rightmost
        passed in function.
    """
    rfs = list(chain([f], fs))
    rfs.reverse()

    def composed(*args, **kwargs):
        return reduce(
            lambda result, fn: fn(result),
            rfs[1:],
            rfs[0](*args, **kwargs))

    return composed


def identity(x):
    return x


def true(*args, **kwargs):
    return True


def false(*args, **kwargs):
    return False