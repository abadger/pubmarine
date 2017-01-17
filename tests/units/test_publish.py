from unittest import mock
import pytest

import pubmarine
from pubmarine import PubPen


@pytest.fixture
def pubpen(event_loop):
    pubpen = PubPen(event_loop)
    pubpen.loop = mock.MagicMock()
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


class TestPubPenEmit:
    def test_emit_warns(self, pubpen):
        with pytest.warns(DeprecationWarning) as e:
            pubpen.emit('test_event')

    def test_called_publish(self, pubpen_emit):
        pubpen_emit.emit('test_event')
        assert pubpen_emit.publish.called
        assert pubpen_emit.publish.call_count == 1
