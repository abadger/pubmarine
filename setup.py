from distutils.core import setup

setup(name="pubmarine",
        version="0.1",
        description="PubSub for Python-3.5's asyncio",
        author="Toshio Kuratomi",
        author_email="toshio@fedoraproject.org",
        maintainer="Toshio Kuratomi",
        maintainer_email="toshio@fedoraproject.org",
        license="Lesser GNU Public License v3+",
        keywords='pubsub events',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.5',
        ],
        packages=['pubmarine'],
    )
