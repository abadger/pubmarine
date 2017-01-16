.. image:: https://travis-ci.org/abadger/pubmarine.svg?branch=master
    :target: https://travis-ci.org/abadger/pubmarine

.. image:: https://coveralls.io/repos/github/abadger/pubmarine/badge.svg?branch=master
    :target: https://coveralls.io/github/abadger/pubmarine?branch=master

=========
Pubmarine
=========

Welcome to Pubmarine, a simple pubsub framework for Python-3.5's asyncio.

Pubmarine allows you to code an application using events to communicate
between different parts of the program.  This gives your program greater
flexibility than defining a single API.  For instance, if a program has
multiple user interfaces to choose from then it will either let some
implementation details leak through from the interface layer to the backend
or it will have to implement its own abstraction layer for the backend to
communicate to the user interface.  Pubmarine offers the program the code for
that abstraction layer built on top of asyncio so you can have parallelism
In IO bound code.


Simple Example
==============

Here's a very simple example to get you started::


    #!/usr/bin/python3 -tt

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

In this example, the server class emits the ``server_msg`` event once
a second (provided that other coroutines give up control for it to do so.)
The client subscribes to the ``server_msg`` event and calls the display()
method any time that event is emitted.  The client also prints a message
of its own to the screen to show that both the server and the client
coroutines are getting serviced.

Requirements
============

Pubmarine requires Python-3.5.0 or greater.  It does not require anything
outside of the Python stdlib to function.

Contributors
============

Things to know if you're contributing to pubmarine:

Testing Pubmarine
-----------------

To run the unittests for pubmarine:

.. code-block:: shell-session

    python3 -m pip install --user -r test-requirements.txt
    python3 -m pip install --user -e .
    pytest --cov=pubmarine tests

You can, of course, use a virtualenv instead of ``--user`` to install the
dependencies.
