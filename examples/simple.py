#!/usr/bin/python3 -tt
#
# Copyright: 2016, Toshio Kuratomi
# License: MIT
"""
Simple example of one logical thread of control emitting periodic events while another logical
thread of control watches and echoes data about those events
"""
import asyncio
import sys

from pubmarine import PubPen


# Python-3.7 introduced a new asyncio API.  The following code shows both
# pre-3.7 and post-3.7 coding style
PY37 = sys.version_info >= (3, 7)


class Server:
    def __init__(self, pubpen):
        self.pubpen = pubpen
        self.beats = 0

    async def heartbeat(self):
        self.pubpen.publish('server_msg', self.beats)
        self.beats += 1
        if self.beats <= 5:
            await asyncio.sleep(1)
            await self.heartbeat()


class Client:
    def __init__(self, pubpen):
        self.pubpen = pubpen
        self.pubpen.subscribe('server_msg', self.display)

    @staticmethod
    def display(message):
        print(message)


async def start():
    if PY37:
        loop = asyncio.get_running_loop()
    else:
        loop = asyncio.get_event_loop()

    pubpen = PubPen(loop)
    server = Server(pubpen)
    # We create a client but never call it directly.  Instead, it subscribes to the `server_msg`
    # event and does something whenever that event occurs.
    client = Client(pubpen)

    await server.heartbeat()


def main():
    if PY37:
        asyncio.run(start())
    else:
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(start())
        finally:
            loop.close()


if __name__ == '__main__':
    main()
