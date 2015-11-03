==========
gallery-dl
==========

gallery-dl is a image gallery downloader for several image hosting platforms.

Installation
------------

Via pip:

.. code:: bash

    $ pip install gallery-dl

Or from github:

.. code:: bash

    $ git clone https://github.com/mikf/gallery-dl.git
    $ cd gallery-dl
    $ python3 setup.py install

Usage
-----

.. code:: bash

    $ gallery-dl URL [URL...]

Configuration
-------------

Configuration files for gallery-dl use a JSON-based file format. For a (more or less) complete example, see gallery-dl.conf_.

gallery-dl searches for configuration files in the following paths:

* /etc/gallery-dl.conf
* ~/.config/gallery/config.json
* ~/.config/gallery-dl.conf
* ~/.gallery-dl.conf

Values in later configuration files will override previous ones.

.. _gallery-dl.conf: https://github.com/mikf/gallery-dl/blob/master/gallery-dl.conf

