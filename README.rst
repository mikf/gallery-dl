==========
gallery-dl
==========

*gallery-dl* is a command-line program to download image-galleries and
-collections from several image hosting sites such as pixiv.net, exhentai.org,
gelbooru.com and several more (see `Supported Sites`_). It requires Python 3.3+
to run and works on Unix-like systems as well as on Windows.


|pypi| |build|

.. section-numbering::


Installation
============

Installation via pip
--------------------

The stable releases of *gallery-dl* are distributed on PyPI_ and can be
easily installed using pip_:

.. code:: bash

    $ pip install gallery-dl

Installing the latest develop-version directly from GitHub can be done via
pip as well:

.. code:: bash

    $ pip install https://github.com/mikf/gallery-dl/archive/master.zip


Manual installation via Python
------------------------------

Get the code by downloading either the stable_ or develop_ archives and unpack
them, or via `git clone`. Navigate into the respective directory and run the
`setup.py` file.

.. code:: bash

    $ git clone https://github.com/mikf/gallery-dl.git
    $ cd gallery-dl
    $ python setup.py install


Standalone executable (Windows only)
------------------------------------

Windows users can download a `standalone executable`_, which comes with a
Python interpreter and all required packages included.
Put this file in your PATH or use it from the current directory and you are
good to go,


Usage
=====

To use *gallery-dl* simply call it with the URLs you wish to download images
from:

.. code:: bash

    $ gallery-dl [OPTION]... URL...

See also :code:`gallery-dl --help`.


Examples
--------

Download images from gelbooru found via tag search for 'bonocho':

.. code:: bash

    $ gallery-dl "http://gelbooru.com/index.php?page=post&s=list&tags=bonocho"


Get the direct URL of an image from a site that requires authentication:

.. code:: bash

    $ gallery-dl -g -u <username> -p <password> http://seiga.nicovideo.jp/seiga/im3211703


| Search a remote resource for URLs and download images from them:
| (URLs for which no extractor can be found will be silently ignored)

.. code:: bash

    $ gallery-dl r:https://pastebin.com/raw/FLwrCYsT


Supported Sites
===============

* pixiv.net
* seiga.nicovideo.jp
* nijie.info
* bato.to
* mangastream.com
* kissmanga.com
* readcomiconline.to
* danbooru.donmai.us
* gelbooru.com
* exhentai.org
* nhentai.net
* luscious.net
* hentai-foundry.com
* deviantart.com
* tumblr.com
* `Complete List`_


Configuration
=============

Configuration files for *gallery-dl* use a JSON-based file format.
For a (more or less) complete example, see gallery-dl.conf_.

*gallery-dl* searches for configuration files in the following paths:

+--------------------------------------------+------------------------------------------+
| Linux                                      | Windows                                  |
+--------------------------------------------+------------------------------------------+
|* ``/etc/gallery-dl.conf``                  |*                                         |
|* ``${HOME}/.config/gallery-dl/config.json``|* ``%USERPROFILE%\gallery-dl\config.json``|
|* ``${HOME}/.gallery-dl.conf``              |* ``%USERPROFILE%\gallery-dl.conf``       |
+--------------------------------------------+------------------------------------------+

(``%USERPROFILE%`` usually refers to the users home directory,
i.e. ``C:\Users\<username>\``)

Values in later configuration files will override previous ones.


Authentication
==============

Some extractors require you to provide valid login-credentials.
This currently includes ``pixiv``, ``exhentai``, ``nijie``, ``seiga``
and ``batoto``.

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


.. _gallery-dl.conf:       https://github.com/mikf/gallery-dl/blob/master/docs/gallery-dl.conf
.. _Complete List:         https://github.com/mikf/gallery-dl/blob/master/docs/supportedsites.rst
.. _standalone executable: https://github.com/mikf/gallery-dl/releases/download/v0.8.3/gallery-dl.exe
.. _Python:   https://www.python.org/downloads/
.. _Requests: https://pypi.python.org/pypi/requests/
.. _PyPI:     https://pypi.python.org/pypi
.. _pip:      https://pip.pypa.io/en/stable/
.. _stable:   https://github.com/mikf/gallery-dl/archive/v0.8.3.zip
.. _develop:  https://github.com/mikf/gallery-dl/archive/master.zip

.. |pypi| image:: https://img.shields.io/pypi/v/gallery-dl.svg
    :target: https://pypi.python.org/pypi/gallery-dl

.. |build| image:: https://travis-ci.org/mikf/gallery-dl.svg?branch=master
    :target: https://travis-ci.org/mikf/gallery-dl
