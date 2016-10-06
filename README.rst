==========
gallery-dl
==========

*gallery-dl* is a small command-line tool to download images and entire image
galleries from several image hosting platforms. It requires Python 3.3+ to run
and works on Unix-like systems as well as Windows.


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


Usage
=====

.. code:: bash

    $ gallery-dl [URL]...


Supported Sites
===============

* Booru:
    behoimi.org, danbooru.donmai.us, e621.net, gelbooru.com, konachan.com,
    rule34.xxx, safebooru.org, chan.sankakucomplex.com, yande.re
* Manga:
    bato.to, dynasty-scans.com, kissmanga.com, kobato.hologfx.com,
    mangahere.co, mangamint.com, mangapanda.com, mangapark.me, mangareader.net,
    mangashare.com, mangastream.com, powermanga.org, raw.senmanga.com,
    thespectrum.net
* Hentai:
    doujinmode.net, exhentai.org, hbrowse.com, hentai2read.com,
    hentaibox.net, hentaihere.com, hitomi.la, luscious.net, nhentai.net
* Japanese:
    pixiv.net, nijie.info, seiga.nicovideo.jp
* Western:
    deviantart.com, hentai-foundry.com, imagefap,com, imgth.com, imgur.com,
    pinterest.com, tumblr.com, twitter.com
* Futaba Channel-like:
    4chan.org, 8ch.net
* Image Hosts:
    chronos.to, coreimg.net, imagebam.com, imagetwist.com, img.yt, imgbox.com,
    imgcandy.net, imgchili.net, imgtrex.com, pic-maniac.com, rapidimg.net,
    turboimagehost.com


Configuration
=============

Configuration files for gallery-dl use a JSON-based file format.
For a (more or less) complete example, see gallery-dl.conf_.

*gallery-dl* searches for configuration files in the following paths:

* ``/etc/gallery-dl.conf``
* ``~/.config/gallery-dl/config.json``
* ``~/.gallery-dl.conf``

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


.. _gallery-dl.conf: https://github.com/mikf/gallery-dl/blob/master/gallery-dl.conf
