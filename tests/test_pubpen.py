import asyncio

import pytest

from pubmarine import PubPen


@pytest.fixture
def pubpen(request):
    loop = asyncio.get_event_loop()
    pubpen = PubPen(loop)
    return pubpen

@pytest.mark.usefixtures("pubpen")
class TestPubPenSubscribe:
    def test_pubpen_id_integer(self, pubpen):
        id_ = pubpen.subscribe('test_event', lambda: None)
        assert isinstance(id_, int)

    def test_pubpen_id_increments(self, pubpen):
        first = pubpen.subscribe('test_event', lambda: None)
        second = pubpen.subscribe('test_event', lambda: None)

        assert second > first
