import weakref

import pytest

import pubmarine
from pubmarine import PubPen


@pytest.fixture
def pubpen(event_loop):
    pubpen = PubPen(event_loop)
    return pubpen


@pytest.fixture
def pubpen_predefined(event_loop):
    pubpen = PubPen(event_loop, event_list=['test_event1', 'test_event2'])
    return pubpen


class Foo:
    def method(self):
        pass


def function():
    pass


class TestPubPenSubscribe:

    def test_pubpen_id_integer(self, pubpen):
        id_ = pubpen.subscribe('test_event', function)
        assert isinstance(id_, int)

    def test_pubpen_id_increments(self, pubpen):
        first = pubpen.subscribe('test_event', lambda: None)
        second = pubpen.subscribe('test_event', lambda: None)
        assert second > first

    def test_subscribe_function(self, pubpen):
        """Test that adding function callbacks succeeds"""
        first = pubpen.subscribe('test_event', function)

        # Test internals of saving worked
        assert pubpen._subscriptions[first] == 'test_event'
        assert len(pubpen._event_handlers['test_event']) == 1

        event = pubpen._event_handlers['test_event']
        assert list(event.keys()) == [first]
        assert list(event.values()) == [weakref.ref(function)]

    def test_subscribe_method(self, pubpen):
        """Test that adding method callbacks succeed"""
        foo = Foo()
        first = pubpen.subscribe('test_event', foo.method)

        # Test internals of saving worked
        assert pubpen._subscriptions[first] == 'test_event'
        assert len(pubpen._event_handlers['test_event']) == 1

        event = pubpen._event_handlers['test_event']
        assert list(event.keys()) == [first]
        assert list(event.values()) == [weakref.WeakMethod(foo.method)]

    def test_in_event_list(self, pubpen_predefined):
        """Test that adding events that are in the event list succeeds"""
        first = pubpen_predefined.subscribe('test_event1', function)

        # Test internals of saving worked
        assert pubpen_predefined._subscriptions[first] == 'test_event1'
        assert len(pubpen_predefined._event_handlers['test_event1']) == 1

        event = pubpen_predefined._event_handlers['test_event1']
        assert list(event.keys()) == [first]
        assert list(event.values()) == [weakref.ref(function)]

    def test_not_in_event_list(self, pubpen_predefined):
        """Test that we raise an error when adding an event not in the event list"""
        with pytest.raises(pubmarine.EventNotFoundError) as e:
            first = pubpen_predefined.subscribe('test_event3', function)
        assert 'test_event3' in '{}'.format(e)

    def test_subscribe_same_callback_same_event(self, pubpen):
        first = pubpen.subscribe('test_event', function)
        second = pubpen.subscribe('test_event', function)

        # Test internals of subscribing worked
        assert pubpen._subscriptions[first] == 'test_event'
        assert pubpen._subscriptions[second] == 'test_event'
        assert len(pubpen._event_handlers['test_event']) == 2

        events = pubpen._event_handlers['test_event']
        assert events[first] == weakref.ref(function)
        assert events[second] == weakref.ref(function)

    def test_subscribe_same_callback_diff_event(self, pubpen):
        first = pubpen.subscribe('test_event1', function)
        second = pubpen.subscribe('test_event2', function)

        # Test internals of subscribing worked
        assert pubpen._subscriptions[first] == 'test_event1'
        assert pubpen._subscriptions[second] == 'test_event2'
        assert len(pubpen._event_handlers['test_event1']) == 1
        assert len(pubpen._event_handlers['test_event2']) == 1

        events = pubpen._event_handlers['test_event1']
        assert events[first] == weakref.ref(function)
        events = pubpen._event_handlers['test_event2']
        assert events[second] == weakref.ref(function)

    def test_subscribe_diff_callback_same_event(self, pubpen):
        first = pubpen.subscribe('test_event', function)
        foo = Foo()
        second = pubpen.subscribe('test_event', foo.method)

        # Test internals of subscribing worked
        assert pubpen._subscriptions[first] == 'test_event'
        assert pubpen._subscriptions[second] == 'test_event'
        assert len(pubpen._event_handlers['test_event']) == 2

        events = pubpen._event_handlers['test_event']
        assert events[first] != events[second]
        assert events[first] in (weakref.ref(function), weakref.WeakMethod(foo.method))
        assert events[second] in (weakref.ref(function), weakref.WeakMethod(foo.method))

    def test_subscribe_diff_callback_diff_event(self, pubpen):
        first = pubpen.subscribe('test_event1', function)
        foo = Foo()
        second = pubpen.subscribe('test_event2', foo.method)

        # Test internals of subscribing worked
        assert pubpen._subscriptions[first] == 'test_event1'
        assert pubpen._subscriptions[second] == 'test_event2'
        assert len(pubpen._event_handlers['test_event1']) == 1
        assert len(pubpen._event_handlers['test_event2']) == 1

        events = pubpen._event_handlers['test_event1']
        assert events[first] == weakref.ref(function)
        events = pubpen._event_handlers['test_event2']
        assert events[second] == weakref.WeakMethod(foo.method)
