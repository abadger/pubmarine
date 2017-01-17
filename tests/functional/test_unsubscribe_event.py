import asyncio

import pytest

from pubmarine import PubPen


@pytest.fixture
def pubpen(request, event_loop):
    pubpen = PubPen(event_loop)
    return pubpen


class Function:
    def __init__(self):
        self.called = 0

    def __call__(self, *args):
        self.called += 1


@pytest.fixture
def function1(request):
    request.cls.function1 = Function()


@pytest.fixture
def function2(request):
    request.cls.function2 = Function()


@pytest.mark.usefixtures('function1', 'function2')
class TestFunctionalUnsubscribe:

    def test_no_callbacks_made(self, pubpen):
        """
        Subscribe to an event then unsubscribe.

        No callbacks are called no matter how many times the event is emitted
        """
        first = pubpen.subscribe('test_event', self.function1)
        pubpen.unsubscribe(first)
        assert self.function1.called == 0

        for iteration in range(1, 3):
            pubpen.emit('test_event')
            pending = asyncio.Task.all_tasks(loop=pubpen.loop)
            pubpen.loop.run_until_complete(asyncio.gather(*pending, loop=pubpen.loop))
            assert self.function1.called == 0

    def test_no_further_callbacks_made(self, pubpen):
        """
        Subscribe to an event emit event once, then unsubscribe.

        Callback is called for the first event but not for any further events
        """
        first = pubpen.subscribe('test_event', self.function1)
        assert self.function1.called == 0
        pubpen.emit('test_event')
        pubpen.unsubscribe(first)

        for iteration in range(1, 3):
            pubpen.emit('test_event')
            pending = asyncio.Task.all_tasks(loop=pubpen.loop)
            pubpen.loop.run_until_complete(asyncio.gather(*pending, loop=pubpen.loop))
            assert self.function1.called == 1

    def test_events_and_callbacks_isolated(self, pubpen):
        """
        Subscribe to two events.  Unsubscribe from one of them

        callbacks invoked on one event but not the other
        """
        first = pubpen.subscribe('test_event1', self.function1)
        second = pubpen.subscribe('test_event2', self.function2)
        pubpen.unsubscribe(first)
        assert self.function1.called == 0
        assert self.function2.called == 0

        for iteration in range(1, 3):
            pubpen.emit('test_event1')
            pubpen.emit('test_event2')
            pending = asyncio.Task.all_tasks(loop=pubpen.loop)
            pubpen.loop.run_until_complete(asyncio.gather(*pending, loop=pubpen.loop))
            assert self.function1.called == 0
            assert self.function2.called == 1 * iteration

    def test_events_isolated(self, pubpen):
        """
        Subscribe to two events.  Unsubscribe from one of them

        callbacks invoked on one event but not the other
        """
        first = pubpen.subscribe('test_event1', self.function1)
        second = pubpen.subscribe('test_event2', self.function1)
        pubpen.unsubscribe(first)
        assert self.function1.called == 0

        for iteration in range(1, 3):
            pubpen.emit('test_event1')
            pubpen.emit('test_event2')
            pending = asyncio.Task.all_tasks(loop=pubpen.loop)
            pubpen.loop.run_until_complete(asyncio.gather(*pending, loop=pubpen.loop))
            assert self.function1.called == 1 * iteration

    def test_callbacks_isolated(self, pubpen):
        """
        Subscribe to two callbacks to one event.  Unsubscribe one callback

        One callback invoked but not the other
        """
        first = pubpen.subscribe('test_event', self.function1)
        second = pubpen.subscribe('test_event', self.function2)
        pubpen.unsubscribe(first)
        assert self.function1.called == 0
        assert self.function2.called == 0

        for iteration in range(1, 3):
            pubpen.emit('test_event')
            pending = asyncio.Task.all_tasks(loop=pubpen.loop)
            pubpen.loop.run_until_complete(asyncio.gather(*pending, loop=pubpen.loop))
            assert self.function1.called == 0
            assert self.function2.called == 1 * iteration
