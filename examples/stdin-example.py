#!/usr/bin/python3 -tt
#
# Copyright: 2016, Toshio Kuratomi
# License: MIT
"""
A continuation of simple.py that adds parallel reading from stdin to the example.
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
        self.pubpen.subscribe('from_client', self.broadcast)

    def broadcast(self, message):
        self.pubpen.publish('from_server', 'Server echoes: {}'.format(message))

    async def heartbeat(self):
        self.pubpen.publish('from_server', self.beats)
        self.beats += 1
        await asyncio.sleep(1)
        # Note: Unlike the simple example, we do not recursively call ourselves.
        # This is because we don't know how many times we might call ourselves here;
        # that's under user control.  So we have to guard against recursing beyond the
        # recursion limit by exiting this function and having the new function invocation
        # happen in the loop, outside of this function
        self.pubpen.loop.create_task(self.heartbeat())


class Client:
    def __init__(self, pubpen, input_queue):
        self.pubpen = pubpen
        self.input = input_queue
        self.pubpen.subscribe('from_server', self.display)

    @staticmethod
    def display(message):
        print('Client echoes: {}'.format(message))

    async def await_input(self):
        while True:
            message = await self.input.get()
            if message.strip() == '.':
                self.pubpen.loop.stop()
                break
            self.pubpen.publish('from_client', message)


def get_stdin_data(loop, queue):
    loop.create_task(queue.put(sys.stdin.readline()))


async def start():
    if PY37:
        loop = asyncio.get_running_loop()
    else:
        loop = asyncio.get_event_loop()

    queue = asyncio.Queue()
    loop.add_reader(sys.stdin, get_stdin_data, loop, queue)

    pubpen = PubPen(loop)
    server = Server(pubpen)
    client = Client(pubpen, queue)

    await asyncio.wait((client.await_input(), server.heartbeat()))


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
