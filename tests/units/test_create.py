from pubmarine import PubPen


class TestPubPenCreate:
    def test_create(self, event_loop):
        """Smoketest that we can create a PubPen object"""
        pubpen = PubPen(event_loop)

        # Test internals were setup
        assert len(pubpen._event_handlers) == 0
        assert len(pubpen._event_list) == 0

    def test_create_with_event_list(self, event_loop):
        """Test that creating a PubPen with an event_list stores the event_list"""
        pubpen = PubPen(event_loop, ['one', 'two'])

        # Test internals of saving the event_list worked
        assert len(pubpen._event_handlers) == 0
        assert len(pubpen._event_list) == 2
        assert 'one' in pubpen._event_list
        assert 'two' in pubpen._event_list
