# This file is part of PubMarine.
#
# PubMarine is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PubMarine.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright: 2017, Toshio Kuratomi
# License: LGPLv3+
"""
PubMarine is a simple PubSub framework for Python3's asyncio.

Authors: Toshio Kuratomi <toshio@fedoraproject.org
"""

__version__ = '0.4'
__version_info__ = ('0', '4')

import warnings
from collections import defaultdict
from weakref import WeakMethod, ref

class PubMarineError(Exception):
    """ Base of all errors specific to PubMarine
    """
    pass


class EventNotFoundError(PubMarineError):
    """ Raised when an event is not handled by this PubPen
    """
    pass


class PubPen:
    """
    A PubPen object coordinates subscription and publication.

    Most programs should create one PubPen instance and then share it between
    all of the objects that wish to communicate with each other.

    """
    def __init__(self, loop, event_list=None):
        """
        :arg loop: Event loop (asyncio compatible) to use.
        :kwarg event_list: If given, event_list is a list of allowed
            event_names.  If not given, any name can be subscribed to on the
            fly.  Dynamic event_lists are convenient.  Statically defined
            lists provide protection against typos.
        """
        self.loop = loop
        self._next_id = self._id_generator()
        self._subscriptions = {}

        if event_list is not None:
            self._event_list = frozenset(event_list)
        else:
            self._event_list = frozenset()

        self._event_handlers = defaultdict(dict)

    def _id_generator(self):
        i = 0
        while True:
            yield i
            i += 1

    def subscribe(self, event, callback):
        """ Subscribe a callback to an event

        :arg event: String name of an event to subscribe to
        :callback: The function to call when the event is published.  This can
            be any python callable.

        Use :func:`functools.partial` to call the callback with any other
        arguments.

        .. note:: The callback is registered with the event each time this
            method is called.  The callback is called each time it has been
            registered when the event is published.  For example::

                >>> import asyncio
                >>> import pubmarine
                >>> pubpen = pubmarine.PubPen(asyncio.get_event_loop)
                >>> def message():
                ...     print('message called')
                >>> pubpen.subscribe('test', message)
                >>> pubpen.subscribe('test', message)
                >>> pubpen.publish('test')
                message called
                message called

            If the caller wants the callback to only be called once, it is the
            caller's responsibility to only subscribe the callbak once.
        """
        if self._event_list and event not in self._event_list:
            raise EventNotFoundError('{} is not a registered event' \
                    .format(event))

        # Get an id for the subscription
        sub_id = next(self._next_id)

        self._subscriptions[sub_id] = event
        try:
            # Add a method
            self._event_handlers[event][sub_id] = WeakMethod(callback)
        except TypeError:
            # Add a function
            self._event_handlers[event][sub_id] = ref(callback)

        return sub_id

    def unsubscribe(self, sub_id):
        """Unsubscribe from an event.

        :arg sub_id: The subscription id returned from subscribe.
        """
        if sub_id in self._subscriptions:
            event = self._subscriptions[sub_id]
        else:
            # It's okay, we just want the subscription to be gone
            return

        for cur_sub_id in self._event_handlers[event]:
            if cur_sub_id == sub_id:
                del self._event_handlers[event][sub_id]
                break

        del self._subscriptions[sub_id]

    def publish(self, event, *args, **kwargs):
        """ Publish an event

        :arg event: String name of an event to publish

        Other args and keyword args are passed to the callback function.
        """
        if self._event_list and event not in self._event_list:
            raise EventNotFoundError('{} is not a registered event' \
                    .format(event))

        removed_sub_ids = []
        for sub_id, handler in self._event_handlers[event].items():
            # Get the callback from the weakref
            func = handler()
            if func is None:
                # Callback was deleted.  Cleanup the weakref as well
                removed_sub_ids.append(sub_id)
                continue
            self.loop.call_soon(func, *args, **kwargs)

        # Cleanup any handlers that are no longer around
        for sub_id in removed_sub_ids:
            del self._event_handlers[event][sub_id]
            try:
                del self._subscriptions[sub_id]
            except KeyError:
                # It's okay.  We just want this gone.
                pass

    def emit(self, event, *args, **kwargs):
        """ Publish an event

        :arg event: String name of an event to publish

        Other args and keyword args are passed to the callback function.

        **Deprecated**: Use publish() instead
        """
        warnings.warn('PubPen.emit() is deprecated.  Use PubPen.publish()'
                ' instead', DeprecationWarning, stacklevel=2)
        self.publish(event, *args, **kwargs)
