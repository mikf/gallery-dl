==========
gallery-dl
==========

*gallery-dl* is a command-line program
to download image galleries and collections
from several image hosting sites
(see `Supported Sites <docs/supportedsites.md>`__).
It is a cross-platform tool
with many `configuration options <https://gdl-org.github.io/docs/configuration.html>`__
and powerful `filenaming capabilities <https://gdl-org.github.io/docs/formatting.html>`__.


|pypi| |build|

.. contents::


Dependencies
============

- Python_ 3.4+
- Requests_

Optional
--------

- yt-dlp_ or youtube-dl_: HLS/DASH video downloads, ``ytdl`` integration
- FFmpeg_: Pixiv Ugoira conversion
- mkvmerge_: Accurate Ugoira frame timecodes
- PySocks_: SOCKS proxy support
- brotli_ or brotlicffi_: Brotli compression support
- zstandard_: Zstandard compression support
- PyYAML_: YAML configuration file support
- toml_: TOML configuration file support for Python<3.11
- SecretStorage_: GNOME keyring passwords for ``--cookies-from-browser``
- Psycopg_: PostgreSQL archive support


Installation
============


Pip
---

The stable releases of *gallery-dl* are distributed on PyPI_ and can be
easily installed or upgraded using pip_:

.. code:: bash

    python3 -m pip install -U gallery-dl

Installing the latest dev version directly from GitHub can be done with
pip_ as well:

.. code:: bash

    python3 -m pip install -U --force-reinstall --no-deps https://github.com/mikf/gallery-dl/archive/master.tar.gz

Omit :code:`--no-deps` if Requests_ hasn't been installed yet.

Note: Windows users should use :code:`py -3` instead of :code:`python3`.

It is advised to use the latest version of pip_,
including the essential packages :code:`setuptools` and :code:`wheel`.
To ensure these packages are up-to-date, run

.. code:: bash

    python3 -m pip install --upgrade pip setuptools wheel


Standalone Executable
---------------------

Prebuilt executable files with a Python interpreter and
required Python packages included are available for

- `Windows <https://github.com/mikf/gallery-dl/releases/download/v1.29.4/gallery-dl.exe>`__
  (Requires `Microsoft Visual C++ Redistributable Package (x86) <https://aka.ms/vs/17/release/vc_redist.x86.exe>`__)
- `Linux   <https://github.com/mikf/gallery-dl/releases/download/v1.29.4/gallery-dl.bin>`__


Nightly Builds
--------------

| Executables build from the latest commit can be found at
| https://github.com/gdl-org/builds/releases


Snap
----

Linux users that are using a distro that is supported by Snapd_ can install *gallery-dl* from the Snap Store:

.. code:: bash

    snap install gallery-dl


Chocolatey
----------

Windows users that have Chocolatey_ installed can install *gallery-dl* from the Chocolatey Community Packages repository:

.. code:: powershell

    choco install gallery-dl


Scoop
-----

*gallery-dl* is also available in the Scoop_ "main" bucket for Windows users:

.. code:: powershell

    scoop install gallery-dl

Homebrew
--------

For macOS or Linux users using Homebrew:

.. code:: bash

    brew install gallery-dl

MacPorts
--------

For macOS users with MacPorts:

.. code:: bash

    sudo port install gallery-dl

Docker
--------
Using the Dockerfile in the repository:

.. code:: bash

    git clone https://github.com/mikf/gallery-dl.git
    cd gallery-dl/
    docker build -t gallery-dl:latest .

Pulling image from `Docker Hub <https://hub.docker.com/r/mikf123/gallery-dl>`__:

.. code:: bash

    docker pull mikf123/gallery-dl
    docker tag mikf123/gallery-dl gallery-dl

Pulling image from `GitHub Container Registry <https://github.com/mikf/gallery-dl/pkgs/container/gallery-dl>`__:

.. code:: bash

    docker pull ghcr.io/mikf/gallery-dl
    docker tag ghcr.io/mikf/gallery-dl gallery-dl

To run the container you will probably want to attach some directories on the host so that the config file and downloads can persist across runs.

Make sure to either download the example config file reference in the repo and place it in the mounted volume location or touch an empty file there.

If you gave the container a different tag or are using podman then make sure you adjust.  Run ``docker image ls`` to check the name if you are not sure.

This will remove the container after every use so you will always have a fresh environment for it to run. If you setup a ci-cd pipeline to autobuild the container you can also add a ``--pull=newer`` flag so that when you run it docker will check to see if there is a newer container and download it before running.

