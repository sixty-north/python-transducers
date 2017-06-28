import unittest
from io import StringIO

from transducer.sinks import rprint, null_sink, CollectingSink, SingularSink


class TestNullSink(unittest.TestCase):

    def test_sent_items_are_sunk(self):
        sink = null_sink()
        for i in range(100):
            sink.send(100)
        sink.close()

    def test_closed_sink_raises_stop_iteration(self):
        sink = null_sink()
        sink.close()
        with self.assertRaises(StopIteration):
            sink.send(42)


class TestRPrint(unittest.TestCase):

    def test_sent_items_are_printed(self):
        with StringIO() as stream:
            sink = rprint(file=stream, flush=True)
            sink.send(10)
            sink.send(20)
            sink.send(30)
            result = stream.getvalue()
            self.assertEqual(result, "10\n20\n30")
            sink.close()

    def test_separators_are_printed(self):
        with StringIO() as stream:
            sink = rprint(sep=', ', file=stream, flush=True)
            sink.send(12)
            sink.send(24)
            sink.send(36)
            result = stream.getvalue()
            self.assertEqual(result, "12, 24, 36")
            sink.close()

    def test_end_terminator_is_printed(self):
        with StringIO() as stream:
            sink = rprint(end='END', file=stream, flush=True)
            sink.send(7)
            sink.send(14)
            sink.send(21)
            sink.close()
            result = stream.getvalue()
            self.assertEqual(result, "7\n14\n21END")

    def test_closed_sink_raises_stop_iteration(self):
        with StringIO() as stream:
            sink = rprint()
            sink.close()
            with self.assertRaises(StopIteration):
                sink.send("StopIteration should be raised")


class TestCollectingSink(unittest.TestCase):

    def test_no_items_is_empty(self):
        collection = CollectingSink()
        self.assertEqual(len(collection), 0)

    def test_send_single_item_has_len_one(self):
        collection = CollectingSink()
        sink = collection()
        sink.send(42)
        self.assertEqual(len(collection), 1)

    def test_send_single_item_is_retrievable(self):
        collection = CollectingSink()
        sink = collection()
        sink.send(64)
        result = list(collection)
        self.assertListEqual(result, [64])

    def test_multiple_items_are_retrievable(self):
        collection = CollectingSink()
        sink = collection()
        sink.send(64)
        sink.send(128)
        sink.send(256)
        result = list(collection)
        self.assertListEqual(result, [64, 128, 256])

    def test_three_items_added_two_dequeued(self):
        collection = CollectingSink()
        sink = collection()
        sink.send(64)
        sink.send(128)
        sink.send(256)
        i = iter(collection)
        next(i)
        next(i)
        self.assertEqual(len(collection), 1)

    def test_three_items_added_four_dequeued_raises_stop_iteration(self):
        collection = CollectingSink()
        sink = collection()
        sink.send(64)
        sink.send(128)
        sink.send(256)
        i = iter(collection)
        next(i)
        next(i)
        next(i)
        with self.assertRaises(StopIteration):
            next(i)

    def test_send_items_to_multiple_sinks(self):
        collection = CollectingSink()
        sink1 = collection()
        sink2 = collection()
        sink1.send(64)
        sink2.send(128)
        sink1.send(256)
        sink2.send(512)
        result = list(collection)
        self.assertListEqual(result, [64, 128, 256, 512])

    def test_send_items_then_clear_is_empty(self):
        collection = CollectingSink()
        sink = collection()
        sink.send(64)
        sink.send(128)
        sink.send(256)
        collection.clear()
        self.assertEqual(len(collection), 0)

    def test_closed_sink_raises_stop_iteration(self):
        collection = CollectingSink()
        sink = collection()
        sink.close()
        with self.assertRaises(StopIteration):
            sink.send(42)


class TestSingularSink(unittest.TestCase):

    def test_no_items_raises_runtime_error(self):
        singular_sink = SingularSink()
        sink = singular_sink()
        with self.assertRaises(RuntimeError):
            _ = singular_sink.value

    def test_one_sent_item_can_be_retrieved(self):
        singular_sink = SingularSink()
        sink = singular_sink()
        sink.send(496)
        self.assertEqual(singular_sink.value, 496)

    def test_two_items_sent_raises_stop_iteration(self):
        singular_sink = SingularSink()
        sink = singular_sink()
        sink.send(342)
        with self.assertRaises(StopIteration):
            sink.send(124)

    def test_closed_sink_raises_stop_iteration(self):
        singular_sink = SingularSink()
        sink = singular_sink()
        sink.close()
        with self.assertRaises(StopIteration):
            sink.send(42)

    def test_zero_sent_items_has_no_value(self):
        singular_sink = SingularSink()
        sink = singular_sink()
        self.assertFalse(singular_sink.has_value)

    def test_one_sent_item_has_value(self):
        singular_sink = SingularSink()
        sink = singular_sink()
        sink.send(78)
        self.assertTrue(singular_sink.has_value)