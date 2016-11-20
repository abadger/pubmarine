#!/usr/bin/python3 -tt
#
# Copyright: 2016, Toshio Kuratomi
# License: MIT

import asyncio
from pubmarine import PubPen

class Client:
    def __init__(self, pubpen):
        self.pubpen = pubpen
        self.pubpen.subscribe('server_msg', self.display)

    def display(self, message):
        print(message)

    async def send_message(self):
        for num in range(0, 5):
            print('message: {}'.format(num))
            await asyncio.sleep(2)

class Server:
    def __init__(self, pubpen):
        self.pubpen = pubpen
        self.beats = 0
        self.pubpen.loop.call_later(1, self.heartbeat)

    def heartbeat(self):
        self.pubpen.emit('server_msg', self.beats)
        self.beats += 1
        self.pubpen.loop.call_later(1, self.heartbeat)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    pubpen = PubPen(loop)
    server = Server(pubpen)
    client = Client(pubpen)
    loop.run_until_complete(client.send_message())
    loop.close()
