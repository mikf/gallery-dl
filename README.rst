==========
gallery-dl
==========

*gallery-dl* is a small command-line tool to download images and entire image galleries from several image hosting platforms.

Installation
============

You can install *gallery-dl* with pip:

.. code:: bash

    $ pip install gallery-dl

or directly from github:

.. code:: bash

    $ git clone https://github.com/mikf/gallery-dl.git
    $ cd gallery-dl
    $ python3 setup.py install

Supported Sites
===============

* images (and ugoira) per artist from pixiv, nijie, deviantart
* images per tag from booru-like sites (danbooru, gelbooru, chan.sankakucomplex, yandere, konachan, safebooru, 3dbooru, e621)
* manga chapters from batoto, kissmanga, mangapanda, mangareader, mangastream, powermanga, redhawkscans
* galleries from exhentai, nhentai, hitomi
* images and videos from threads on Futaba Channel-like boards (4chan, 8chan)

Usage
=====

.. code:: bash

    $ gallery-dl URL [URL...]

Certain supported sites require authentication to download images from. This currently includes pixiv, exhentai, gelbooru and nijie. To make these sites accessible to *gallery-dl* you need to specify the necessary login credentials or cookies in the configuration files.

Configuration
=============

Configuration files for gallery-dl use a JSON-based file format. For a (more or less) complete example, see gallery-dl.conf_.

*gallery-dl* searches for configuration files in the following paths:

* /etc/gallery-dl.conf
* ~/.config/gallery/config.json
* ~/.config/gallery-dl.conf
* ~/.gallery-dl.conf

Values in later configuration files will override previous ones.

.. _gallery-dl.conf: https://github.com/mikf/gallery-dl/blob/master/gallery-dl.conf

