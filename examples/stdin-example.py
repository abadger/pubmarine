#!/usr/bin/python3 -tt
#
# Copyright: 2016, Toshio Kuratomi
# License: MIT

import asyncio
import sys

from pubmarine import PubPen

class Server:
    def __init__(self, pubpen):
        self.pubpen = pubpen
        self.beats = 0
        self.pubpen.loop.call_later(1, self.heartbeat)

        self.pubpen.subscribe('incoming', self.broadcast)

    def broadcast(self, message):
        self.pubpen.emit('outgoing', message)

    def heartbeat(self):
        self.pubpen.emit('outgoing', self.beats)
        self.beats += 1
        self.pubpen.loop.call_later(1, self.heartbeat)


class Client:
    def __init__(self, pubpen, input_queue):
        self.pubpen = pubpen
        self.input = input_queue
        self.pubpen.subscribe('outgoing', self.display)

    def display(self, message):
        print(message)

    @asyncio.coroutine
    def await_input(self):
        while True:
            message = yield from self.input.get()
            if message.strip() == '.':
                self.pubpen.loop.stop()
                break
            self.pubpen.emit('incoming', message)


def get_stdin_data(loop, queue):
    loop.create_task(queue.put(sys.stdin.readline()))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()
    loop.add_reader(sys.stdin, get_stdin_data, loop, queue)
    pubpen = PubPen(loop)
    server = Server(pubpen)
    client = Client(pubpen, queue)
    loop.run_until_complete(client.await_input())
    loop.close()
