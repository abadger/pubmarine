from unittest import mock
import pytest

import pubmarine
from pubmarine import PubPen

def handler1():
    return 'handler1'


def handler2():
    return 'handler2'


def handler3():
    return 'handler3'


def handler_None():
    return None


@pytest.fixture
def pubpen(event_loop):
    pubpen = PubPen(event_loop)
    pubpen.loop = mock.MagicMock()
    pubpen._event_handlers['test_event1'][0] = handler1
    pubpen._event_handlers['test_event2'][1] = handler2
    pubpen._event_handlers['test_event2'][2] = handler3
    return pubpen


@pytest.fixture
def pubpen_predefined(event_loop):
    pubpen = PubPen(event_loop, event_list=['test_event1', 'test_event2'])
    pubpen.loop = mock.MagicMock()
    return pubpen


@pytest.fixture
def pubpen_emit(event_loop):
    pubpen = PubPen(event_loop)
    pubpen.publish = mock.MagicMock()
    return pubpen


@pytest.fixture
def pubpen_handlers_dealloc(event_loop):
    pubpen = PubPen(event_loop)
    pubpen.loop = mock.MagicMock()
    pubpen._subscriptions[0] = 'test_event1'
    pubpen._subscriptions[1] = 'test_event1'
    pubpen._event_handlers['test_event1'][0] = handler1
    pubpen._event_handlers['test_event1'][1] = handler_None
    return pubpen


@pytest.fixture
def pubpen_handlers_partially_removed(event_loop):
    """
    The handler has been deallocated (because it's a weakref) but it's only
    been removed from the _subscriptions list already.
    """
    pubpen = PubPen(event_loop)
    pubpen.loop = mock.MagicMock()
    pubpen._subscriptions[0] = 'test_event1'
    pubpen._event_handlers['test_event1'][0] = handler1
    pubpen._event_handlers['test_event1'][1] = handler_None
    return pubpen


class TestPubPenPublish:
    def test_publish_event_list_pass(self, pubpen_predefined):
        result = pubpen_predefined.publish('test_event1')
        assert result is None
        assert pubpen_predefined.loop.call_soon.called is False

        result = pubpen_predefined.publish('test_event2')
        assert result is None
        assert pubpen_predefined.loop.call_soon.called is False

    def test_publish_event_list_fail(self, pubpen_predefined):
        with pytest.raises(pubmarine.EventNotFoundError) as e:
            result = pubpen_predefined.publish('test_event_bad')
        assert 'test_event_bad' in '{}'.format(e)

    def test_no_callbacks(self, pubpen):
        result = pubpen.publish('no_event')
        assert result is None

        assert pubpen.loop.call_soon.called is False

    def test_one_callback(self, pubpen):
        result = pubpen.publish('test_event1')
        assert result is None

        assert pubpen.loop.call_soon.called is True
        assert pubpen.loop.call_soon.call_count == 1
        assert 'handler1' in pubpen.loop.call_soon.call_args[0]

    def test_multi_callbacks(self, pubpen):
        result = pubpen.publish('test_event2')
        assert result is None

        assert pubpen.loop.call_soon.called is True
        assert pubpen.loop.call_soon.call_count == 2
        for call in pubpen.loop.call_soon.call_args_list:
            assert 'handler2' in call[0] or 'handler3' in call[0]
        assert pubpen.loop.call_soon.call_args_list[0][0] != pubpen.loop.call_soon.call_args_list[1][0]

    def test_deallocated_callback(self, pubpen_handlers_dealloc):
        pubpenhd = pubpen_handlers_dealloc
        result = pubpenhd.publish('test_event1')
        assert result is None

        assert pubpenhd.loop.call_soon.called is True
        assert pubpenhd.loop.call_soon.call_count == 1
        assert 'handler1' in pubpenhd.loop.call_soon.call_args_list[0][0]

        # Test internals have been updated correctly
        assert len(pubpenhd._event_handlers['test_event1']) == 1
        assert len(pubpenhd._subscriptions) == 1
        assert pubpenhd._subscriptions[0] == 'test_event1'

    def test_partially_removed_callback(self, pubpen_handlers_partially_removed):
        pubpenhpr = pubpen_handlers_partially_removed
        result = pubpenhpr.publish('test_event1')
        assert result is None

        assert pubpenhpr.loop.call_soon.called is True
        assert pubpenhpr.loop.call_soon.call_count == 1
        assert 'handler1' in pubpenhpr.loop.call_soon.call_args_list[0][0]

        # Test internals have been updated correctly
        assert len(pubpenhpr._event_handlers['test_event1']) == 1
        assert len(pubpenhpr._subscriptions) == 1
        assert pubpenhpr._subscriptions[0] == 'test_event1'


class TestPubPenEmit:
    def test_emit_warns(self, pubpen):
        with pytest.warns(DeprecationWarning) as e:
            pubpen.emit('test_event')

    def test_called_publish(self, pubpen_emit):
        pubpen_emit.emit('test_event')
        assert pubpen_emit.publish.called
        assert pubpen_emit.publish.call_count == 1
