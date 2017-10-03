Making a Release
================

* Make sure changes have been recorded using `reno`_.
* Update the release in pubmarine/__init__.py
* Regenerate release notes using `reno`_.
* git push
* Check that tests are passing in `travis`_.
* git tag the release
* git push the release to github
* git clone a fresh copy
* python3 setup.py sdist
* check that the dist is sane (same as what's in the repository.  No extra files.  No missing files)
* python3 setup.py sdist --upload --sign

* Make sdist

.. reno:: https://docs.openstack.org/reno/latest/user/usage.html
.. travis:: https://travis-ci.org/abadger/pubmarine
