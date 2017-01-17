import pytest

from pubmarine import PubPen


@pytest.fixture
def pubpen(event_loop):
    pubpen = PubPen(event_loop)
    return pubpen


@pytest.fixture
def pubpen_multi_event(event_loop):
    pubpen = PubPen(event_loop)

    # Fake up the internal data structures that unsubscribe uses
    pubpen._subscriptions[0] = 'test_event1'
    pubpen._subscriptions[1] = 'test_event2'
    pubpen._event_handlers['test_event1'][0] = 'handler1'
    pubpen._event_handlers['test_event2'][1] = 'handler2'

    return pubpen


@pytest.fixture
def pubpen_multi_callback(event_loop):
    pubpen = PubPen(event_loop)

    # Fake up the internal data structures that unsubscribe uses
    pubpen._subscriptions[0] = 'test_event1'
    pubpen._subscriptions[1] = 'test_event1'
    pubpen._subscriptions[2] = 'test_event1'
    pubpen._event_handlers['test_event1'][0] = 'handler1'
    pubpen._event_handlers['test_event1'][1] = 'handler2'
    pubpen._event_handlers['test_event1'][2] = 'handler3'

    return pubpen


@pytest.fixture
def pubpen_partially_dealloc(event_loop):
    """The event handler has been partially removed already."""
    pubpen = PubPen(event_loop)
    pubpen._subscriptions[0] = 'test_event1'
    return pubpen

class Foo:
    def method(self):
        pass


def function():
    pass


class TestPubPenUnsubscribe:

    def test_unsubscribe_nonexisting(self, pubpen):
        result = pubpen.unsubscribe(0)
        assert result is None

        # Test internal implementation is correct
        assert len(pubpen._subscriptions) == 0
        assert len(pubpen._event_handlers) == 0

    def test_unsubscribe_multi_event_remove_first(self, pubpen_multi_event):
        result = pubpen_multi_event.unsubscribe(0)
        assert result is None

        # Test internal implementation is correct
        assert len(pubpen_multi_event._subscriptions) == 1
        assert pubpen_multi_event._subscriptions[1] == 'test_event2'

        assert len(pubpen_multi_event._event_handlers['test_event1']) == 0
        assert len(pubpen_multi_event._event_handlers['test_event2']) == 1
        assert (1, 'handler2') in pubpen_multi_event._event_handlers['test_event2'].items()


    def test_unsubscribe_multi_event_remove_last(self, pubpen_multi_event):
        result = pubpen_multi_event.unsubscribe(1)
        assert result is None

        # Test internal implementation is correct
        assert len(pubpen_multi_event._subscriptions) == 1
        assert pubpen_multi_event._subscriptions[0] == 'test_event1'

        assert len(pubpen_multi_event._event_handlers['test_event1']) == 1
        assert len(pubpen_multi_event._event_handlers['test_event2']) == 0
        assert (0, 'handler1') in pubpen_multi_event._event_handlers['test_event1'].items()

    def test_unsubscribe_multi_callback_remove_first(self, pubpen_multi_callback):
        result = pubpen_multi_callback.unsubscribe(0)
        assert result is None

        # Test internal implementation is correct
        assert len(pubpen_multi_callback._subscriptions) == 2
        assert pubpen_multi_callback._subscriptions[1] == 'test_event1'
        assert pubpen_multi_callback._subscriptions[2] == 'test_event1'

        assert len(pubpen_multi_callback._event_handlers['test_event1']) == 2
        assert (1, 'handler2') in pubpen_multi_callback._event_handlers['test_event1'].items()
        assert (2, 'handler3') in pubpen_multi_callback._event_handlers['test_event1'].items()

    def test_unsubscribe_multi_callback_remove_last(self, pubpen_multi_callback):
        result = pubpen_multi_callback.unsubscribe(2)
        assert result is None

        # Test internal implementation is correct
        assert len(pubpen_multi_callback._subscriptions) == 2
        assert pubpen_multi_callback._subscriptions[0] == 'test_event1'
        assert pubpen_multi_callback._subscriptions[1] == 'test_event1'

        assert len(pubpen_multi_callback._event_handlers['test_event1']) == 2
        assert (0, 'handler1') in pubpen_multi_callback._event_handlers['test_event1'].items()
        assert (1, 'handler2') in pubpen_multi_callback._event_handlers['test_event1'].items()

    def test_unsubscribe_partially_deallocated_handler(self, pubpen_partially_dealloc):
        pubpenpd = pubpen_partially_dealloc
        result = pubpenpd.unsubscribe(0)
        assert result is None

        # Test internal implementation is correct
        assert len(pubpenpd._subscriptions) == 0
        assert len(pubpenpd._event_handlers['test_event1']) == 0

