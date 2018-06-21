Configuration
#############

Contents
========

1) `Extractor Options`_
2) `Extractor-specific Options`_
3) `Downloader Options`_
4) `Output Options`_
5) `Postprocessor Options`_
6) `Miscellaneous Options`_
7) `API Tokens & IDs`_


Extractor Options
=================

Each extractor is identified by its ``category`` and ``subcategory``.
The ``category`` is the lowercase site name without any spaces or special
characters, which is usually just the module name
(``pixiv``, ``danbooru``, ...).
The ``subcategory`` is a lowercase word describing the general functionality
of that extractor (``user``, ``favorite``, ``manga``, ...).

Each one of the following options can be specified on multiple levels of the
configuration tree:

================== =====
Base level:        ``extractor.<option-name>``
Category level:    ``extractor.<category>.<option-name>``
Subcategory level: ``extractor.<category>.<subcategory>.<option-name>``
================== =====

A value in a "deeper" level hereby overrides a value of the same name on a
lower level. Setting the ``extractor.pixiv.filename`` value, for example, lets
you specify a general filename pattern for all the different pixiv extractors.
Using the ``extractor.pixiv.user.filename`` value lets you override this
general pattern specifically for ``PixivUserExtractor`` instances.

The ``category`` and ``subcategory`` of all extractors are included in the
output of ``gallery-dl --list-extractors``. For a specific URL these values
can also be determined by using the ``-K``/``--list-keywords`` command-line
option (see the example below).

extractor.*.filename
--------------------
=========== =====
Type        ``string``
Example     ``"{manga}_c{chapter}_{page:>03}.{extension}"``
Description A `format string`_ to build the resulting filename
            for a downloaded file.

            The available replacement keys depend on the extractor used. A list
            of keys for a specific one can be acquired by calling *gallery-dl*
            with the ``-K``/``--list-keywords`` command-line option.
            For example:

            .. code::

                $ gallery-dl -K http://seiga.nicovideo.jp/seiga/im5977527
                Keywords for directory names:
                -----------------------------
                category
                  seiga
                subcategory
                  image

                Keywords for filenames:
                -----------------------
                category
                  seiga
                extension
                  None
                image-id
                  5977527
                subcategory
                  image

            Note that even if the value of the ``extension`` key is missing or
            ``None``, it will filled in later when the file download is
            starting. This key is therefore always available to provide
            a valid filename extension.
=========== =====


extractor.*.directory
---------------------
=========== =====
Type        ``list`` of ``strings``
Example     ``["{category}", "{manga}", "c{chapter} - {title}"]``
Description A list of `format strings`_ for the resulting target directory.

            Each individual string in such a list represents a single path
            segment, which will be joined together and appended to the
            base-directory_ to form the complete target directory path.
=========== =====


extractor.*.base-directory
--------------------------
=========== =====
Type        |Path|_
Default     ``"./gallery-dl/"``
Description Directory path used as the base for all download destinations.
=========== =====


extractor.*.skip
----------------
=========== =====
Type        ``bool`` or ``string``
Default     ``true``
Description Controls the behavior when downloading a file whose filename
            already exists.

            * ``true``: Skip the download
            * ``false``: Overwrite the already existing file
            * ``"abort"``: Abort the current extractor run
            * ``"exit"``: Exit the program altogether
=========== =====


extractor.*.sleep
-----------------
=========== =====
Type        ``float``
Default     ``0``
Description Number of seconds to sleep before each download.
=========== =====


extractor.*.username & .password
--------------------------------
=========== =====
Type        ``string``
Default     ``null``
Description The username and password to use when attempting to log in to
            another site.

            Specifying username and password is
            required for the ``pixiv``, ``nijie`` and ``seiga`` modules and
            optional (but strongly recommended) for ``exhentai``,
            ``sankaku`` and ``idolcomplex``.

            These values can also be set via the ``-u/--username`` and
            ``-p/--password`` command-line options or by using a |.netrc|_ file.
            (see Authentication_)
=========== =====


extractor.*.cookies
-------------------
=========== =====
Type        |Path|_ or ``object``
Default     ``null``
Description Source to read additional cookies from.

            * If this is a |Path|_, it specifies a
              Mozilla/Netscape format cookies.txt file.
            * If this is an ``object``, its key-value pairs, which should both
              be ``strings``, will be used as cookie-names and -values.
=========== =====


