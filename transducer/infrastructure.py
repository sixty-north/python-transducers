"""Infrastructure for implementing transducers."""

from abc import ABCMeta


class Reduced:
    """A sentinel 'box' used to return the final value of a reduction."""

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value


class Reducer(metaclass=ABCMeta):
    """An Abstract Base Class for Reducers.
    """

    def __init__(self, reducer):
        self._reducer = reducer

    def __call__(self, result, item):
        """Transducers are callable, so they can be used as reducers."""
        return self.step(result, item)

    def initial(self):
        return self._reducer.initial()

    def step(self, result, item):
        """Reduce one item.

        Called once for each item. Overrides should invoke the callable self._reducer
        directly as self._reducer(...) rather than as self._reducer.step(...) so that
        any 2-arity reduction callable can be used.

        Args:
            result: The reduced result thus far.
            item: The new item to be combined with result to give the new result.

        Returns:
            The newly reduced result; that is, result combined in some way with
            item to produce a new result.  If reduction needs to be terminated,
            this method should return the sentinel Reduced(result).
        """
        return self._reducer(result, item)

    def complete(self, result):
        """Called at exactly once when reduction is complete.

        Called on completion of a transducible process.
        Consider overriding terminate() rather than this method for convenience.
        """
        result = self.terminate(result)

        try:
            return self._reducer.complete(result)
        except AttributeError:
            return result

    def terminate(self, result):
        """Optionally override to terminate the result."""
        return result


def reducer(initial):
    """A function decorator allowing easy specification of the initial value for reduction."""

    class ReducerWrapper(Reducer):
        """Convert simple reducer functions to support the reduction protocol."""

        def __init__(self, rdcr):
            super().__init__(rdcr)
            # TODO: Something clever with names and docstrings

        def initial(self):
            return initial

    return ReducerWrapper





