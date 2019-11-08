==========
gallery-dl
==========

*gallery-dl* is a command-line program to download image-galleries and
-collections from several image hosting sites (see `Supported Sites`_).
It is a cross-platform tool with many configuration options
and powerful filenaming capabilities.


|pypi| |build| |gitter|


Dependencies
============

- Python_ 3.4+
- Requests_

Optional
--------

- FFmpeg_: Pixiv Ugoira to WebM conversion
- youtube-dl_: Video downloads
- pyOpenSSL_: Access Cloudflare protected sites


Installation
============

Pip
---

The stable releases of *gallery-dl* are distributed on PyPI_ and can be
easily installed or upgraded using pip_:

.. code:: bash

    $ python3 -m pip install --upgrade gallery-dl

Installing the latest dev-version directly from GitHub can be done with
pip_ as well:

.. code:: bash

    $ python3 -m pip install --upgrade https://github.com/mikf/gallery-dl/archive/master.tar.gz

Note: Windows users should use :code:`py -3` instead of :code:`python3`.

| It is advised to use the latest version of pip_,
  including the essential packages :code:`setuptools` and :code:`wheel`.
| To ensure that these packages are up-to-date, run

.. code:: bash

    $ python3 -m pip install --upgrade pip setuptools wheel


From Source
-----------

Get the code by either

* Downloading a stable_ or dev_ archive and unpacking it
* Or via :code:`git clone https://github.com/mikf/gallery-dl.git`

Navigate into the respective directory and run the :code:`setup.py` file.

.. code:: bash

    $ wget https://github.com/mikf/gallery-dl/archive/master.tar.gz
    $ tar -xf master.tar.gz
    # or
    $ git clone https://github.com/mikf/gallery-dl.git

    $ cd gallery-dl*
    $ python3 setup.py install


Standalone Executable
---------------------

Download a standalone executable file,
put it into your `PATH <https://en.wikipedia.org/wiki/PATH_(variable)>`__,
and run it inside a command prompt (like ``cmd.exe``).

- `Windows <https://github.com/mikf/gallery-dl/releases/download/v1.10.6/gallery-dl.exe>`__
- `Linux   <https://github.com/mikf/gallery-dl/releases/download/v1.10.6/gallery-dl.bin>`__

These executables include a Python 3.7 interpreter
and all required Python packages.


Snap
----

Linux users that are using a distro that is supported by Snapd_ can install *gallery-dl* from the Snap Store:

.. code:: bash

    $ snap install gallery-dl


Usage
=====

To use *gallery-dl* simply call it with the URLs you wish to download images
from:

.. code:: bash

    $ gallery-dl [OPTION]... URL...

See also :code:`gallery-dl --help`.


Examples
--------

Download images; in this case from danbooru via tag search for 'bonocho':

.. code:: bash

    $ gallery-dl http://danbooru.donmai.us/posts?tags=bonocho


Get the direct URL of an image from a site that requires authentication:

.. code:: bash

    $ gallery-dl -g -u <username> -p <password> http://seiga.nicovideo.jp/seiga/im3211703


| Search a remote resource for URLs and download images from them:
| (URLs for which no extractor can be found will be silently ignored)

.. code:: bash

    $ gallery-dl r:https://pastebin.com/raw/FLwrCYsT


Configuration
=============

Configuration files for *gallery-dl* use a JSON-based file format.

| For a (more or less) complete example with options set to their default values,
  see gallery-dl.conf_.
| For a configuration file example with more involved settings and options,
  see gallery-dl-example.conf_.
| A list of all available configuration options and their
  descriptions can be found in configuration.rst_.

*gallery-dl* searches for configuration files in the following places:

+--------------------------------------------+------------------------------------------+
| Linux                                      | Windows                                  |
+--------------------------------------------+------------------------------------------+
|* ``/etc/gallery-dl.conf``                  |*                                         |
|* ``${HOME}/.config/gallery-dl/config.json``|* ``%USERPROFILE%\gallery-dl\config.json``|
|* ``${HOME}/.gallery-dl.conf``              |* ``%USERPROFILE%\gallery-dl.conf``       |
+--------------------------------------------+------------------------------------------+

(``%USERPROFILE%`` usually refers to the user's home directory,
i.e. ``C:\Users\<username>\``)

Values in later configuration files will override previous ones.


Authentication
==============

Username & Password
-------------------

Some extractors require you to provide valid login-credentials in the form of
a username & password pair. This is necessary for
``pixiv``, ``nijie``, and ``seiga``
and optional (but strongly recommended) for
``danbooru``, ``exhentai``, ``idolcomplex``, ``instagram``,
``luscious``, ``sankaku``, ``tsumino``, and ``twitter``.

You can set the necessary information in your configuration file
(cf. gallery-dl.conf_)

.. code::

    {
        "extractor": {
            ...
            "pixiv": {
                "username": "<username>",
                "password": "<password>"
            }
            ...
        }
    }

or you can provide them directly via the
:code:`-u/--username` and :code:`-p/--password` or via the
:code:`-o/--option` command-line options

.. code:: bash

    $ gallery-dl -u <username> -p <password> URL
    $ gallery-dl -o username=<username> -o password=<password> URL

OAuth
-----

*gallery-dl* supports user authentication via OAuth_ for
``deviantart``, ``flickr``, ``reddit``, ``smugmug`` and ``tumblr``.
This is entirely optional, but grants *gallery-dl* the ability
to issue requests on your account's behalf and enables it to access resources
which would otherwise be unavailable to a public user.

To link your account to *gallery-dl*, start by invoking it with
``oauth:<site-name>`` as an argument. For example:

.. code:: bash

    $ gallery-dl oauth:flickr

You will be sent to the site's authorization page and asked to grant read
access to *gallery-dl*. Authorize it and you will be shown one or more
"tokens", which should be added to your configuration file.


.. _gallery-dl.conf:         https://github.com/mikf/gallery-dl/blob/master/docs/gallery-dl.conf
.. _gallery-dl-example.conf: https://github.com/mikf/gallery-dl/blob/master/docs/gallery-dl-example.conf
.. _configuration.rst:       https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst
.. _Supported Sites:         https://github.com/mikf/gallery-dl/blob/master/docs/supportedsites.rst
.. _stable:                  https://github.com/mikf/gallery-dl/archive/v1.10.6.zip
.. _dev:                     https://github.com/mikf/gallery-dl/archive/master.zip

.. _Python:     https://www.python.org/downloads/
.. _PyPI:       https://pypi.org/
.. _pip:        https://pip.pypa.io/en/stable/
.. _Requests:   https://requests.readthedocs.io/en/master/
.. _FFmpeg:     https://www.ffmpeg.org/
.. _youtube-dl: https://ytdl-org.github.io/youtube-dl/
.. _pyOpenSSL:  https://pyopenssl.org/
.. _Snapd:      https://docs.snapcraft.io/installing-snapd
.. _OAuth:      https://en.wikipedia.org/wiki/OAuth

.. |pypi| image:: https://img.shields.io/pypi/v/gallery-dl.svg
    :target: https://pypi.org/project/gallery-dl/

.. |build| image:: https://travis-ci.org/mikf/gallery-dl.svg?branch=master
    :target: https://travis-ci.org/mikf/gallery-dl

.. |gitter| image:: https://badges.gitter.im/gallery-dl/main.svg
    :target: https://gitter.im/gallery-dl/main
