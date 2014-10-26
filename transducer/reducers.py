def sender(result, item):
    """A reducer for sending items to a coroutine.

    Args:
        result: A coroutine or sink.
        item: An item to send.
    """
    result.send(item)
    return result


def appender(result, item):
    """A reducer for appending to a list"""
    result.append(item)
    return result