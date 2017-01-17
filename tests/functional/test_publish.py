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
        print('here')
        self.called += 1


@pytest.fixture
def function1(request):
    request.cls.function1 = Function()


@pytest.fixture
def function2(request):
    request.cls.function2 = Function()


@pytest.mark.usefixtures('function1', 'function2')
class TestFunctionalPublish:

    def test_one_event_one_callback(self, pubpen):
        """
        One event registered, one callback registered

        Yields callback called once each time event is published.
        """
        first = pubpen.subscribe('test_event', self.function1)
        assert self.function1.called == 0

        for iteration in range(1, 3):
            pubpen.publish('test_event')
            pending = asyncio.Task.all_tasks(loop=pubpen.loop)
            pubpen.loop.run_until_complete(asyncio.gather(*pending, loop=pubpen.loop))
            assert self.function1.called == 1 * iteration

    def test_one_event_one_callback_several_times(self, pubpen):
        """
        One event registered, one callback registered there three times

        Yields callback called three times each time  event is published.
        """
        first = pubpen.subscribe('test_event', self.function1)
        second = pubpen.subscribe('test_event', self.function1)
        third = pubpen.subscribe('test_event', self.function1)
        assert self.function1.called == 0

        for iteration in range(1, 3):
            pubpen.publish('test_event')
            pending = asyncio.Task.all_tasks(loop=pubpen.loop)
            pubpen.loop.run_until_complete(asyncio.gather(*pending, loop=pubpen.loop))
            assert self.function1.called == 3 * iteration

    def test_multi_events_one_callback_all_events_called(self, pubpen):
        """
        Three events registered, one callback registered there three times

        Yields callback called once any time any of the three events are published
        """
        first = pubpen.subscribe('test_event1', self.function1)
        second = pubpen.subscribe('test_event2', self.function1)
        third = pubpen.subscribe('test_event3', self.function1)
        assert self.function1.called == 0

        for iteration in range(1, 3):
            pubpen.publish('test_event1')
            pubpen.publish('test_event2')
            pubpen.publish('test_event3')
            pending = asyncio.Task.all_tasks(loop=pubpen.loop)
            pubpen.loop.run_until_complete(asyncio.gather(*pending, loop=pubpen.loop))
            assert self.function1.called == 3 * iteration

    def test_multi_events_one_callback_one_event_called(self, pubpen):
        """
        Three events registered, one callback registered there three times

        Each event is published so the callback is called three times every
        time the events are published
        """
        first = pubpen.subscribe('test_event1', self.function1)
        second = pubpen.subscribe('test_event2', self.function1)
        third = pubpen.subscribe('test_event3', self.function1)
        assert self.function1.called == 0

        for iteration in range(1, 3):
            pubpen.publish('test_event1')
            pending = asyncio.Task.all_tasks(loop=pubpen.loop)
            pubpen.loop.run_until_complete(asyncio.gather(*pending, loop=pubpen.loop))
            assert self.function1.called == 1 * iteration

    def test_one_event_multi_callback(self, pubpen):
        """
        One event registered, two callbacks registered there.

        Each callback is called when the event is published
        """
        first = pubpen.subscribe('test_event', self.function1)
        second = pubpen.subscribe('test_event', self.function2)
        assert self.function1.called == 0
        assert self.function2.called == 0

        pubpen.publish('test_event')
        pending = asyncio.Task.all_tasks(loop=pubpen.loop)
        pubpen.loop.run_until_complete(asyncio.gather(*pending, loop=pubpen.loop))
        assert self.function1.called == 1
        assert self.function2.called == 1

    def test_one_event_multi_callback_several_times(self, pubpen):
        """
        One event registered, two callbacks registered there.

        Each callback is called each time the event is published
        """
        first = pubpen.subscribe('test_event', self.function1)
        second = pubpen.subscribe('test_event', self.function2)
        assert self.function1.called == 0
        assert self.function2.called == 0

        for iteration in range(1, 3):
            pubpen.publish('test_event')
            pending = asyncio.Task.all_tasks(loop=pubpen.loop)
            pubpen.loop.run_until_complete(asyncio.gather(*pending, loop=pubpen.loop))
            assert self.function1.called == 1 * iteration
            assert self.function2.called == 1 * iteration

    def test_multi_event_multi_callback_all_events_called(self, pubpen):
        """
        One event registered, two callbacks registered there.

        Each callback is called each time the event is published
        """
        first = pubpen.subscribe('test_event1', self.function1)
        second = pubpen.subscribe('test_event2', self.function2)
        assert self.function1.called == 0
        assert self.function2.called == 0

        for iteration in range(1, 3):
            pubpen.publish('test_event1')
            pubpen.publish('test_event2')
            pending = asyncio.Task.all_tasks(loop=pubpen.loop)
            pubpen.loop.run_until_complete(asyncio.gather(*pending, loop=pubpen.loop))
            assert self.function1.called == 1 * iteration
            assert self.function2.called == 1 * iteration

    def test_multi_event_multi_callback_one_event_called(self, pubpen):
        """
        One event registered, two callbacks registered there.

        Each callback is called each time the event is published
        """
        first = pubpen.subscribe('test_event1', self.function1)
        second = pubpen.subscribe('test_event2', self.function2)
        assert self.function1.called == 0
        assert self.function2.called == 0

        for iteration in range(1, 3):
            pubpen.publish('test_event1')
            pending = asyncio.Task.all_tasks(loop=pubpen.loop)
            pubpen.loop.run_until_complete(asyncio.gather(*pending, loop=pubpen.loop))
            assert self.function1.called == 1 * iteration
            assert self.function2.called == 0

    def test_multi_event_multi_callback_specific_events(self, pubpen):
        """
        One event registered, two callbacks registered there.

        Each callback is called each time the event is published
        """
        first = pubpen.subscribe('test_event1', self.function1)
        second = pubpen.subscribe('test_event2', self.function2)
        assert self.function1.called == 0
        assert self.function2.called == 0

        for iteration in range(1, 3):
            pubpen.publish('test_event1')
            pubpen.publish('test_event2')
            pending = asyncio.Task.all_tasks(loop=pubpen.loop)
            pubpen.loop.run_until_complete(asyncio.gather(*pending, loop=pubpen.loop))
            assert self.function1.called == 1 * iteration
            assert self.function2.called == 1 * iteration


@pytest.mark.usefixtures('function1')
class TestFunctionalEmit:
    def test_emit_same_as_publish(self, pubpen):
        """
        One event registered, one callback registered

        Yields callback called once each time event is published.
        """
        first = pubpen.subscribe('test_event', self.function1)
        assert self.function1.called == 0

        for iteration in range(1, 3):
            pubpen.emit('test_event')
            pending = asyncio.Task.all_tasks(loop=pubpen.loop)
            pubpen.loop.run_until_complete(asyncio.gather(*pending, loop=pubpen.loop))
            assert self.function1.called == 1 * iteration
