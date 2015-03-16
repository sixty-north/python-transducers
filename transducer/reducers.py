from transducer.infrastructure import Reducer


class Appending(Reducer):

    def initial(self):
        return []

    def step(self, result, item):
        result.append(item)
        return result

_appending = Appending()


def appending():
    return _appending


class Conjoining(Reducer):

    def initial(self):
        return tuple()

    def step(self, result, item):
        return result + type(result)((item,))

_conjoining = Conjoining()


def conjoining():
    return _conjoining


class ExpectingSingle(Reducer):

    def __init__(self):
        self._num_steps = 0

    def initial(self):
        return None

    def step(self, result, item):
        assert result is None
        self._num_steps += 1
        if self._num_steps > 1:
            raise RuntimeError("Too many steps!")
        return item

    def complete(self, result):
        if self._num_steps < 1:
            raise RuntimeError("Too few steps!")
        return result


def expecting_single():
    return ExpectingSingle()


class Sending(Reducer):

    class NullSink:
        """The /dev/null of coroutine sinks."""

        def send(self, item):
            pass

        def close(self):
            pass

    def initial(self):
        return Sending.NullSink()

    def step(self, result, item):
        try:
            result.send(item)
        except StopIteration:
            pass  # TODO: What is the correct course of action here?
        return result

_sending = Sending()


def sending():
    return _sending
