import asyncio
import weakref

import pytest

import pubmarine
from pubmarine import PubPen


@pytest.fixture
def pubpen(request):
    loop = asyncio.get_event_loop()
    pubpen = PubPen(loop)
    return pubpen

@pytest.fixture
def pubpen_predefined():
    loop = asyncio.get_event_loop()
    pubpen = PubPen(loop, event_list=['test_event1', 'test_event2'])
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
        assert isinstance(first, int)

        # Test internals of saving worked
        assert len(pubpen._event_handlers['test_event']) == 1

        event = next(iter(pubpen._event_handlers['test_event']))
        assert event[0] == first
        assert event[1] == weakref.ref(function)

    def test_subscribe_method(self, pubpen):
        """Test that adding method callbacks succeed"""
        foo = Foo()
        first = pubpen.subscribe('test_event', foo.method)
        assert isinstance(first, int)

        # Test internals of saving worked
        assert len(pubpen._event_handlers['test_event']) == 1

        event = next(iter(pubpen._event_handlers['test_event']))
        assert event[0] == first
        assert event[1] == weakref.WeakMethod(foo.method)

    def test_in_event_list(self, pubpen_predefined):
        """Test that adding events that are in the event list succeeds"""
        first = pubpen_predefined.subscribe('test_event1', function)
        assert isinstance(first, int)

        # Test internals of saving worked
        assert len(pubpen_predefined._event_handlers['test_event1']) == 1

        event = next(iter(pubpen_predefined._event_handlers['test_event1']))
        assert event[0] == first
        assert event[1] == weakref.ref(function)

    def test_not_in_event_list(self, pubpen_predefined):
        """Test that we raise an error when adding an event not in the event list"""
        with pytest.raises(pubmarine.EventNotFoundError) as e:
            first = pubpen_predefined.subscribe('test_event3', function)
        assert 'test_event3' in '{}'.format(e)