extractor.*.proxy
-----------------
=========== =====
Type        ``string`` or ``object``
Default     ``null``
Description Proxy (or proxies) to be used for remote connections.

            * If this is a ``string``, it is the proxy URL for all
              outgoing requests.
            * If this is an ``object``, it is a scheme-to-proxy mapping to
              specify different proxy URLs for each scheme.
              It is also possible to set a proxy for a specific host by using
              ``scheme://host`` as key.
              See `Requests' proxy documentation`_ for more details.

              Example:

              .. code::

                {
                    "http": "http://10.10.1.10:3128",
                    "https": "http://10.10.1.10:1080",
                    "http://10.20.1.128": "http://10.10.1.10:5323"
                }

            Note that all proxy URLs should include a scheme,
            otherwise ``http://`` is assumed.
=========== =====


extractor.*.user-agent
----------------------
=========== =====
Type        ``string``
Default     ``"Mozilla/5.0 (X11; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0"``
Description User-Agent header value to be used for HTTP requests.

            Note that this option has no effect on `pixiv` and
            `readcomiconline` extractors, as these need specific values to
            function correctly.
=========== =====


extractor.*.keywords
--------------------
=========== =====
Type        ``object``
Example     ``{"type": "Pixel Art", "type_id": 123}``
Description Additional key-value pairs to be added to each metadata dictionary.
=========== =====


extractor.*.keywords-default
----------------------------
=========== =====
Type        any
Default     ``"None"``
Description Default value used for missing or undefined keyword names in
            format strings.
=========== =====


extractor.*.archive
-------------------
=========== =====
Type        |Path|_
Default     ``null``
Description File to store IDs of downloaded files in. Downloads of files
            already recorded in this archive file will be skipped_.

            The resulting archive file is not a plain text file but an SQLite3
            database, as either lookup operations are significantly faster or
            memory requirements are significantly lower when the
            amount of stored IDs gets reasonably large.
=========== =====


extractor.*.archive-format
--------------------------
=========== =====
Type        ``string``
Example     ``"{id}_{offset}"``
Description An alternative `format string`_ to build archive IDs with.
=========== =====


extractor.*.postprocessors
--------------------------
=========== =====
Type        ``list`` of |Postprocessor Configuration|_ objects
Example     .. code::

                [
                    {"name": "zip", "compression": "zip"},
                    {"name": "exec",  "command": ["/home/asd/script", "{category}", "{image_id}"]}
                ]

Description A list of post-processors to be applied to each downloaded file
            in the same order as they are specified.
=========== =====



Extractor-specific Options
==========================

extractor.artstation.external
-----------------------------
=========== =====
Type        ``bool``
Default     ``false``
Description Try to follow external URLs of embedded players.
=========== =====


extractor.deviantart.flat
-------------------------
=========== =====
Type        ``bool``
Default     ``true``
Description Select the directory structure created by the Gallery- and
            Favorite-Extractors.

            * ``true``: Use a flat directory structure.
            * ``false``: Collect a list of all gallery-folders or
              favorites-collections and transfer any further work to other
              extractors (``folder`` or ``collection``), which will then
              create individual subdirectories for each of them.
=========== =====


extractor.deviantart.mature
---------------------------
=========== =====
Type        ``bool``
Default     ``true``
Description Enable mature content.

            This option simply sets the |mature_content|_ parameter for API
            calls to either ``"true"`` or ``"false"`` and does not do any other
            form of content filtering.
=========== =====


extractor.deviantart.original
-----------------------------
=========== =====
Type        ``bool``
Default     ``true``
Description Download full-sized original images if available.

            Some of DeviantArt's images require an additional API call to get
            their actual original version, which is being hosted on
            Amazon Web Services (AWS) servers.
=========== =====


extractor.deviantart.refresh-token
----------------------------------
=========== =====
Type        ``string``
Default     ``null``
Description The ``refresh_token`` value you get from linking your
            DeviantArt account to *gallery-dl*.

            Using a ``refresh_token`` allows you to access private or otherwise
            not publicly available deviations.
=========== =====


extractor.exhentai.original
---------------------------
=========== =====
Type        ``bool``
Default     ``true``
Description Download full-sized original images if available.
=========== =====


extractor.exhentai.wait-min & .wait-max
---------------------------------------
=========== =====
Type        ``float``
Default     ``3.0`` and ``6.0``
Description Minimum and maximum wait time in seconds between each image

            ExHentai detects and blocks automated downloaders.
            *gallery-dl* waits a randomly selected number of
            seconds between ``wait-min`` and ``wait-max`` after
            each image to prevent getting blocked.
