from distutils.core import setup

import pubmarine


with open('README.rst', 'r') as f:
    long_desc = f.read()

setup(name="pubmarine",
      version='%s.1' % pubmarine.__version__,
      description="An event dispatcher based on the PubSub pattern for Python-3.5's asyncio",
      long_description=long_desc,
      long_description_content_type="text/x-rst",
      author="Toshio Kuratomi",
      author_email="toshio@fedoraproject.org",
      maintainer="Toshio Kuratomi",
      maintainer_email="toshio@fedoraproject.org",
      url="https://github.com/abadger/pubmarine",
      license="Lesser GNU Public License v3+",
      keywords='pubsub events',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      packages=['pubmarine'],
      )
