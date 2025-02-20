import unittest
from distributed_rest.events.baseevent import BaseEvent


class TestBaseEvent(unittest.TestCase):
    def setUp(self):
        self.event = BaseEvent()

    def test_subscribe(self):
        def handler():
            pass
        self.event.subscribe(handler)
        self.assertIn(handler, self.event._subscriptions)

    def test_unsubscribe(self):
        def handler():
            pass
        self.event.subscribe(handler)
        self.event.unsubscribe(handler)
        self.assertNotIn(handler, self.event._subscriptions)

    def test_fire(self):
        self.handler_called = False

        def handler():
            self.handler_called = True

        self.event.subscribe(handler)
        self.event._fire()
        self.assertTrue(self.handler_called)

if __name__ == '__main__':
    unittest.main()