=========== =====


extractor.flickr.access-token & .access-token-secret
----------------------------------------------------
=========== =====
Type        ``string``
Default     ``null``
Description The ``access_token`` and ``access_token_secret`` values you get
            from linking your Flickr account to *gallery-dl*.
=========== =====


extractor.flickr.metadata
-------------------------
=========== =====
Type        ``bool``
Default     ``false``
Description Load additional metadata when using the single-image extractor.
=========== =====


extractor.flickr.size-max
--------------------------
=========== =====
Type        ``integer`` or ``string``
Default     ``null``
Description Sets the maximum allowed size for downloaded images.

            * If this is an ``integer``, it specifies the maximum image dimension
              (width and height) in pixels.
            * If this is a ``string``, it should be one of Flickr's format specifiers
              (``"Original"``, ``"Large"``, ... or ``"o"``, ``"k"``, ``"h"``,
              ``"l"``, ...) to use as an upper limit.
=========== =====


extractor.gelbooru.api
----------------------
=========== =====
Type        ``bool``
Default     ``true``
Description Enable use of Gelbooru's API.

            Set this value to `false` if the API has been disabled to switch
            to manual information extraction.
=========== =====


extractor.gfycat.format
-----------------------
=========== =====
Type        ``string``
Default     ``"mp4"``
Description The name of the preferred animation format, which can be one of
            ``"mp4"``, ``"webm"``, ``"gif"``, ``"webp"`` or ``"mjpg"``.

            If the selected format is not available, ``"mp4"``, ``"webm"``
            and ``"gif"`` (in that order) will be tried instead, until an
            available format is found.
=========== =====


extractor.imgur.mp4
-------------------
=========== =====
Type        ``bool`` or ``string``
Default     ``true``
Description Controls whether to choose the GIF or MP4 version of an animation.

            * ``true``: Follow Imgur's advice and choose MP4 if the
              ``prefer_video`` flag in an image's metadata is set.
            * ``false``: Always choose GIF.
            * ``"always"``: Always choose MP4.
=========== =====


extractor.oauth.browser
-----------------------
=========== =====
Type        ``bool``
Default     ``true``
Description Controls how a user is directed to an OAuth authorization site.

            * ``true``: Use Python's |webbrowser.open()|_ method to automatically
              open the URL in the user's browser.
            * ``false``: Ask the user to copy & paste an URL from the terminal.
=========== =====


extractor.pixiv.ugoira
----------------------
=========== =====
Type        ``bool``
Default     ``true``
Description Download Pixiv's Ugoira animations or ignore them.

            These animations come as a ``.zip`` file containing all the single
            animation frames in JPEG format.
=========== =====


extractor.recursive.blacklist
-----------------------------
=========== =====
Type        ``list`` of ``strings``
Default     ``["directlink", "oauth", "recursive", "test"]``
Description A list of extractor categories which should be ignored when using
            the ``recursive`` extractor.
=========== =====


extractor.reddit.comments
-------------------------
=========== =====
Type        ``integer`` or ``string``
Default     ``500``
Description The value of the ``limit`` parameter when loading
            a submission and its comments.
            This number (roughly) specifies the total amount of comments
            being retrieved with the first API call.

            Reddit's internal default and maximum values for this parameter
            appear to be 200 and 500 respectively.

            The value `0` ignores all comments and significantly reduces the
            time required when scanning a subreddit.
=========== =====


extractor.reddit.morecomments
-----------------------------
=========== =====
Type        ``bool``
Default     ``false``
Description Retrieve additional comments by resolving the ``more`` comment
            stubs in the base comment tree.

            This requires 1 additional API call for every 100 extra comments.
=========== =====


extractor.reddit.date-min & .date-max
-------------------------------------
=========== =====
Type        ``integer`` or ``string``
Default     ``0`` and ``253402210800`` (timestamp of |datetime.max|_)
Description Ignore all submissions posted before/after this date.

            * If this is an ``integer``, it represents the date as UTC timestamp.
            * If this is a ``string``, it will get parsed according to date-format_.
=========== =====