.. code:: bash

    docker run --rm  -v $HOME/Downloads/:/gallery-dl/ -v $HOME/.config/gallery-dl/gallery-dl.conf:/etc/gallery-dl.conf -it gallery-dl:latest

You can also add an alias to your shell for "gallery-dl" or create a simple bash script and drop it somewhere in your $PATH to act as a shim for this command.

Nix and Home Manager
--------------------------

Adding *gallery-dl* to your system environment:

.. code:: nix

    environment.systemPackages = with pkgs; [
      gallery-dl
    ];

Using :code:`nix-shell`

.. code:: bash

    nix-shell -p gallery-dl

.. code:: bash

    nix-shell -p gallery-dl --run "gallery-dl <args>"

For Home Manager users, you can manage *gallery-dl* declaratively:

.. code:: nix

    programs.gallery-dl = {
      enable = true;
      settings = {
        extractor.base-directory = "~/Downloads";
      };
    };

Alternatively, you can just add it to :code:`home.packages` if you don't want to manage it declaratively:

.. code:: nix

    home.packages = with pkgs; [
      gallery-dl
    ];

After making these changes, simply rebuild your configuration and open a new shell to have *gallery-dl* available.

Usage
=====

To use *gallery-dl* simply call it with the URLs you wish to download images
from:

.. code:: bash

    gallery-dl [OPTIONS]... URLS...

Use :code:`gallery-dl --help` or see `<docs/options.md>`__
for a full list of all command-line options.


Examples
--------

Download images; in this case from danbooru via tag search for 'bonocho':

.. code:: bash

    gallery-dl "https://danbooru.donmai.us/posts?tags=bonocho"


Get the direct URL of an image from a site supporting authentication with username & password:

.. code:: bash

    gallery-dl -g -u "<username>" -p "<password>" "https://twitter.com/i/web/status/604341487988576256"


Filter manga chapters by chapter number and language:

.. code:: bash

    gallery-dl --chapter-filter "10 <= chapter < 20" -o "lang=fr" "https://mangadex.org/title/59793dd0-a2d8-41a2-9758-8197287a8539"


| Search a remote resource for URLs and download images from them:
| (URLs for which no extractor can be found will be silently ignored)

.. code:: bash

    gallery-dl "r:https://pastebin.com/raw/FLwrCYsT"


If a site's address is nonstandard for its extractor, you can prefix the URL with the
extractor's name to force the use of a specific extractor:

.. code:: bash

    gallery-dl "tumblr:https://sometumblrblog.example"


Configuration
=============

Configuration files for *gallery-dl* use a JSON-based file format.


Documentation
-------------

A list of all available configuration options and their descriptions
can be found at `<https://gdl-org.github.io/docs/configuration.html>`__.

| For a default configuration file with available options set to their
  default values, see `<docs/gallery-dl.conf>`__.

| For a commented example with more involved settings and option usage,
  see `<docs/gallery-dl-example.conf>`__.


Locations
---------

*gallery-dl* searches for configuration files in the following places:

Windows:
    * ``%APPDATA%\gallery-dl\config.json``
    * ``%USERPROFILE%\gallery-dl\config.json``
    * ``%USERPROFILE%\gallery-dl.conf``

    (``%USERPROFILE%`` usually refers to a user's home directory,
    i.e. ``C:\Users\<username>\``)

Linux, macOS, etc.:
    * ``/etc/gallery-dl.conf``
    * ``${XDG_CONFIG_HOME}/gallery-dl/config.json``
    * ``${HOME}/.config/gallery-dl/config.json``
    * ``${HOME}/.gallery-dl.conf``

When run as `executable <Standalone Executable_>`__,
*gallery-dl* will also look for a ``gallery-dl.conf`` file
in the same directory as said executable.

It is possible to use more than one configuration file at a time.
In this case, any values from files after the first will get merged
into the already loaded settings and potentially override previous ones.


Authentication
==============

Username & Password
-------------------

Some extractors require you to provide valid login credentials in the form of
a username & password pair. This is necessary for
``nijie``
and optional for
``aryion``,
``danbooru``,
``e621``,
``exhentai``,
``idolcomplex``,
``imgbb``,
``inkbunny``,
``mangadex``,
``mangoxo``,
``pillowfort``,
``sankaku``,
``subscribestar``,
``tapas``,
``tsumino``,
``twitter``,
and ``zerochan``.

You can set the necessary information in your
`configuration file <Configuration_>`__

.. code:: json

    {
        "extractor": {
            "twitter": {
                "username": "<username>",
                "password": "<password>"
            }
        }
    }

or you can provide them directly via the
:code:`-u/--username` and :code:`-p/--password` or via the
:code:`-o/--option` command-line options

