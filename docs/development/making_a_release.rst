Making a Release
================

* Make sure changes have been recorded using `reno`_.

    * ``reno new --edit [SLUG]``

* Update the version info in :file:`pubmarine/__init__.py` for the release
* Regenerate release notes using `reno`_.

    * ``reno report .> NEWS``
    * Edit :file:`NEWS` to adjust the version number for the release.  Since there's no tag for the new
      release yet, the version has to be bumped manually in this file.

* ``git push``
* Check that tests are passing in `travis`_.
* git tag the release
* ``git push --tags``
* git clone a fresh copy
* git checkout the tag
* ``python3 setup.py sdist``
* check that the dist is sane (same as what's in the repository.  No extra files.  No missing files)
* ``python3 setup.py sdist --upload --sign``

.. _reno: https://docs.openstack.org/reno/latest/user/usage.html
.. _travis: https://travis-ci.org/abadger/pubmarine
