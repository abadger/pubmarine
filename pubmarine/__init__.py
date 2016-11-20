# This file is part of PubMarine.
#
# Foobar is free software: you can redistribute it and/or modify
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
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright: 2017, Toshio Kuratomi
# License: LGPLv3+
"""
PubMarine is a simple PubSub framework for Python3's asyncio.

Authors: Toshio Kuratomi <toshio@fedoraproject.org
"""

__version__ = '0.1'
__version_info__ = ('0', '1')

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
        if event_list is not None:
            self._event_list = frozenset(event_list)
        else:
            self._event_list = frozenset()

        self._event_handlers = defaultdict(set)

    def subscribe(self, event, callback):
        """ Subscribe a callback to an event

        :arg event: String name of an event to subscribe to
        :callback: The function to call when the event is emitted.  This can
            be any python callable.

        Use :func:`functools.partial` to call the callback with any other
        arguments.

        """
        if self._event_list and event not in self._event_list:
            raise EventNotFoundError('{} is not a registered event' \
                    .format(event))
        try:
            # Add a method
            self._event_handlers[event].add(WeakMethod(callback))
        except TypeError:
            # Add a function
            self._event_handlers[event].add(ref(callback))

    def emit(self, event, *args, **kwargs):
        """ Emit an event

        :arg event: String name of an event to emit

        Other args and keyword args are passed to the callback function.
        """
        if self._event_list and event not in self._event_list:
            raise EventNotFoundError('{} is not a registered event' \
                    .format(event))

        gone = []
        for handler in self._event_handlers[event]:
            # Get the callback from the weakref
            func = handler()
            if func is None:
                # Callback was deleted.  Cleanup the weakref as well
                gone.append(handler)
                continue
            self.loop.call_soon(func, *args, **kwargs)

        # Cleanup any handlers that are no longer around
        for handler in gone:
            self._event_handlers[event].discard(handler)
