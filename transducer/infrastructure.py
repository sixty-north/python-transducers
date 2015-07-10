"""Infrastructure for implementing transducers."""

from abc import ABCMeta, abstractmethod


class Reduced:
    """A sentinel 'box' used to return the final value of a reduction.

    Wrapping a value in a Reduced instance is idempotent, so
    Reduced(Reduced(item)) is equivalent to Reduced(item)
    """

    def __new__(cls, value):
        if isinstance(value, cls):
            return value
        obj = super().__new__(cls)
        obj._value = value
        return obj

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self._value)


class Reducer(object, metaclass=ABCMeta):

    @abstractmethod
    def initial(self):
        raise NotImplementedError

    @abstractmethod
    def step(self, result, item):
        raise NotImplementedError

    def complete(self, result):
        return result

    def __call__(self, result, item):
        """Reducing objects are callable so they can be used like functions."""
        return self.step(result, item)


class Transducer(Reducer):
    """An Base Class for Transducers which also serves as the identity transducer.
    """

    def __init__(self, reducer):
        self._reducer = reducer

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

        Called on completion of a transducible process. The default implementation calls complete()
        on the underlying reducer, which should be done to meet the requirements of the transducer
        contract.  Overrides of this method are the right place to deal with any pending state or
        perform with other clean-up actions.

        Args:
            result: The result prior to completion.

        Returns:
            The completed result.
        """
        return self._reducer.complete(result)