extractor.reddit.date-format
----------------------------
=========== =====
Type        ``string``
Default     ``"%Y-%m-%dT%H:%M:%S"``
Description An explicit format string used to parse the ``string`` values of
            `date-min and date-max`_.

            See |strptime|_ for a list of formatting directives.
=========== =====


extractor.reddit.id-min & .id-max
---------------------------------
=========== =====
Type        ``string``
Example     ``"6kmzv2"``
Description Ignore all submissions posted before/after the submission with
            this ID.
=========== =====


extractor.reddit.recursion
--------------------------
=========== =====
Type        ``integer``
Default     ``0``
Description Reddit extractors can recursively visit other submissions
            linked to in the initial set of submissions.
            This value sets the maximum recursion depth.

            Special values:

            * ``0``: Recursion is disabled
            * ``-1``: Infinite recursion (don't do this)
=========== =====


extractor.reddit.refresh-token
------------------------------
=========== =====
Type        ``string``
Default     ``null``
Description The ``refresh_token`` value you get from linking your
            Reddit account to *gallery-dl*.

            Using a ``refresh_token`` allows you to access private or otherwise
            not publicly available subreddits, given that your account is
            authorized to do so,
            but requests to the reddit API are going to be rate limited
            at 600 requests every 10 minutes/600 seconds.
=========== =====


extractor.sankaku.wait-min & .wait-max
--------------------------------------
=========== =====
Type        ``float``
Default     ``2.5`` and ``5.0``
Description Minimum and maximum wait time in seconds between each image

            Sankaku Channel responds with ``429 Too Many Requests`` if it
            receives too many HTTP requests in a certain amount of time.
            Waiting a few seconds between each request tries to prevent that.
=========== =====


extractor.tumblr.external
-------------------------
=========== =====
Type        ``bool``
Default     ``false``
Description Follow external URLs (e.g. from "Link" posts) and try to extract
            images from them.
=========== =====


extractor.tumblr.inline
-----------------------
=========== =====
Type        ``bool``
Default     ``false``
Description Search posts for inline images.
=========== =====


extractor.tumblr.reblogs
------------------------
=========== =====
Type        ``bool``
Default     ``true``
Description Extract images from reblogged posts.
=========== =====


extractor.tumblr.posts
----------------------
=========== =====
Type        ``string`` or ``list`` of ``strings``
Default     ``"photo"``
Example     ``"video,audio,link"`` or ``["video", "audio", "link"]``
Description A (comma-separated) list of post types to extract images, etc. from.

            Possible types are ``text``, ``quote``, ``link``, ``answer``,
            ``video``, ``audio``, ``photo``, ``chat``.

            You can use ``"all"`` instead of listing all types separately.
=========== =====



Downloader Options
==================

downloader.part
---------------
=========== =====
Type        ``bool``
Default     ``true``
Description Controls the use of ``.part`` files during file downloads.

            * ``true``: Write downloaded data into ``.part`` files and rename
              them upon download completion. This mode additionally supports
              resuming incomplete downloads.
            * ``false``: Do not use ``.part`` files and write data directly
              into the actual output files.
=========== =====


downloader.part-directory
-------------------------
=========== =====
Type        |Path|_
Default     ``null``
Description Alternate location for ``.part`` files.

            Missing directories will be created as needed.
            If this value is ``null``, ``.part`` files are going to be stored
            alongside the actual output files.
=========== =====


downloader.http.rate
--------------------
=========== =====
Type        ``string``
Default     ``null``
Examples    ``"32000"``, ``"500k"``, ``"2.5M"``
Description Maximum download rate in bytes per second.

            Possible values are valid integer or floating-point numbers
            optionally followed by one of ``k``, ``m``. ``g``, ``t`` or ``p``.
            These suffixes are case-insensitive.
=========== =====


downloader.http.retries
-----------------------
=========== =====
Type        ``integer``
Default     ``5``
Description Number of times a failed download is retried before giving up.
=========== =====


downloader.http.timeout
-----------------------
=========== =====
Type        ``float`` or ``null``
Default     ``30``
Description Amount of time (in seconds) to wait for a successful connection
            and response from a remote server.

            This value gets internally used as the |timeout|_ parameter for the
            |requests.request()|_ method during downloads.
=========== =====


downloader.http.verify
----------------------
=========== =====
Type        ``bool`` or ``string``
Default     ``true``
Description Controls whether to verify SSL/TLS certificates for HTTPS requests.

            If this is a ``string``, it must be the path to a CA bundle to use
            instead of the default certificates.

            This value gets internally used as the |verify|_ parameter for the
            |requests.request()|_ method during downloads.
=========== =====



Output Options
==============

output.mode
-----------
=========== =====
Type        ``string``
Default     ``"auto"``
Description Controls the output string format and status indicators.

            * ``"null"``: No output
            * ``"pipe"``: Suitable for piping to other processes or files
            * ``"terminal"``: Suitable for the standard Windows console
            * ``"color"``: Suitable for terminals that understand ANSI escape codes and colors
            * ``"auto"``: Automatically choose the best suitable output mode
=========== =====


output.shorten
--------------
=========== =====
Type        ``bool``
Default     ``true``
Description Controls whether the output strings should be shortened to fit
            on one console line.
=========== =====


output.progress
---------------
=========== =====
Type        ``bool`` or ``string``
Default     ``true``
Description Controls the progress indicator when *gallery-dl* is run with
            multiple URLs as arguments.

            * ``true``: Show the default progress indicator
              (``"[{current}/{total}] {url}"``)
            * ``false``: Do not show any progress indicator
            * Any ``string``: Show the progress indicator using this
              as a custom `format string`_. Possible replacement keys are
              ``current``, ``total``  and ``url``.
=========== =====


output.log
----------
=========== =====
Type        ``string`` or |Logging Configuration|_
Default     ``"[{name}][{levelname}] {message}"``
Description Configuration for standard logging output to stderr.

            If this is a simple ``string``, it specifies
            the format string for logging messages.
=========== =====


output.logfile
--------------
=========== =====
Type        |Path|_ or |Logging Configuration|_
Default     ``null``
Description File to write logging output to.
=========== =====


output.unsupportedfile
----------------------
=========== =====
Type        |Path|_ or |Logging Configuration|_
Default     ``null``
Description File to write external URLs unsupported by *gallery-dl* to.

            The default format string here is ``"{message}"``.
=========== =====



Postprocessor Options
=====================


classify
--------

Categorize files by filename extension

classify.mapping
----------------
=========== =====
Type        ``object``
Default     .. code::

                {
                    "Pictures" : ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp"],
                    "Video"    : ["flv", "ogv", "avi", "mp4", "mpg", "mpeg", "3gp", "mkv", "webm", "vob", "wmv"],
                    "Music"    : ["mp3", "aac", "flac", "ogg", "wma", "m4a", "wav"],
                    "Archives" : ["zip", "rar", "7z", "tar", "gz", "bz2"]
                }

Description A mapping from directory names to filename extensions that should
            be stored in them.

            Files with an extension not listed will be ignored and stored
            in their default location.
=========== =====


exec
----

Execute external commands.

exec.async
----------
=========== =====
Type        ``bool``
Default     ``false``
Description Controls whether to wait for a subprocess to finish
            or to let it run asynchronously.
=========== =====

exec.command
------------
=========== =====
Type        ``list`` of ``strings``
Example     ``["echo", "{user[account]}", "{id}"]``
Description The command to run.

            Each element of this list is treated as a `format string`_ using
            the files' metadata.
=========== =====


ugoira
------

Convert Pixiv Ugoira to WebM using `FFmpeg <https://www.ffmpeg.org/>`__.

ugoira.extension
----------------
=========== =====
Type        ``string``
Default     ``"webm"``
Description Filename extension for the resulting video files.
=========== =====

ugoira.ffmpeg-args
------------------
=========== =====
Type        ``list`` of ``strings``
Default     ``null``
Example     ``["-c:v", "libvpx-vp9", "-an", "-b:v", "2M"]``
Description Additional FFmpeg command-line arguments.
=========== =====

ugoira.ffmpeg-location
----------------------
=========== =====
Type        |Path|_
Default     ``"ffmpeg"``
Description Location of the ``ffmpeg`` (or ``avconv``) executable to use.
=========== =====

ugoira.ffmpeg-twopass
---------------------
=========== =====
Type        ``bool``
Default     ``False``
Description Enable Two-Pass encoding.
=========== =====

ugoira.keep-files
-----------------
=========== =====
Type        ``bool``
Default     ``false``
Description Keep ZIP archives after conversion.
=========== =====


zip
---

Store files in a ZIP archive.

zip.compression
---------------
=========== =====
Type        ``string``
Default     ``"store"``
Description Compression method to use when writing the archive.

            Possible values are ``"store"``, ``"zip"``, ``"bzip2"``, ``"lzma"``.
=========== =====

zip.extension
-------------
=========== =====
Type        ``string``
Default     ``"zip"``
Description Filename extension for the created ZIP archive.
=========== =====

zip.keep-files
--------------
=========== =====
Type        ``bool``
Default     ``false``
Description Keep the actual files after writing them to a ZIP archive.
=========== =====



Miscellaneous Options
=====================

netrc
-----
=========== =====
Type        ``bool``
Default     ``false``
Description Enable the use of |.netrc|_ authentication data.
=========== =====


cache.file
----------
=========== =====
Type        |Path|_
Default     |tempfile.gettempdir()|_ + ``".gallery-dl.cache"``
Description Path of the SQLite3 database used to cache login sessions,
            cookies and API tokens across `gallery-dl` invocations.

            Set this option to ``null`` or an invalid path to disable
            this cache.
=========== =====



API Tokens & IDs
================

All configuration keys listed in this section have fully functional default
values embedded into *gallery-dl* itself, but if things unexpectedly break
or you want to use your own personal client credentials, you can follow these
instructions to get an alternative set of API tokens and IDs.


extractor.deviantart.client-id & .client-secret
-----------------------------------------------
=========== =====
Type        ``string``
How To      - login and visit DeviantArt's
              `Applications & Keys <https://www.deviantart.com/developers/apps>`__
              section
            - click "Register your Application"
            - scroll to "OAuth2 Redirect URI Whitelist (Required)"
              and enter "https://mikf.github.io/gallery-dl/oauth-redirect.html"
            - click "Save" (top right)
            - copy ``client_id`` and ``client_secret`` of your new
              application and put them in your configuration file
=========== =====


extractor.flickr.api-key & .api-secret
--------------------------------------
=========== =====
Type        ``string``
How To      - login and `Create an App <https://www.flickr.com/services/apps/create/apply/>`__
              in Flickr's `App Garden <https://www.flickr.com/services/>`__
            - click "APPLY FOR A NON-COMMERCIAL KEY"
            - fill out the form with a random name and description
              and click "SUBMIT"
            - copy ``Key`` and ``Secret`` and put them in your configuration
              file
=========== =====


extractor.pawoo.access-token
----------------------------
=========== =====
Type        ``string``
How To
=========== =====


extractor.reddit.client-id & .user-agent
----------------------------------------
=========== =====
Type        ``string``
How To      - login and visit the `apps <https://www.reddit.com/prefs/apps/>`__
              section of your account's preferences
            - click the "are you a developer? create an app..." button
            - fill out the form, choose "installed app", preferably set
              "http://localhost:6414/" as "redirect uri" and finally click
              "create app"
            - copy the client id (third line, under your application's name and
              "installed app") and put it in your configuration file
            - use "``Python:<application name>:v1.0 (by /u/<username>)``" as
              user-agent and replace ``<application name>`` and ``<username>``
              accordingly (see Reddit's
              `API access rules <https://github.com/reddit/reddit/wiki/API>`__)
=========== =====


extractor.smugmug.api-key & .api-secret
---------------------------------------
=========== =====
Type        ``string``
How To      - login and `Apply for an API Key <https://api.smugmug.com/api/developer/apply>`__
            - use a random name and description,
              set "Type" to "Application", "Platform" to "All",
              and "Use" to "Non-Commercial"
            - fill out the two checkboxes at the bottom and click "Apply"
            - copy ``API Key`` and ``API Secret``
              and put them in your configuration file
=========== =====


extractor.tumblr.api-key & .api-secret
--------------------------------------
=========== =====
Type        ``string``
How To      - login and visit Tumblr's
              `Applications <https://www.tumblr.com/oauth/apps>`__ section
            - click "Register application"
            - fill out the form: use a random name and description, set
              https://example.org/ as "Application Website" and "Default
              callback URL"
            - solve Google's "I'm not a robot" challenge and click "Register"
            - click "Show secret key" (below "OAuth Consumer Key")
            - copy your ``OAuth Consumer Key`` and ``Secret Key``
              and put them in your configuration file
=========== =====



Custom Types
============


Path
----
=========== =====
Type        ``string`` or ``list`` of ``strings``
Examples    * ``"file.ext"``
            * ``"~/path/to/file.ext"``
            * ``"$HOME/path/to/file.ext"``
            * ``["$HOME", "path", "to", "file.ext"]``
Description A |Path|_ is a ``string`` representing the location of a file
            or directory.

            Simple `tilde expansion <https://docs.python.org/3/library/os.path.html#os.path.expanduser>`__
            and `environment variable expansion <https://docs.python.org/3/library/os.path.html#os.path.expandvars>`__
            is supported.

            In Windows environments, backslashes (``"\"``) can, in addition to
            forward slashes (``"/"``), be used as path separators.
            Because backslashes are JSON's escape character,
            they themselves have to be escaped.
            The path ``C:\path\to\file.ext`` has therefore to be written as
            ``"C:\\path\\to\\file.ext"`` if you want to use backslashes.
=========== =====


Logging Configuration
---------------------
=========== =====
Type        ``object``

Example     .. code::

                {
                    "format": "{asctime} {name}: {message}",
                    "format-date": "%H:%M:%S",
                    "path": "~/log.txt",
                    "encoding": "ascii"
                }

Description Extended logging output configuration.

            * format
                * Format string for logging messages
                  (see `LogRecord attributes <https://docs.python.org/3/library/logging.html#logrecord-attributes>`__)
                * Default: ``"[{name}][{levelname}] {message}"``
            * format-date
                * Format string for ``{asctime}`` fields in logging messages
                  (see `strftime() directives <https://docs.python.org/3/library/time.html#time.strftime>`__)
                * Default: ``"%Y-%m-%d %H:%M:%S"``
            * level
                * Minimum logging message level
                  (one of ``"debug"``, ``"info"``, ``"warning"``, ``"error"``, ``"exception"``)
                * Default: ``"info"``
            * path
                * |Path|_ to the output file
            * mode
                * Mode in which the file is opened;
                  use ``"w"`` to truncate or ``"a"`` to append
                  (see `open() <https://docs.python.org/3/library/functions.html#open>`__)
                * Default: ``"w"``
            * encoding
                * File encoding
                * Default: ``"utf-8"``

            Note: path, mode and encoding are only applied when configuring
            logging output to a file.
=========== =====


Postprocessor Configuration
---------------------------
=========== =====
Type        ``object``

Example     .. code::

                {
                    "name": "zip",
                    "compression": "store",
                    "extension": "cbz"
                }

Description An object with the ``name`` of the post-processor to use
            and its options.
            See `Postprocessor Options`_ for a list of available
            post-processors and their respective options.
=========== =====



.. |.netrc| replace:: ``.netrc``
.. |tempfile.gettempdir()| replace:: ``tempfile.gettempdir()``
.. |requests.request()| replace:: ``requests.request()``
.. |timeout| replace:: ``timeout``
.. |verify| replace:: ``verify``
.. |mature_content| replace:: ``mature_content``
.. |webbrowser.open()| replace:: ``webbrowser.open()``
.. |datetime.max| replace:: ``datetime.max``
.. |Path| replace:: ``Path``
.. |Logging Configuration| replace:: ``Logging Configuration``
.. |Postprocessor Configuration| replace:: ``Postprocessor Configuration``
.. |strptime| replace:: strftime() and strptime() Behavior

.. _base-directory: `extractor.*.base-directory`_
.. _skipped: `extractor.*.skip`_
.. _`date-min and date-max`: `extractor.reddit.date-min & .date-max`_
.. _date-format: extractor.reddit.date-format_

.. _.netrc:            https://stackoverflow.com/tags/.netrc/info
.. _tempfile.gettempdir(): https://docs.python.org/3/library/tempfile.html#tempfile.gettempdir
.. _requests.request(): https://docs.python-requests.org/en/master/api/#requests.request
.. _timeout:           https://docs.python-requests.org/en/latest/user/advanced/#timeouts
.. _verify:            https://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification
.. _`Requests' proxy documentation`: http://docs.python-requests.org/en/master/user/advanced/#proxies
.. _format string:     https://docs.python.org/3/library/string.html#formatstrings
.. _format strings:    https://docs.python.org/3/library/string.html#formatstrings
.. _strptime:          https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
.. _mature_content:    https://www.deviantart.com/developers/http/v1/20160316/object/deviation
.. _webbrowser.open(): https://docs.python.org/3/library/webbrowser.html
.. _datetime.max:      https://docs.python.org/3/library/datetime.html#datetime.datetime.max
.. _Authentication:    https://github.com/mikf/gallery-dl#5authentication
