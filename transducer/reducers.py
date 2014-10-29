from transducer.infrastructure import reducer
from transducer.react import NullSink


@reducer(initial=NullSink)
def sender(result, item):
    """A reducer for sending items to a coroutine.

    Args:
        result: A coroutine or sink.
        item: An item to send.
    """
    result.send(item)
    return result


@reducer(initial=[])
def appender(result, item):
    """A reducer for appending to a mutable sequence"""
    result.append(item)
    return result