.. code:: bash

    gallery-dl -u "<username>" -p "<password>" "URL"
    gallery-dl -o "username=<username>" -o "password=<password>" "URL"


Cookies
-------

For sites where login with username & password is not possible due to
CAPTCHA or similar, or has not been implemented yet, you can use the
cookies from a browser login session and input them into *gallery-dl*.

This can be done via the
`cookies <https://gdl-org.github.io/docs/configuration.html#extractor-cookies>`__
option in your configuration file by specifying

- | the path to a Mozilla/Netscape format cookies.txt file exported by a browser addon
  | (e.g. `Get cookies.txt LOCALLY <https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc>`__ for Chrome,
    `Export Cookies <https://addons.mozilla.org/en-US/firefox/addon/export-cookies-txt/>`__ for Firefox)

- | a list of name-value pairs gathered from your browser's web developer tools
  | (in `Chrome <https://developers.google.com/web/tools/chrome-devtools/storage/cookies>`__,
     in `Firefox <https://developer.mozilla.org/en-US/docs/Tools/Storage_Inspector>`__)

- | the name of a browser to extract cookies from
  | (supported browsers are Chromium-based ones, Firefox, and Safari)

For example:

.. code:: json

    {
        "extractor": {
            "instagram": {
                "cookies": "$HOME/path/to/cookies.txt"
            },
            "patreon": {
                "cookies": {
                    "session_id": "K1T57EKu19TR49C51CDjOJoXNQLF7VbdVOiBrC9ye0a"
                }
            },
            "twitter": {
                "cookies": ["firefox"]
            }
        }
    }

| You can also specify a cookies.txt file with
  the :code:`--cookies` command-line option
| or a browser to extract cookies from with :code:`--cookies-from-browser`:

.. code:: bash

    gallery-dl --cookies "$HOME/path/to/cookies.txt" "URL"
    gallery-dl --cookies-from-browser firefox "URL"


OAuth
-----

*gallery-dl* supports user authentication via OAuth_ for some extractors.
This is necessary for
``pixiv``
and optional for
``deviantart``,
``flickr``,
``reddit``,
``smugmug``,
``tumblr``,
and ``mastodon`` instances.

Linking your account to *gallery-dl* grants it the ability to issue requests
on your account's behalf and enables it to access resources which would
otherwise be unavailable to a public user.

To do so, start by invoking it with ``oauth:<sitename>`` as an argument.
For example:

.. code:: bash

    gallery-dl oauth:flickr

You will be sent to the site's authorization page and asked to grant read
access to *gallery-dl*. Authorize it and you will be shown one or more
"tokens", which should be added to your configuration file.

To authenticate with a ``mastodon`` instance, run *gallery-dl* with
``oauth:mastodon:<instance>`` as argument. For example:

.. code:: bash

    gallery-dl oauth:mastodon:pawoo.net
    gallery-dl oauth:mastodon:https://mastodon.social/


.. _Python:     https://www.python.org/downloads/
.. _PyPI:       https://pypi.org/
.. _pip:        https://pip.pypa.io/en/stable/
.. _Requests:   https://requests.readthedocs.io/en/master/
.. _FFmpeg:     https://www.ffmpeg.org/
.. _mkvmerge:   https://www.matroska.org/downloads/mkvtoolnix.html
.. _yt-dlp:     https://github.com/yt-dlp/yt-dlp
.. _youtube-dl: https://ytdl-org.github.io/youtube-dl/
.. _PySocks:    https://pypi.org/project/PySocks/
.. _brotli:     https://github.com/google/brotli
.. _brotlicffi: https://github.com/python-hyper/brotlicffi
.. _zstandard:  https://github.com/indygreg/python-zstandard
.. _PyYAML:     https://pyyaml.org/
.. _toml:       https://pypi.org/project/toml/
.. _SecretStorage: https://pypi.org/project/SecretStorage/
.. _Psycopg:    https://www.psycopg.org/
.. _Snapd:      https://docs.snapcraft.io/installing-snapd
.. _OAuth:      https://en.wikipedia.org/wiki/OAuth
.. _Chocolatey: https://chocolatey.org/install
.. _Scoop:      https://scoop.sh

.. |pypi| image:: https://img.shields.io/pypi/v/gallery-dl.svg
    :target: https://pypi.org/project/gallery-dl/

.. |build| image:: https://github.com/mikf/gallery-dl/workflows/tests/badge.svg
    :target: https://github.com/mikf/gallery-dl/actions

.. |gitter| image:: https://badges.gitter.im/gallery-dl/main.svg
    :target: https://gitter.im/gallery-dl/main
