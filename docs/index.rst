.. Pubmarine documentation master file, created by
   sphinx-quickstart on Tue Sep 12 22:28:56 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Pubmarine's documentation!
=====================================

Pubmarine is an implementation of the publish-subscribe pattern for asyncio.  It is used for
intra-process communication.  "What's that", you ask, "Intra-process?"  Yep.  Intra-process.  When you create
a program that has multiple threads of control, you sometimes need an easy way to communicate
between the various pieces.  That's where pubmarine comes in.  It provides a few functions to
subscribe one thread of control to a topic and then publish events to the topic from another thread.

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    getting_started
    api
    development/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
