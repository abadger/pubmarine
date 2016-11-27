from distutils.core import setup

setup(name="pubmarine",
        version="0.3",
        description="An event dispatcher based on the PubSub pattern for Python-3.5's asyncio",
        long_description="""
This module implements and event dispatcher based on the publish-subscribe
pattern using asyncio.  It is akin to the QT library's signals and slots
mechanism.  Pubmarine's PubSub is intended for asynchronous signalling within
an application.  It is not meant for communicating with other programs over
the network.
        """,
        author="Toshio Kuratomi",
        author_email="toshio@fedoraproject.org",
        maintainer="Toshio Kuratomi",
        maintainer_email="toshio@fedoraproject.org",
        url="https://github.com/abadger/pubmarine",
        license="Lesser GNU Public License v3+",
        keywords='pubsub events',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        packages=['pubmarine'],
    )
