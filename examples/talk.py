#!/usr/bin/python3 -tt
#
# Copyright: 2017, Toshio Kuratomi
# License: MIT

import asyncio
import curses
from functools import partial

from pubmarine import PubPen


PATH = '/var/tmp/talk.sock'

class Display:
    def __init__(self, pubpen):
        self.pubpen = pubpen

        self.pubpen.subscribe('incoming', self.show_message)
        self.pubpen.subscribe('typed', self.show_typing)
        self.pubpen.subscribe('error', self.show_error)
        self.pubpen.subscribe('info', self.show_error)
        self.pubpen.subscribe('conn_lost', self.show_error)

    def __enter__(self):
        self.stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)

        max_y, max_x = self.stdscr.getmaxyx()

        self.error_buffer = self.stdscr.derwin(1, max_x, 0, 0)

        self.separator1 = self.stdscr.derwin(1, max_x, 1, 0)
        sep_txt = b'-' * (max_x - 1)
        self.separator1.addstr(0, 0, sep_txt)

        self.chat_log = self.stdscr.derwin(max_y - 3, max_x, 2, 0)
        self.chat_max_y, self.chat_max_x = self.chat_log.getmaxyx()
        self.current_chat_line = 0

        self.separator2 = self.stdscr.derwin(1, max_x, max_y - 2, 0)
        sep_txt = b'=' * (max_x - 1)
        self.separator2.addstr(0, 0, sep_txt)

        self.input_buffer = self.stdscr.derwin(1, max_x, max_y - 1, 0)
        self.input_max_y, self.input_max_x = self.input_buffer.getmaxyx()
        self.input_current_x = 0
        self.input_contents = ''

        self.stdscr.refresh()
        return self

    def __exit__(self, *args):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

        return False

    async def get_ch(self):
        while True:
            char = chr(await self.pubpen.loop.run_in_executor(None, self.stdscr.getch))
            self.pubpen.publish('typed', char)

    def show_message(self, message, user):
        # Instead of scrolling, simply stop the program
        if self.current_chat_line >= self.chat_max_y:
            self.pubpen.loop.stop()
            return

        message = "%s %s" % (user, message)

        # Instead of line breaking, simply truncate the message
        if len(message) > self.chat_max_x:
            message = message[:self.chat_max_x]

        self.chat_log.addstr(self.current_chat_line, 0, message.encode('utf-8'))
        self.current_chat_line += 1
        self.chat_log.refresh()

    def show_typing(self, char):
        if char == '\n':
            if self.input_contents == '.':
                self.pubpen.loop.stop()
            self.pubpen.publish('outgoing', self.input_contents)
            self.show_message(self.input_contents, '<myself>')
            self.clear_typing()
            return

        self.input_current_x += 1
        self.input_contents += char
        self.input_buffer.addstr(0, self.input_current_x - 1, char.encode('utf-8'))
        self.input_buffer.refresh()

    def clear_typing(self):
        self.input_current_x = 0
        self.input_buffer.clear()
        self.input_contents = ''
        self.input_buffer.refresh()

    def show_error(self, exc):
        self.error_buffer.clear()
        self.error_buffer.addstr(0, 0, str(exc).encode('utf-8'))
        self.error_buffer.refresh()


class TalkProtocol(asyncio.Protocol):
    def __init__(self, pubpen):
        self.pubpen = pubpen

        self.pubpen.subscribe('outgoing', self.send_message)

    def send_message(self, message):
        self.transport.write(message.encode('utf-8'))

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.pubpen.publish('incoming', data.decode('utf-8', errors='replace'), "<you>")

    def error_received(self, exc):
        self.pubpen.publish('error', exc)

    def connection_lost(self, exc):
        self.pubpen.publish('conn_lost', exc)
        self.pubpen.loop.stop()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    pubpen = PubPen(loop)

    with Display(pubpen) as display:
        try:
            # try Client first
            connection = loop.create_unix_connection(partial(TalkProtocol, pubpen), PATH)
            loop.run_until_complete(connection)
        except ConnectionRefusedError:
            # server
            connection = loop.create_unix_server(partial(TalkProtocol, pubpen), PATH)
            loop.run_until_complete(connection)

        task = loop.create_task(display.get_ch())
        loop.run_forever()
        task.cancel()
        try:
            loop.run_until_complete(task)
        except:
            pass
