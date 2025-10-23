Configuration
#############

| Configuration files for *gallery-dl* use a JSON-based file format.
| For a (more or less) complete example with options set to their default values,
  see `gallery-dl.conf <gallery-dl.conf>`__.
| For a configuration file example with more involved settings and options,
  see `gallery-dl-example.conf <gallery-dl-example.conf>`__.
|

This file lists all available configuration options and their descriptions.


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

``category`` is the lowercase site name without any spaces or special
characters, which is usually just the module name
(``pixiv``, ``danbooru``, ...).

``subcategory`` is a lowercase word describing the general functionality
of that extractor (``user``, ``favorite``, ``manga``, ...).

The ``category`` and ``subcategory`` of all extractors are included in the
output of ``gallery-dl --list-extractors``.
For a specific URL, these values
can also be determined by using the
``-E`` / ``--extractor-info`` and ``-K`` / ``--list-keywords``
command-line optiona (see the example below).

Each one of the following options can be specified on multiple levels of the
configuration tree:

================== =======
Base level:        ``extractor.<option-name>``
Category level:    ``extractor.<category>.<option-name>``
Subcategory level: ``extractor.<category>.<subcategory>.<option-name>``
================== =======

JSON Representation:

.. code:: json

    {
        "extractor": {
            "<option-name>": "<value-base>",

            "<category>": {
                "<option-name>": "<value-category>",

                "<subcategory>": {
                    "<option-name>": "<value-subcategory>"
                }
            }
        }
    }

A value in a "deeper" level hereby
overrides a value of the same name on a lower level.
For example, setting a value for ``extractor.pixiv.filename``
lets you specify a general filename pattern
for all the different ``pixiv`` extractors.
Setting the ``extractor.pixiv.user.filename`` value lets you override this
general pattern specifically for ``PixivUserExtractor`` instances.

Specifying an option on the top level, next to ``extractor``,
acts as a *global* setting,
overriding *all* other values with the same option name,
regardless of their position.

.. code:: json

    {
        "extractor": {
            "<option-name>": "<value-base (overridden)>"
        },
        "<option-name>": "<value-global>"
    }



extractor.*.filename
--------------------
Type
    * `Format String`_
    * ``object`` (Condition_ → `Format String`_)
Example
    .. code:: json

        "{manga}_c{chapter}_{page:>03}.{extension}"

    .. code:: json

        {
            "extension == 'mp4'": "{id}_video.{extension}",
            "'nature' in title" : "{id}_{title}.{extension}",
            ""                  : "{id}_default.{extension}"
        }

Description
    A `Format String`_ to generate filenames for downloaded files.

    If this is an ``object``,
    it must contain Conditions_ mapping to the
    `Format String`_ to use.
    These Conditions_ are evaluated in the specified order
    until one evaluates to ``True``.
    When none match, the ``""`` entry or
    the extractor's default filename `Format String`_ is used.

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
Note
    Even if the value of the ``extension`` key is missing or
    ``None``, it will be filled in later when the file download is
    starting. This key is therefore always available to provide
    a valid filename extension.


extractor.*.directory
---------------------
Type
    * ``list`` of `Format Strings`_
    * ``object`` (Condition_ → `Format Strings`_)
Example
    .. code:: json

        ["{category}", "{manga}", "c{chapter} - {title}"]

    .. code:: json

        {
            "'nature' in content": ["Nature Pictures"],
            "retweet_id != 0"    : ["{category}", "{user[name]}", "Retweets"],
            ""                   : ["{category}", "{user[name]}"]
        }

Description
    A list of `Format String(s)`_ to generate the target directory path.

    If this is an ``object``,
    it must contain Conditions_ mapping to the
    list of `Format Strings`_ to use.

    Each individual string in such a list represents a single path
    segment, which will be joined together and appended to the
    base-directory_ to form the complete target directory path.


extractor.*.base-directory
--------------------------
Type
    * |Path|_
    * ``object`` (Condition_ → |Path|_)
Default
    ``"./gallery-dl/"``
Example
    .. code:: json

        "~/Downloads/gallery-dl"

    .. code:: json

        {
            "score >= 100": "$DL",
            "duration"    : "$DL/video",
            ""            : "/tmp/files/"
        }
Description
    Directory path used as base for all download destinations.

    If this is an ``object``,
    it must contain Conditions_ mapping to the |Path|_ to use.
    Specifying a default |Path|_ with ``""`` is required.


extractor.*.parent-directory
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Use an extractor's current target directory as
    base-directory_ for any spawned child extractors.


extractor.*.parent-metadata
---------------------------
extractor.*.metadata-parent
---------------------------
Type
    * ``bool``
    * ``string``
Default
    ``false``
Description
    If ``true``, overwrite any metadata provided by a child extractor
    with its parent's.

    | If this is a ``string``, add a parent's metadata to its children's
      to a field named after said string.
    | For example with ``"parent-metadata": "_p_"``:

    .. code:: json

        {
            "id": "child-id",
            "_p_": {"id": "parent-id"}
        }


extractor.*.parent-skip
-----------------------
Type
    ``bool``
Default
    ``false``
Description
    Share number of skipped downloads between parent and child extractors.


extractor.*.path-restrict
-------------------------
Type
    * ``string``
    * ``object`` (`character` → `replacement character(s)`)
Default
    ``"auto"``
Example
    * ``"/!? (){}"``
    * ``{"/": "_", "+": "_+_", "({[": "(", "]})": ")", "a-z": "*"}``
Description
    | A ``string`` of characters to be replaced with the value of
      `path-replace <extractor.*.path-replace_>`__
    | or an ``object`` mapping invalid/unwanted characters, character sets,
      or character ranges to their replacements
    | for generated path segment names.
Special Values
    ``"auto"``
        Use characters from ``"unix"`` or ``"windows"``
        depending on the local operating system
    ``"unix"``
        ``"/"``
    ``"windows"``
        | ``"\\\\|/<>:\"?*"``
        | (https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file)
    ``"ascii"``
        | ``"^0-9A-Za-z_."``
        | (only ASCII digits, letters, underscores, and dots)
    ``"ascii+"``
        | ``"^0-9@-[\\]-{ #-)+-.;=!}~"``
        | (all ASCII characters except the ones not allowed by Windows)
Implementation Detail
    For ``strings`` with length >= 2, this option uses a
    `Regular Expression Character Set <https://www.regular-expressions.info/charclass.html>`__,
    meaning that:

    * Using a caret ``^`` as first character inverts the set
      (``"^..."``)
    * Character ranges are supported
      (``"0-9a-z"``)
    * ``]``, ``-``, and ``\`` need to be escaped as
      ``\\]``, ``\\-``, and ``\\\\`` respectively
      to use them as literal characters


extractor.*.path-replace
------------------------
Type
    ``string``
Default
    ``"_"``
Description
    The replacement character(s) for
    `path-restrict <extractor.*.path-restrict_>`__


extractor.*.path-remove
-----------------------
Type
    ``string``
Default
    ``"\u0000-\u001f\u007f"`` (ASCII control characters)
Description
    Set of characters to remove from generated path names.
Note
    In a string with 2 or more characters, ``[]^-\`` need to be
    escaped with backslashes, e.g. ``"\\[\\]"``


extractor.*.path-strip
----------------------
Type
    ``string``
Default
    ``"auto"``
Description
    Set of characters to remove from the end of generated path segment names
    using `str.rstrip() <https://docs.python.org/3/library/stdtypes.html#str.rstrip>`_
Special Values
    ``"auto"``
        Use characters from ``"unix"`` or ``"windows"``
        depending on the local operating system
    ``"unix"``
        ``""``
    ``"windows"``
        ``". "``


extractor.*.path-convert
------------------------
Type
    `Conversion(s)`_
Example
    * ``"g"``
    * ``"Wl"``
Description
    `Conversion(s)`_ to apply to each path segment after
    `path-restrict <extractor.*.path-restrict_>`__
    replacements.


extractor.*.path-extended
-------------------------
Type
    ``bool``
Default
    ``true``
Description
    On Windows, use `extended-length paths <https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation>`__
    prefixed with ``\\?\`` to work around the 260 characters path length limit.


extractor.*.extension-map
-------------------------
Type
    ``object`` (`extension` → `replacement`)
Default
    .. code:: json

        {
            "jpeg": "jpg",
            "jpe" : "jpg",
            "jfif": "jpg",
            "jif" : "jpg",
            "jfi" : "jpg"
        }
Description
    A JSON ``object`` mapping filename extensions to their replacements.


extractor.*.skip
----------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Example
    * ``"abort:5"``
    * ``"abort:5:2"``
    * ``"abort:5:manga"``
    * ``"terminate:3"``
Description
    Controls the behavior when downloading files that have been
    downloaded before, i.e. a file with the same filename already
    exists or its ID is in a `download archive <extractor.*.archive_>`__.

    ``true``
        Skip downloads
    ``false``
        Overwrite already existing files

    ``"abort"``
        Stop the current extractor
    ``"abort:N"``
        Skip downloads and
        stop the current extractor after ``N`` consecutive skips
    ``"abort:N:L"``
        | Skip downloads and
          stop the current extractor after ``N`` consecutive skips
        | Ascend ``L`` levels in the extractor hierarchy
    ``"abort:N:SC"``
        | Skip downloads and
          stop the current extractor after ``N`` consecutive skips
        | Ascend to an extractor with subcategory ``SC`` in the extractor hierarchy

    ``"terminate"``
        Stop the current extractor, including parent extractors
    ``"terminate:N"``
        Skip downloads and
        stop the current extractor, including parent extractors,
        after ``N`` consecutive skips

    ``"exit"``
        Exit the program altogether
    ``"exit:N"``
        Skip downloads and
        exit the program after ``N`` consecutive skips

    ``"enumerate"``
        Add an enumeration index to the beginning of the
        filename extension (``file.1.ext``, ``file.2.ext``, etc.)


extractor.*.skip-filter
-----------------------
Type
    Condition_
Description
    Python Expression_ controlling which skipped files to count towards
    ``"abort"`` / ``"terminate"`` / ``"exit"``.


extractor.*.sleep
-----------------
Type
    |Duration|_
Default
    ``0``
Description
    Number of seconds to sleep before each download.


extractor.*.sleep-extractor
---------------------------
Type
    |Duration|_
Default
    ``0``
Description
    Number of seconds to sleep before handling an input URL,
    i.e. before starting a new extractor.


extractor.*.sleep-429
---------------------
Type
    |Duration|_
Default
    ``60``
Description
    Number of seconds to sleep when receiving a `429 Too Many Requests`
    response before `retrying <extractor.*.retries_>`__ the request.


extractor.*.sleep-request
-------------------------
Type
    |Duration|_
Default
    ``"0.5-1.5"``
        ``ao3``             |
        ``arcalive``        |
        ``booth``           |
        ``civitai``         |
        ``[Danbooru]``      |
        ``[E621]``          |
        ``[foolfuuka]:search`` |
        ``hdoujin``         |
        ``itaku``           |
        ``newgrounds``      |
        ``[philomena]``     |
        ``pixiv-novel``     |
        ``plurk``           |
        ``poipiku``         |
        ``pornpics``        |
        ``schalenetwork``   |
        ``scrolller``       |
        ``sizebooru``       |
        ``soundgasm``       |
        ``thehentaiworld``  |
        ``urlgalleries``    |
        ``vk``              |
        ``webtoons``        |
        ``weebcentral``     |
        ``xfolio``          |
        ``zerochan``
    ``"1.0"``
        ``furaffinity``     |
        ``rule34``
    ``"1.0-2.0"``
        ``flickr``          |
        ``pexels``          |
        ``weibo``           |
        ``[wikimedia]``
    ``"1.4"``
        ``wallhaven``
    ``"2.0-4.0"``
        ``behance``         |
        ``imagefap``        |
        ``[Nijie]``
    ``"3.0-6.0"``
        ``bilibili``        |
        ``exhentai``        |
        ``[reactor]``       |
        ``readcomiconline``
    ``"6.0-6.1"``
        ``twibooru``
    ``"6.0-12.0"``
        ``instagram``
    ``0``
        otherwise
Description
    Minimal time interval in seconds between each HTTP request
    during data extraction.


extractor.*.username & .password
--------------------------------
Type
    ``string``
Default
    ``null``
Description
    The username and password to use when attempting to log in to
    another site.

    This is supported for

    * ``aibooru`` (`* <pw-apikey_>`__)
    * ``ao3``
    * ``aryion``
    * ``atfbooru`` (`* <pw-apikey_>`__)
    * ``bluesky``
    * ``booruvar`` (`* <pw-apikey_>`__)
    * ``coomer``
    * ``danbooru`` (`* <pw-apikey_>`__)
    * ``deviantart``
    * ``e621`` (`* <pw-apikey_>`__)
    * ``e6ai`` (`* <pw-apikey_>`__)
    * ``e926`` (`* <pw-apikey_>`__)
    * ``exhentai``
    * ``girlswithmuscle``
    * ``horne`` (`R <pw-required_>`__)
    * ``idolcomplex``
    * ``imgbb``
    * ``inkbunny``
    * ``iwara``
    * ``kemono``
    * ``madokami`` (`R <pw-required_>`__)
    * ``mangadex``
    * ``mangoxo``
    * ``newgrounds``
    * ``nijie`` (`R <pw-required_>`__)
    * ``pillowfort``
    * ``rule34xyz``
    * ``sankaku``
    * ``scrolller``
    * ``seiga``
    * ``simpcity``
    * ``subscribestar``
    * ``tapas``
    * ``tsumino``
    * ``vipergirls``
    * ``zerochan``

    These values can also be specified via the
    ``-u/--username`` and ``-p/--password`` command-line options or
    by using a |.netrc|_ file. (see Authentication_)

Note
    Leave the ``password`` value empty or undefined
    to be prompted for a password when performing a login
    (see `getpass() <https://docs.python.org/3/library/getpass.html#getpass.getpass>`__).

    .. _pw-apikey:

    (*) The ``password`` value for these sites should be
    the API key found in your user profile, not the actual account password.

    .. _pw-required:

    (R) Login with username & password or
    supplying authenticated
    `cookies <extractor.*.cookies_>`__
    is *required*


extractor.*.input
-----------------
Type
    ``bool``
Default
    ``true`` if `stdin` is attached to a terminal,
    ``false`` otherwise
Description
    Allow prompting the user for interactive input.


extractor.*.netrc
-----------------
Type
    ``bool``
Default
    ``false``
Description
    Enable the use of |.netrc|_ authentication data.


extractor.*.cookies
-------------------
Type
    * |Path|_
    * ``object`` (`name` → `value`)
    * ``list``
Description
    Source to read additional cookies from. This can be

    * The |Path|_ to a Mozilla/Netscape format cookies.txt file

      .. code:: json

        "~/.local/share/cookies-instagram-com.txt"

    * An ``object`` specifying cookies as name-value pairs

      .. code:: json

        {
            "cookie-name": "cookie-value",
            "sessionid"  : "14313336321%3AsabDFvuASDnlpb%3A31",
            "isAdult"    : "1"
        }

    * A ``list`` with up to 5 entries specifying a browser profile.

      * The first entry is the browser name
      * The optional second entry is a profile name or an absolute path to a profile directory
      * The optional third entry is the keyring to retrieve passwords for decrypting cookies from
      * The optional fourth entry is a (Firefox) container name (``"none"`` for only cookies with no container (default))
      * The optional fifth entry is the domain to extract cookies for. Prefix it with a dot ``.`` to include cookies for subdomains.

      .. code:: json

        ["firefox"]
        ["firefox", null, null, "Personal"]
        ["chromium", "Private", "kwallet", null, ".twitter.com"]


extractor.*.cookies-select
--------------------------
Type
    ``string``
Default
    ``null``
Description
    Interpret `extractor.cookies <extractor.*.cookies_>`__
    as a list of cookie sources and select one of them for each extractor run.

    .. code:: json

      [
          "~/.local/share/cookies-instagram-com-1.txt",
          "~/.local/share/cookies-instagram-com-2.txt",
          "~/.local/share/cookies-instagram-com-3.txt",
          ["firefox", null, null, "c1", ".instagram-com"],
      ]

Supported Values
    ``"random"``
        Select cookies `randomly <https://docs.python.org/3.10/library/random.html#random.choice>`__.
    ``"rotate"``
        Select cookies in sequence. Start over from the beginning after reaching the end of the list.


extractor.*.cookies-update
--------------------------
Type
    * ``bool``
    * |Path|_
Default
    ``true``
Description
    Export session cookies in cookies.txt format.

    * If this is a |Path|_, write cookies to the given file path.

    * If this is ``true`` and `extractor.*.cookies`_ specifies the |Path|_
      of a valid cookies.txt file, update its contents.


extractor.*.proxy
-----------------
Type
    * ``string``
    * ``object`` (`scheme` → `proxy`)
Example
    .. code:: json

      "http://10.10.1.10:3128"

    .. code:: json

      {
          "http" : "http://10.10.1.10:3128",
          "https": "http://10.10.1.10:1080",
          "http://10.20.1.128": "http://10.10.1.10:5323"
      }

Description
    Proxy (or proxies) to be used for remote connections.

    * If this is a ``string``, it is the proxy URL for all
      outgoing requests.
    * If this is an ``object``, it is a scheme-to-proxy mapping to
      specify different proxy URLs for each scheme.
      It is also possible to set a proxy for a specific host by using
      ``scheme://host`` as key.
      See `Requests' proxy documentation`_ for more details.
Note
    If a proxy URL does not include a scheme, ``http://`` is assumed.


extractor.*.proxy-env
---------------------
Type
    ``bool``
Default
    ``true``
Description
    Collect proxy configuration information from environment variables
    (``HTTP_PROXY``, ``HTTPS_PROXY``, ``NO_PROXY``)
    and Windows Registry settings.


extractor.*.source-address
--------------------------
Type
    * ``string``
    * ``list`` with 1 ``string`` and 1 ``integer`` as elements
Example
    * ``"192.168.178.20"``
    * ``["192.168.178.20", 8080]``
Description
    Client-side IP address to bind to.

    | Can be either a simple ``string`` with just the local IP address
    | or a ``list`` with IP and explicit port number as elements.


extractor.*.user-agent
----------------------
Type
    ``string``
Default
    ``"gallery-dl/VERSION"``
        * ``[Danbooru]``
        * ``mangadex``
        * ``weasyl``
        * ``zerochan``
    ``"gallery-dl/VERSION (by mikf)"``
        * ``[E621]``
    ``"net.umanle.arca.android.playstore/0.9.75"``
        * ``arcalive``
    ``"Patreon/72.2.28 (Android; Android 14; Scale/2.10)"``
        * ``patreon``
    ``"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/LATEST.0.0.0 Safari/537.36"``
        * ``instagram``
    ``"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:LATEST) Gecko/20100101 Firefox/LATEST"``
        * otherwise
Example
    * ``"curl/8.14.1"``
    * ``"browser"``
    * ``"@chrome"``
Description
    User-Agent header value used for HTTP requests.

    Setting this value to ``"browser"`` will try to automatically detect
    and use the ``User-Agent`` header of the system's default browser.

    Setting this value to ``"@BROWSER"``, e.g. ``"@chrome"``, will try to automatically detect
    and use the ``User-Agent`` header of this installed browser.


extractor.*.browser
-------------------
Type
    ``string``
Default
    ``"firefox"``
        ``artstation`` |
        ``behance``    |
        ``fanbox``     |
        ``twitter``
    ``null``
        otherwise
Example
    * ``"firefox"``
    * ``"firefox/128"``
    * ``"chrome:macos"``
    * ``"chrome/138:macos"``
Description
    | Try to emulate a real browser (``firefox`` or ``chrome``)
    | by using its HTTP headers and TLS ciphers for HTTP requests
      by setting specialized defaults for

    * `user-agent <extractor.*.user-agent_>`__
    * `headers <extractor.*.headers_>`__
    * `ciphers <extractor.*.ciphers_>`__

    Supported browsers:

    * ``firefox``
    * ``firefox/140``
    * ``firefox/128``
    * ``chrome``
    * ``chrome/138``
    * ``chrome/111``

    The operating system used in the ``User-Agent`` header can be
    specified after a colon ``:`` (``windows``, ``linux``, ``macos``),
    for example ``chrome:windows``.
Note
    Any value *not* matching a supported browser
    will fall back to ``"firefox"``.

    ``requests`` and ``urllib3`` only support HTTP/1.1, while a real
    browser would use HTTP/2 and HTTP/3.


extractor.*.referer
-------------------
Type
    * ``bool``
    * ``string``
Default
    ``false``
        ``4archive``      |
        ``4chanarchives`` |
        ``archivedmoe``   |
        ``nsfwalbum``     |
        ``tumblrgallery``
    ``true``
        otherwise
Description
    Send `Referer <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referer>`__
    headers with all outgoing HTTP requests.

    If this is a ``string``, send it as Referer
    instead of the extractor's ``root`` domain.


extractor.*.headers
-------------------
Type
    * ``"string"``
    * ``object`` (`name` → `value`)
Default
    .. code:: json

      {
          "User-Agent"     : "<extractor.*.user-agent>",
          "Accept"         : "*/*",
          "Accept-Language": "en-US,en;q=0.5",
          "Accept-Encoding": "gzip, deflate",
          "Referer"        : "<extractor.*.referer>"
      }

Description
    Additional `HTTP headers <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers>`__
    to be sent with each HTTP request,

    To disable sending a header, set its value to ``null``.

    Set this option to ``"firefox"`` or ``"chrome"``
    to use these browser's default headers.


extractor.*.ciphers
-------------------
Type
    * ``string``
    * ``list`` of ``strings``
Example
    * ``"firefox"``
    * .. code:: json

        ["ECDHE-ECDSA-AES128-GCM-SHA256",
         "ECDHE-RSA-AES128-GCM-SHA256",
         "ECDHE-ECDSA-CHACHA20-POLY1305",
         "ECDHE-RSA-CHACHA20-POLY1305"]

Description
    List of TLS/SSL cipher suites in
    `OpenSSL cipher list format <https://docs.openssl.org/master/man1/openssl-ciphers/#cipher-list-format>`__
    to be passed to
    `ssl.SSLContext.set_ciphers() <https://docs.python.org/3/library/ssl.html#ssl.SSLContext.set_ciphers>`__

    Set this option to ``"firefox"`` or ``"chrome"``
    to use these browser's default ciphers.


extractor.*.tls12
-----------------
Type
    ``bool``
Default
    ``false``
        ``artstation`` |
        ``behance``    |
        ``vsco``
    ``true``
        otherwise
Description
    Allow selecting TLS 1.2 cipher suites.

    Can be disabled to alter TLS fingerprints
    and potentially bypass Cloudflare blocks.


extractor.*.keywords
--------------------
Type
    ``object`` (`name` → `value`)
Example
    ``{"type": "Pixel Art", "type_id": 123}``
Description
    Additional name-value pairs to be added to each metadata dictionary.


extractor.*.keywords-eval
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Evaluate each `keywords <extractor.*.keywords_>`__ ``string`` value
    as a `Format String`_.


extractor.*.keywords-default
----------------------------
Type
    any
Default
    ``"None"``
Description
    Default value used for missing or undefined keyword names in a
    `Format String`_.


extractor.*.metadata-url
------------------------
extractor.*.url-metadata
------------------------
Type
    ``string``
Description
    Insert a file's download URL into its metadata dictionary as the given name.

    For example, setting this option to ``"gdl_file_url"`` will cause a new
    metadata field with name ``gdl_file_url`` to appear, which contains the
    current file's download URL.
    This can then be used in `filenames <extractor.*.filename_>`_,
    with a ``metadata`` post processor, etc.


extractor.*.metadata-path
-------------------------
extractor.*.path-metadata
-------------------------
Type
    ``string``
Description
    Insert a reference to the current
    `PathFormat <https://github.com/mikf/gallery-dl/blob/v1.27.0/gallery_dl/path.py#L27>`__
    data structure into metadata dictionaries as the given name.

    For example, setting this option to ``"gdl_path"`` would make it possible
    to access the current file's filename as ``"{gdl_path.filename}"``.


extractor.*.metadata-extractor
------------------------------
extractor.*.extractor-metadata
------------------------------
Type
    ``string``
Description
    Insert a reference to the current
    `Extractor <https://github.com/mikf/gallery-dl/blob/v1.27.0/gallery_dl/extractor/common.py#L28>`__
    object into metadata dictionaries as the given name.


extractor.*.metadata-http
-------------------------
extractor.*.http-metadata
-------------------------
Type
    ``string``
Description
    Insert an ``object`` containing a file's HTTP headers and
    ``filename``, ``extension``, and ``date`` parsed from them
    into metadata dictionaries as the given name.

    For example, setting this option to ``"gdl_http"`` would make it possible
    to access the current file's ``Last-Modified`` header as ``"{gdl_http[Last-Modified]}"``
    and its parsed form as ``"{gdl_http[date]}"``.


extractor.*.metadata-version
----------------------------
extractor.*.version-metadata
----------------------------
Type
    ``string``
Description
    Insert an ``object`` containing gallery-dl's version info into
    metadata dictionaries as the given name.

    The content of the object is as follows:

    .. code:: json

        {
            "version"         : "string",
            "is_executable"   : "bool",
            "current_git_head": "string or null"
        }


extractor.*.category-transfer
-----------------------------
Type
    ``bool``
Default
    Extractor-specific
Description
    Transfer an extractor's (sub)category values to all child
    extractors spawned by it, to let them inherit their parent's
    config options.


extractor.*.blacklist & .whitelist
----------------------------------
Type
    ``list`` of ``strings``
Default
    ``["oauth", "recursive", "test"]`` + current extractor category
Example
    ``["imgur", "redgifs:user", "*:image"]``
Description
    A list of extractor identifiers to ignore (or allow)
    when spawning child extractors for unknown URLs,
    e.g. from ``reddit`` or ``plurk``.

    Each identifier can be

    * A category or basecategory name (``"imgur"``, ``"mastodon"``)
    * | A (base)category-subcategory pair, where both names are separated by a colon (``"redgifs:user"``).
      | Both names can be a `*` or left empty, matching all possible names (``"*:image"``, ``":user"``).
Note
    Any ``blacklist`` setting will automatically include
    ``"oauth"``, ``"recursive"``, and ``"test"``.


extractor.*.archive
-------------------
Type
    * ``string``
    * |Path|_
Default
    ``null``
Example
    * ``"$HOME/.archives/{category}.sqlite3"``
    * ``"postgresql://user:pass@host/database"``
Description
    File to store IDs of downloaded files in. Downloads of files
    already recorded in this archive file will be
    `skipped <extractor.*.skip_>`__.

    The resulting archive file is not a plain text file but an SQLite3
    database, as either lookup operations are significantly faster or
    memory requirements are significantly lower when the
    amount of stored IDs gets reasonably large.

    If this value is a
    `PostgreSQL Connection URI <https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING-URIS>`__,
    the archive will use this PostgreSQL database as backend (requires
    `Psycopg <https://www.psycopg.org/>`__).
Note
    Archive files that do not already exist get generated automatically.

    Archive paths support basic `Format String`_ replacements,
    but be aware that using external inputs for building local paths
    may pose a security risk.


extractor.*.archive-event
-------------------------
Type
     + ``string``
     + ``list`` of ``strings``
Default
    ``"file"``
Example
    * ``"after,skip"``
    * ``["after", "skip"]``
Description
    `Event(s) <metadata.event_>`__
    for which IDs get written to an
    `archive <extractor.*.archive_>`__.
Available Events
    * ``file``
    * ``after``
    * ``skip``


extractor.*.archive-format
--------------------------
Type
    `Format String`_
Example
    ``"{id}_{offset}"``
Description
    An alternative `Format String`_ to build archive IDs with.


extractor.*.archive-mode
------------------------
Type
    ``string``
Default
    ``"file"``
Description
    Controls when to write `archive IDs <extractor.*.archive-format_>`__
    to the archive database.

    ``"file"``
        Write IDs immediately
        after completing or skipping a file download.
    ``"memory"``
        Keep IDs in memory
        and only write them after successful job completion.


extractor.*.archive-prefix
--------------------------
Type
    `Format String`_
Default
    * ``""`` when `archive-table <extractor.*.archive-table_>`__ is set
    * ``"{category}"`` otherwise
Description
    Prefix for archive IDs.


extractor.*.archive-pragma
--------------------------
Type
    ``list`` of ``strings``
Example
    ``["journal_mode=WAL", "synchronous=NORMAL"]``
Description
    A list of SQLite ``PRAGMA`` statements to run during archive initialization.

    See `<https://www.sqlite.org/pragma.html#toc>`__
    for available ``PRAGMA`` statements and further details.


extractor.*.archive-table
-------------------------
Type
    `Format String`_
Default
    ``"archive"``
Example
    ``"{category}"``
Description
    `Format String`_ selecting the archive database table name.


extractor.*.actions
-------------------
Type
    * ``object`` (`pattern` → `Action(s)`_)
    * ``list`` of [`pattern`, `Action(s)`_] pairs
Example
    .. code:: json

        {
            "info:Logging in as .+"   : "level = debug",
            "warning:(?i)unable to .+": "exit 127",
            "error"                   : [
                "status |= 1",
                "exec notify.sh 'gdl error'",
                "abort"
            ]
        }

    .. code:: json

        [
            ["info:Logging in as .+"   , "level = debug"],
            ["warning:(?i)unable to .+", "exit 127"     ],
            ["error"                   , [
                "status |= 1",
                "exec notify.sh 'gdl error'",
                "abort"
            ]]
        ]

Description
    Perform an Action_ when logging a message matched by ``pattern``.

    ``pattern`` is parsed as severity level (``debug``, ``info``, ``warning``, ``error``, or integer value)
    followed by an optional
    `Python Regular Expression <https://docs.python.org/3/library/re.html#regular-expression-syntax>`__
    separated by a colon:
    ``<level>:<re>``

    Using ``*`` as `level` or leaving it empty
    matches logging messages of all levels:
    ``*:<re>`` or ``:<re>``


extractor.*.postprocessors
--------------------------
Type
    * |Postprocessor Configuration|_ object
    * ``list`` of |Postprocessor Configuration|_ objects
Example
    .. code:: json

        [
            {
                "name": "zip" ,
                "compression": "store"
            },
            {
                "name": "exec",
                "command": ["/home/foobar/script", "{category}", "{image_id}"]
            }
        ]

Description
    A list of `post processors <Postprocessor Configuration_>`__
    to be applied to each downloaded file in the specified order.

    | Unlike other options, a |postprocessors|_ setting at a deeper level
      does not override any |postprocessors|_ setting at a lower level.
    | Instead, all post processors from all applicable |postprocessors|_
      settings get combined into a single list.

    For example

    * an ``mtime`` post processor at ``extractor.postprocessors``,
    * a ``zip`` post processor at ``extractor.pixiv.postprocessors``,
    * and using ``--exec``

    will run all three post processors - ``mtime``, ``zip``, ``exec`` -
    for each downloaded ``pixiv`` file.


extractor.*.postprocessor-options
---------------------------------
Type
    ``object`` (`name` → `value`)
Example
    .. code:: json

        {
            "archive": null,
            "keep-files": true
        }

Description
    Additional `Postprocessor Options`_ that get added to each individual
    `post processor object <Postprocessor Configuration_>`__
    before initializing it and evaluating filters.


extractor.*.retries
-------------------
Type
    ``integer``
Default
    ``4``
Description
    Maximum number of times a failed HTTP request is retried before
    giving up, or ``-1`` for infinite retries.


extractor.*.retry-codes
-----------------------
Type
    ``list`` of ``integers``
Example
    ``[404, 429, 430]``
Description
    Additional `HTTP response status codes <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status>`__
    to retry an HTTP request on.

    ``2xx`` codes (success responses) and
    ``3xx`` codes (redirection messages)
    will never be retried and always count as success,
    regardless of this option.

    ``5xx`` codes (server error responses)  will always be retried,
    regardless of this option.


extractor.*.timeout
-------------------
Type
    ``float``
Default
    ``30.0``
Description
    Amount of time (in seconds) to wait for a successful connection
    and response from a remote server.

    This value gets internally used as the |timeout|_ parameter for the
    |requests.request()|_ method.


extractor.*.verify
------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Controls whether to verify SSL/TLS certificates for HTTPS requests.

    If this is a ``string``, it must be the path to a CA bundle to use
    instead of the default certificates.

    This value gets internally used as the |verify|_ parameter for the
    |requests.request()|_ method.


extractor.*.truststore
----------------------
Type
    ``bool``
Default
    ``false``
Description
    | Use a
      `truststore <https://truststore.readthedocs.io/en/latest/>`__
      ``SSLContext`` for verifying SSL/TLS certificates
    | to make use of your system's native certificate stores
      instead of relying on
      `certifi <https://pypi.org/project/certifi/>`__
      certificates.


extractor.*.download
--------------------
Type
    ``bool``
Default
    ``true``
Description
    Controls whether to download media files.

    Setting this to ``false`` won't download any files, but all other
    functions (`postprocessors`_, `download archive`_, etc.)
    will be executed as normal.


extractor.*.fallback
--------------------
Type
    ``bool``
Default
    ``true``
Description
    Use fallback download URLs when a download fails.


extractor.*.image-range
-----------------------
Type
    * ``string``
    * ``list`` of ``strings``
Example
    * ``"10-20"``
    * ``"-5, 10, 30-50, 100-"``
    * ``"10:21, 30:51:2, :5, 100:"``
    * ``["-5", "10", "30-50", "100-"]``
Description
    Index range(s) selecting which files to download.

    These can be specified as

    * index: ``3`` (file number 3)
    * range: ``2-4`` (files 2, 3, and 4)
    * `slice <https://docs.python.org/3/library/functions.html#slice>`__: ``3:8:2`` (files 3, 5, and 7)

    | Arguments for range and slice notation are optional
      and will default to begin (``1``) or end (``sys.maxsize``) if omitted.
    | For example ``5-``, ``5:``, and ``5::`` all mean "Start at file number 5".
Note
    The index of the first file is ``1``.


extractor.*.chapter-range
-------------------------
Type
    ``string``
Description
    Like `image-range <extractor.*.image-range_>`__,
    but applies to delegated URLs like manga chapters, etc.


extractor.*.image-filter
------------------------
Type
    * Condition_
    * ``list`` of Conditions_
Example
    * ``"re.search(r'foo(bar)+', description)"``
    * ``["width >= 1200", "width/height > 1.2"]``
Description
    Python Expression_ controlling which files to download.

    A file only gets downloaded when *all* of the given Expressions_ evaluate to ``True``.

    Available values are the filename-specific ones listed by ``-K`` or ``-j``.


extractor.*.chapter-filter
--------------------------
Type
    * Condition_
    * ``list`` of Conditions_
Example
    * ``"lang == 'en'"``
    * ``["language == 'French'", "10 <= chapter < 20"]``
Description
    Like `image-filter <extractor.*.image-filter_>`__,
    but applies to delegated URLs like manga chapters, etc.


extractor.*.image-unique
------------------------
Type
    ``bool``
Default
    ``false``
Description
    Ignore image URLs that have been encountered before during the
    current extractor run.


extractor.*.chapter-unique
--------------------------
Type
    ``bool``
Default
    ``false``
Description
    Like `image-unique <extractor.*.image-unique_>`__,
    but applies to delegated URLs like manga chapters, etc.


extractor.*.date-format
-----------------------
Type
    ``string``
Default
    ``"%Y-%m-%dT%H:%M:%S"``
Description
    Format string used to parse ``string`` values of
    `date-min` and `date-max`.

    See |strptime|_ for a list of formatting directives.
Note
    Despite its name, this option does **not** control how
    ``{date}`` metadata fields are formatted.
    To use a different formatting for those values other than the default
    ``%Y-%m-%d %H:%M:%S``, put |strptime|_ formatting directives
    after a colon ``:``, for example ``{date:%Y%m%d}``.


extractor.*.write-pages
-----------------------
Type
    * ``bool``
    * ``string``
Default
    ``false``
Description
    During data extraction,
    write received HTTP request data
    to enumerated files in the current working directory.
Special Values
    ``"all"``
        | Include HTTP request and response headers.
        | Hide ``Authorization``, ``Cookie``, and ``Set-Cookie`` values.
    ``"ALL"``
        Include all HTTP request and response headers.



Extractor-specific Options
==========================


extractor.ao3.formats
---------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"pdf"``
Example
    * ``"azw3,epub,mobi,pdf,html"``
    * ``["azw3", "epub", "mobi", "pdf", "html"]``
Description
    Format(s) to download.


extractor.arcalive.emoticons
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download emoticon images.


extractor.arcalive.gifs
-----------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Try to download ``.gif`` versions of ``.mp4`` videos.

    ``true`` | ``"fallback``
        Use the ``.gif`` version as primary URL
        and provide the ``.mp4`` one as
        `fallback <extractor.*.fallback_>`__.
    ``"check"``
        Check whether a ``.gif`` version is available
        by sending an extra HEAD request.
    ``false``
        Always download the ``.mp4`` version.


extractor.artstation.external
-----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Try to follow external URLs of embedded players.


extractor.artstation.max-posts
------------------------------
Type
    ``integer``
Default
    ``null``
Description
    Limit the number of posts/projects to download.


extractor.artstation.mviews
---------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download ``.mview`` files.


extractor.artstation.previews
-----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download embed previews.


extractor.artstation.videos
---------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download video clips.


extractor.artstation.search.pro-first
-------------------------------------
Type
    ``bool``
Default
    ``true``
Description
    Enable the "Show Studio and Pro member artwork first" checkbox
    when retrieving search results.


extractor.aryion.recursive
--------------------------
Type
    ``bool``
Default
    ``true``
Description
    Controls the post extraction strategy.

    ``true``
        Start on users' main gallery pages and
        recursively descend into subfolders
    ``false``
        Get posts from "Latest Updates" pages


extractor.batoto.domain
-----------------------
Type
    ``string``
Default
    ``"auto"``
Example
    ``"mangatoto.org"``
Description
    Specifies the domain used by ``batoto`` extractors.

    ``"auto"`` | ``"url"``
        Use the input URL's domain
    ``"nolegacy"``
        Use the input URL's domain
        - replace legacy domains with ``"xbato.org"``
    ``"nowarn"``
        Use the input URL's domain
        - do not warn about legacy domains
    any ``string``
        Use this domain


extractor.bbc.width
-------------------
Type
    ``integer``
Default
    ``1920``
Description
    Specifies the requested image width.

    This value must be divisble by 16 and gets rounded down otherwise.
    The maximum possible value appears to be ``1920``.


extractor.behance.modules
-------------------------
Type
    ``list`` of ``strings``
Default
    ``["image", "video", "mediacollection", "embed"]``
Description
    Selects which gallery modules to download from.
Supported Types
    * ``"image"``
    * ``"video"``
    * ``"mediacollection"``
    * ``"embed"``
    * ``"text"``


extractor.bellazon.order-posts
------------------------------
Type
    ``string``
Default
    ``"desc"``
Description
    Controls the order in which
    posts of a ``thread`` are processed.

    ``"asc"``
        Ascending order (oldest first)
    ``"desc"`` | ``"reverse"``
        Descending order (newest first)


extractor.bellazon.quoted
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract files from quoted content.


extractor.[blogger].api-key
---------------------------
Type
    ``string``
Description
    Custom Blogger API key.

    https://developers.google.com/blogger/docs/3.0/using#APIKey


extractor.[blogger].videos
--------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download embedded videos hosted on https://www.blogger.com/


extractor.bluesky.include
-------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    * ``"posts"`` if
      `reposts <extractor.bluesky.reposts_>`__ or
      `quoted <extractor.bluesky.quoted_>`__ is enabled
    * ``"media"`` otherwise
Example
    * ``"avatar,background,posts"``
    * ``["avatar", "background", "posts"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``info``
    * ``avatar``
    * ``background``
    * ``posts``
    * ``replies``
    * ``media``
    * ``video``
    * ``likes``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.bluesky.likes.endpoint
--------------------------------
Type
    ``string``
Default
    ``"listRecords"``
Description
    API endpoint to use for retrieving liked posts.

    ``"listRecords"``
        | Use the results from
          `com.atproto.repo.listRecords <https://docs.bsky.app/docs/api/com-atproto-repo-list-records>`__
        | Requires no login and alows accessing likes of all users,
          but uses one request to
          `getPostThread <https://docs.bsky.app/docs/api/app-bsky-feed-get-post-thread>`__
          per post,
    ``"getActorLikes"``
        | Use the results from
          `app.bsky.feed.getActorLikes <https://docs.bsky.app/docs/api/app-bsky-feed-get-actor-likes>`__
        | Requires login and only allows accessing your own likes.


extractor.bluesky.metadata
--------------------------
Type
    * ``bool``
    * ``string``
    * ``list`` of ``strings``
Default
    ``false``
Example
    * ``"facets,user"``
    * ``["facets", "user"]``
Description
    Extract additional metadata.

    ``facets``
        ``hashtags``, ``mentions``, ``uris``
    ``user``
        | Detailed ``user`` metadata for the user referenced in the input URL.
        | (`app.bsky.actor.getProfile <https://docs.bsky.app/docs/api/app-bsky-actor-get-profile>`__)


extractor.bluesky.post.depth
----------------------------
extractor.bluesky.likes.depth
-----------------------------
Type
    ``integer``
Default
    ``0``
Description
    Sets the maximum depth of returned reply posts.

    (See the ``depth`` parameter of `app.bsky.feed.getPostThread <https://docs.bsky.app/docs/api/app-bsky-feed-get-post-thread>`__)


extractor.bluesky.quoted
------------------------
Type
    ``bool``
Default
    ``false``
Description
    Fetch media from quoted posts.


extractor.bluesky.reposts
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Process reposts.


extractor.bluesky.videos
------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download videos.


extractor.boosty.allowed
------------------------
Type
    ``bool``
Default
    ``true``
Description
    Request only available posts.


extractor.boosty.bought
-----------------------
Type
    ``bool``
Default
    ``false``
Description
    Request only purchased posts for ``feed`` results.


extractor.boosty.metadata
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Provide detailed ``user`` metadata.


extractor.boosty.videos
-----------------------
Type
    * ``bool``
    * ``list`` of ``strings``
Default
    ``true``
Example
    ``["full_hd", "high", "medium"]``
Description
    Download videos.

    If this is a ``list``, it selects which format to try to download.
Possible Formats
    * ``ultra_hd`` (2160p)
    * ``quad_hd``  (1440p)
    * ``full_hd``  (1080p)
    * ``high``      (720p)
    * ``medium``    (480p)
    * ``low``       (360p)
    * ``lowest``    (240p)
    * ``tiny``      (144p)


extractor.booth.strategy
------------------------
Type
    ``string``
Default
    ``"webpage"``
Description
    Selects how to handle and extract file URLs.

    ``"webpage"``
        Retrieve the full HTML page
        and extract file URLs from it
    ``"fallback"``
        Use `fallback <extractor.*.fallback_>`__ URLs
        to `guess` each file's correct filename extension


extractor.bunkr.endpoint
------------------------
Type
    ``string``
Default
    ``"/api/_001_v2"``
Description
    API endpoint for retrieving file URLs.


extractor.bunkr.tlds
--------------------
Type
    ``bool``
Default
    ``false``
Description
    Controls which ``bunkr`` TLDs to accept.

    ``true``
        Match URLs with *all* possible TLDs (e.g. ``bunkr.xyz`` or ``bunkrrr.duck``)
    ``false``
        Match only URLs with known TLDs


extractor.cien.files
--------------------
Type
    ``list`` of ``strings``
Default
    ``["image", "video", "download", "gallery"]``
Description
    Determines the type and order of files to download.
Available Types
    * ``image``
    * ``video``
    * ``download``
    * ``gallery``


extractor.civitai.api
---------------------
Type
    ``string``
Default
    ``"trpc"``
Description
    Selects which API endpoints to use.

    ``"rest"``
        `Public REST API <https://developer.civitai.com/docs/api/public-rest>`__
    ``"trpc"``
        Internal tRPC API


extractor.civitai.api-key
-------------------------
Type
    ``string``
Description
    The API Key value generated in your
    `User Account Settings <https://civitai.com/user/account>`__
    to make authorized API requests.

    See `API/Authorization <https://developer.civitai.com/docs/api/public-rest#authorization>`__
    for details.


extractor.civitai.files
-----------------------
Type
    ``list`` of ``strings``
Default
    ``["image"]``
Description
    Determines the type and order of files to download when processing models.
Available Types
    * ``model``
    * ``image``
    * ``gallery``


extractor.civitai.include
-------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``["user-images", "user-videos"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``user-models``
    * ``user-posts``
    * ``user-images``
    * ``user-videos``
    * ``user-collections``
Note
    It is possible to use ``"all"`` instead of listing all values separately.

    To get a more complete set of metadata
    like ``model['name']`` and ``post['title']``,
    include ``user-models`` and ``user-posts``
    as well as the default ``user-images`` and ``user-videos``:

    ``["user-models", "user-posts", "user-images", "user-videos"]``


extractor.civitai.metadata
--------------------------
Type
    * ``bool``
    * ``string``
    * ``list`` of ``strings``
Default
    ``false``
Example
    * ``"generation,post,version"``
    * ``["version", "generation"]``
Description
    Extract additional ``generation``, ``version``, and ``post`` metadata.
Note
    This requires 1 or more additional API requests per image or video.


extractor.civitai.nsfw
----------------------
Type
    * ``bool``
    * ``string`` (``"api": "rest"``)
    * ``integer`` (``"api": "trpc"``)
Default
    ``true``
Description
    Download NSFW-rated images.

    * For ``"api": "rest"``, this can be one of
      ``"None"``, ``"Soft"``, ``"Mature"``, ``"X"``
      to set the highest returned mature content flag.

    * For ``"api": "trpc"``, this can be an ``integer``
      whose bits select the returned mature content flags.

      For example, ``28`` (``4|8|16``)  would return only
      ``R``, ``X``, and ``XXX`` rated images,
      while ``3`` (``1|2``) would return only
      ``None`` and ``Soft`` rated images,


extractor.civitai.period
------------------------
Type
    ``string``
Default
    ``"AllTime"``
Description
    Sets the ``period`` parameter
    when paginating over results.
Supported Values
    * ``"AllTime"``
    * ``"Year"``
    * ``"Month"``
    * ``"Week"``
    * ``"Day"``


extractor.civitai.sort
----------------------
Type
    ``string``
Default
    ``"Newest"``
Description
    Sets the ``sort`` parameter
    when paginating over results.
Supported Values
    * ``"Newest"``
    * ``"Oldest"``
    * ``"Most Reactions"``
    * ``"Most Comments"``
    * ``"Most Collected"``
Special Values
    ``"asc"``
        Ascending order (``"Oldest"``)
    ``"desc"`` | ``"reverse"``
        Descending order (``"Newest"``)


extractor.civitai.quality
-------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"original=true"``
Example
    * ``"width=1280,quality=90"``
    * ``["width=1280", "quality=90"]``
Description
    A (comma-separated) list of image quality options
    to pass with every image URL.

    Known available options include ``original``, ``quality``, ``width``
Note
    Set this option to an arbitrary letter, e.g., ``"w"``,
    to download images in JPEG format at their original resolution.


extractor.civitai.quality-videos
--------------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"quality=100"``
Example
    * ``"+transcode=true,quality=100"``
    * ``["+", "transcode=true", "quality=100"]``
Description
    A (comma-separated) list of video quality options
    to pass with every video URL.

    Known available options include ``original``, ``quality``, ``transcode``

    Use ``+`` as first character to `add` the given options to the
    `quality <extractor.civitai.quality_>`__ ones.


extractor.civitai.search-models.token
-------------------------------------
extractor.civitai.search-images.token
-------------------------------------
Type
    ``string``
Default
    ``"8c46eb2508e21db1e9828a97968d91ab1ca1caa5f70a00e88a2ba1e286603b61"``
Description
    ``Authorization`` header value used for `/multi-search` queries.


extractor.comick.lang
---------------------
Type
    * ``string``
    * ``list`` of ``strings``
Example
    * ``"en"``
    * ``"fr,it,pl"``
    * ``["fr", "it", "pl"]``
Description
    |ISO 639-1| code(s) to filter chapters by.


extractor.cyberdrop.domain
--------------------------
Type
    ``string``
Default
    ``null``
Example
    ``"cyberdrop.to"``
Description
    Specifies the domain used by ``cyberdrop`` regardless of input URL.

    Setting this option to ``"auto"``
    uses the same domain as a given input URL.


extractor.cyberfile.password
----------------------------
Type
    ``string``
Default
    ``""``
Description
    Password value used to access protected files and folders.

    Leave this value empty or undefined
    to be interactively prompted for a password when needed
    (see `getpass() <https://docs.python.org/3/library/getpass.html#getpass.getpass>`__).


extractor.[Danbooru].external
-----------------------------
Type
    ``bool``
Default
    ``false``
Description
    For unavailable or restricted posts,
    follow the ``source`` and download from there if possible.


extractor.[Danbooru].pool.order-posts
-------------------------------------
extractor.[Danbooru].favgroup.order-posts
-----------------------------------------
Type
    ``string``
Default
    ``"pool"``
Description
    Controls the order in which ``pool``/``favgroup`` posts are returned.

    ``"pool"`` | ``"pool_asc"`` | ``"asc"`` | ``"asc_pool"``
        Pool order
    ``"pool_desc"`` | ``"desc_pool"`` | ``"desc"``
        Reverse Pool order
    ``"id"`` | ``"id_desc"`` | ``"desc_id"``
        Descending Post ID order
    ``"id_asc"`` | ``"asc_id"``
        Ascending Post ID order


extractor.[Danbooru].ugoira
---------------------------
Type
    ``bool``
Default
    ``false``
Description
    Controls the download target for Ugoira posts.

    ``true``
        ZIP archives
    ``false``
        Converted video files


extractor.[Danbooru].metadata
-----------------------------
Type
    * ``bool``
    * ``string``
    * ``list`` of ``strings``
Default
    ``false``
Example
    * ``"replacements,comments,ai_tags"``
    * ``["replacements", "comments", "ai_tags"]``
Description
    Extract additional metadata
    (notes, artist commentary, parent, children, uploader)

    It is possible to specify a custom list of metadata includes.
    See `available_includes <https://github.com/danbooru/danbooru/blob/2cf7baaf6c5003c1a174a8f2d53db010cf05dca7/app/models/post.rb#L1842-L1849>`__
    for possible field names. ``aibooru`` also supports ``ai_metadata``.
Note
    This requires 1 additional HTTP request per 200-post batch.


extractor.[Danbooru].threshold
------------------------------
Type
    * ``string``
    * ``integer``
Default
    ``"auto"``
Description
    Stop paginating over API results if the length of a batch of returned
    posts is less than the specified number. Defaults to the per-page limit
    of the current instance, which is 200.
Note
    Changing this setting is normally not necessary. When the value is
    greater than the per-page limit, gallery-dl will stop after the first
    batch. The value cannot be less than 1.


extractor.dankefuerslesen.zip
-----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download each chapter as a single ZIP archive instead of individual images.


extractor.deviantart.auto-watch
-------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Automatically watch users when encountering "Watchers-Only Deviations"
    (requires a `refresh-token <extractor.deviantart.refresh-token_>`_).


extractor.deviantart.auto-unwatch
---------------------------------
Type
    ``bool``
Default
    ``false``
Description
    After watching a user through `auto-watch <extractor.deviantart.auto-watch_>`_,
    unwatch that user at the end of the current extractor run.


extractor.deviantart.comments
-----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract ``comments`` metadata.


extractor.deviantart.comments-avatars
-------------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download the avatar of each commenting user.
Note
    Enabling this option also enables deviantart.comments_.


extractor.deviantart.extra
--------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download extra Sta.sh resources from
    description texts and journals.
Note
    Enabling this option also enables deviantart.metadata_.


extractor.deviantart.flat
-------------------------
Type
    ``bool``
Default
    ``true``
Description
    Select the directory structure created by the Gallery- and
    Favorite-Extractors.

    ``true``
        Use a flat directory structure.
    ``false``
            Collect a list of all gallery ``folders`` or
            favorites ``collections`` and transfer any further work to other
            extractors (``folder`` or ``collection``), which will then
            create individual subdirectories for each of them.
Note
    Going through all gallery folders won't
    fetch deviations not contained in any folder.


extractor.deviantart.folders
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Provide a ``folders`` metadata field that contains the names of all
    folders a deviation is present in.
Note
    Gathering this information requires a lot of API calls.
    Use with caution.


extractor.deviantart.group
--------------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Check whether the profile name in a given URL
    belongs to a group or a regular user.

    When disabled, assume every given profile name
    belongs to a regular user.
Special Values
    ``"skip"``
        Skip groups


extractor.deviantart.include
----------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"gallery"``
Example
    * ``"favorite,journal,scraps"``
    * ``["favorite", "journal", "scraps"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``avatar``
    * ``background``
    * ``gallery``
    * ``scraps``
    * ``journal``
    * ``favorite``
    * ``status``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.deviantart.intermediary
---------------------------------
Type
    ``bool``
Default
    ``true``
Description
    For older non-downloadable images,
    download a higher-quality ``/intermediary/`` version.


extractor.deviantart.journals
-----------------------------
Type
    ``string``
Default
    ``"html"``
Description
    Selects the output format for textual content. This includes journals,
    literature and status updates.

    ``"html"``
        HTML with (roughly) the same layout as on DeviantArt.
    ``"text"``
        Plain text with image references and HTML tags removed.
    ``"none"``
        Don't download textual content.


extractor.deviantart.mature
---------------------------
Type
    ``bool``
Default
    ``true``
Description
    Enable mature content.

    This option simply sets the |mature_content|_ parameter for API
    calls to either ``"true"`` or ``"false"`` and does not do any other
    form of content filtering.


extractor.deviantart.metadata
-----------------------------
Type
    * ``bool``
    * ``string``
    * ``list`` of ``strings``
Default
    ``false``
Example
    * ``"stats,submission"``
    * ``["camera", "stats", "submission"]``
Description
    Extract additional metadata for deviation objects.

    Provides
    ``description``, ``tags``, ``license``, and ``is_watching``
    fields when enabled.

    It is possible to request extended metadata by specifying a list of

    ``camera``
        EXIF information if available
    ``stats``
        Deviation statistics
    ``submission``
        Submission information
    ``collection``
        Favourited folder information (requires a `refresh token <extractor.deviantart.refresh-token_>`__)
    ``gallery``
        Gallery folder information (requires a `refresh token <extractor.deviantart.refresh-token_>`__)
Note
    Set this option to ``"all"`` to request all extended metadata categories.

    See `/deviation/metadata <https://www.deviantart.com/developers/http/v1/20210526/deviation_metadata/7824fc14d6fba6acbacca1cf38c24158>`__
    for official documentation.


extractor.deviantart.original
-----------------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Download original files if available.

    Setting this option to ``"images"`` only downloads original
    files if they are images and falls back to preview versions for
    everything else (archives, videos, etc.).


extractor.deviantart.pagination
-------------------------------
Type
    ``string``
Default
    ``"api"``
Description
    Controls when to stop paginating over API results.

    ``"api"``
        Trust the API and stop when ``has_more`` is ``false``.
    ``"manual"``
        Disregard ``has_more`` and only stop when a batch of results is empty.


extractor.deviantart.previews
-----------------------------
Type
    ``bool``
Default
    ``false``
Description
    For non-image files (archives, videos, etc.),
    also download the file's preview image.

    Set this option to ``"all"`` to download previews for all files.


extractor.deviantart.public
---------------------------
Type
    ``bool``
Default
    ``true``
Description
    Use a public access token for API requests.

    Disable this option to *force* using a private token for all requests
    when a `refresh token <extractor.deviantart.refresh-token_>`__ is provided.


extractor.deviantart.quality
----------------------------
Type
    * ``integer``
    * ``string``
Default
    ``100``
Description
    JPEG quality level of images for which
    an original file download is not available.

    Set this to ``"png"`` to download a PNG version of these images instead.


extractor.deviantart.refresh-token
----------------------------------
Type
    ``string``
Default
    ``null``
Description
    The ``refresh-token`` value you get from
    `linking your DeviantArt account to gallery-dl <OAuth_>`__.

    Using a ``refresh-token`` allows you to access private or otherwise
    not publicly available deviations.
Note
    The ``refresh-token`` becomes invalid
    `after 3 months <https://www.deviantart.com/developers/authentication#refresh>`__
    or whenever your `cache file <cache.file_>`__ is deleted or cleared.


extractor.deviantart.wait-min
-----------------------------
Type
    ``integer``
Default
    ``0``
Description
    Minimum wait time in seconds before API requests.


extractor.deviantart.avatar.formats
-----------------------------------
Type
    ``list`` of ``strings``
Example
    ``["original.jpg", "big.jpg", "big.gif", ".png"]``
Description
    Avatar URL formats to return.

    | Each format is parsed as ``SIZE.EXT``.
    | Leave ``SIZE`` empty to download the regular, small avatar format.
Note
    | Consider updating
      `archive-format <extractor.*.archive-format_>`__
      for ``avatar`` results to
    | ``"a_{_username}_{index}{title[6:]}.{extension}"``
    | or similar when using an
      `archive <extractor.*.archive_>`__
      to be able to handle different formats.


extractor.deviantart.folder.subfolders
--------------------------------------
Type
    ``bool``
Default
    ``true``
Description
    Also extract subfolder content.


extractor.discord.embeds
------------------------
Type
    ``list`` of ``strings``
Default
    ``["image", "gifv", "video"]``
Description
    Selects which embed types to download from.

    Supported embed types are
    ``image``, ``gifv``, ``video``, ``rich``, ``article``, ``link``.


extractor.discord.threads
-------------------------
Type
    ``bool``
Default
    ``true``
Description
    Extract threads from Discord text channels.


extractor.discord.token
-----------------------
Type
    ``string``
Description
    Discord Bot Token for API requests.

    You can follow `this guide <https://github.com/Tyrrrz/DiscordChatExporter/blob/master/.docs/Token-and-IDs.md#how-to-get-a-user-token>`__ to get a token.


extractor.dynastyscans.anthology.metadata
-----------------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract ``alert``, ``description``, and ``status`` metadata
    from an anthology's HTML page.


extractor.[E621].metadata
-------------------------
Type
    * ``bool``
    * ``string``
    * ``list`` of ``strings``
Default
    ``false``
Example
    * ``"notes,pools"``
    * ``["notes", "pools"]``
Description
    Extract additional metadata (notes, pool metadata) if available.
Note
    This requires 0-2 additional HTTP requests per post.


extractor.[E621].threshold
--------------------------
Type
    * ``string``
    * ``integer``
Default
    ``"auto"``
Description
    Stop paginating over API results if the length of a batch of returned
    posts is less than the specified number. Defaults to the per-page limit
    of the current instance, which is 320.
Note
    Changing this setting is normally not necessary. When the value is
    greater than the per-page limit, gallery-dl will stop after the first
    batch. The value cannot be less than 1.


extractor.erome.user.reposts
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Include reposts when extracting albums from a user profile.


extractor.exhentai.domain
-------------------------
Type
    ``string``
Default
    ``"auto"``
Description
    ``"auto"``
        Use ``e-hentai.org`` or ``exhentai.org``
        depending on the input URL
    ``"e-hentai.org"``
        Use ``e-hentai.org`` for all URLs
    ``"exhentai.org"``
        Use ``exhentai.org`` for all URLs


extractor.exhentai.fallback-retries
-----------------------------------
Type
    ``integer``
Default
    ``2``
Description
    Number of times a failed image gets retried
    or ``-1`` for infinite retries.


extractor.exhentai.fav
----------------------
Type
    ``string``
Example
    ``"4"``
Description
    After downloading a gallery,
    add it to your account's favorites as the given category number.
Note
    Set this to `"favdel"` to remove galleries from your favorites.

    This will remove any Favorite Notes when applied
    to already favorited galleries.


extractor.exhentai.gp
---------------------
Type
    ``string``
Default
    ``"resized"``
Description
    Selects how to handle "you do not have enough GP" errors.

    * `"resized"`: Continue downloading `non-original <extractor.exhentai.original_>`__ images.
    * `"stop"`: Stop the current extractor run.
    * `"wait"`: Wait for user input before retrying the current image.


extractor.exhentai.limits
-------------------------
Type
    ``integer``
Default
    ``null``
Description
    Set a custom image download limit and perform
    `limits-action <extractor.exhentai.limits-action_>`__
    when it gets exceeded.


extractor.exhentai.limits-action
--------------------------------
Type
    ``string``
Default
    ``"stop"``
Description
    Action to perform when the image limit is exceeded.

    * `"stop"`: Stop the current extractor run.
    * `"wait"`: Wait for user input.
    * `"reset"`: Spend GP to reset your account's image limits.


extractor.exhentai.metadata
---------------------------
Type
    ``bool``
Default
    ``false``
Description
    Load extended gallery metadata from the
    `API <https://ehwiki.org/wiki/API#Gallery_Metadata>`_.

    * Adds ``archiver_key``, ``posted``, and ``torrents``
    * Provides exact ``date`` and ``filesize``


extractor.exhentai.original
---------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download full-sized original images if available.


extractor.exhentai.source
-------------------------
Type
    ``string``
Default
    ``"gallery"``
Description
    Selects an alternative source to download files from.

    ``"hitomi"``
         Download the corresponding gallery from ``hitomi.la``
    ``"metadata"``
        Load only a gallery's metadata from the
        `API <https://ehwiki.org/wiki/API#Gallery_Metadata>`_


extractor.exhentai.tags
-----------------------
Type
    ``bool``
Default
    ``false``
Description
    Group ``tags`` by type and
    provide them as ``tags_<type>`` metadata fields,
    for example ``tags_artist`` or ``tags_character``.


extractor.facebook.author-followups
-----------------------------------
Type
    ``bool``
Default
    ``false``
description
    Extract comments that include photo attachments made by the author of the post.


extractor.facebook.include
--------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"photos"``
Example
    * ``"avatar,photos"``
    * ``["avatar", "photos"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``info``
    * ``avatar``
    * ``photos``
    * ``albums``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.facebook.videos
-------------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Control video download behavior.

    ``true``
        Extract and download video & audio separately.
    ``"ytdl"``
        Let |ytdl| handle video extraction and download, and merge video & audio streams.
    ``false``
        Ignore videos.


extractor.fanbox.comments
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract ``comments`` metadata.
Note
    This requires 1 or more additional API requests per post,
    depending on the number of comments.


extractor.fanbox.embeds
-----------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Control behavior on embedded content from external sites.

    ``true``
        Extract embed URLs and download them if supported
        (videos are not downloaded).
    ``"ytdl"``
        Like ``true``, but let |ytdl| handle video
        extraction and download for YouTube, Vimeo, and SoundCloud embeds.
    ``false``
        Ignore embeds.


extractor.fanbox.fee-max
------------------------
Type
    ``integer``
Description
    Do not request API data or extract files from posts
    that require a fee (``feeRequired``) greater than the specified amount.
Note
    This option has no effect on individual post URLs.


extractor.fanbox.metadata
-------------------------
Type
    * ``bool``
    * ``string``
    * ``list`` of ``strings``
Default
    ``false``
Example
    * ``user,plan,comments``
    * ``["user", "plan", "comments"]``
Description
    Extract ``plan`` and extended ``user`` metadata.
Supported Fields
    * ``comments``
    * ``plan``
    * ``user``
Note
    ``comments`` can also be enabled via
    `fanbox.comments <extractor.fanbox.comments_>`__


extractor.fansly.formats
------------------------
Type
    ``list`` of ``integers``
Default
    ``[1, 2, 3, 4, 302, 303]``
Description
    List of file formats to consider during format selection.


extractor.fansly.token
----------------------
Type
    ``string``
Example
    ``"kX7pL9qW3zT2rY8mB5nJ4vC6xF1tA0hD8uE2wG9yR3sQ7iZ4oM5jN6cP8lV0bK2tU9aL1eW"``
Description
    ``authorization`` header value
    used for requests to ``https://apiv3.fansly.com/api``
    to access locked content.


extractor.flickr.access-token & .access-token-secret
----------------------------------------------------
Type
    ``string``
Default
    ``null``
Description
    The ``access_token`` and ``access_token_secret`` values you get
    from `linking your Flickr account to gallery-dl <OAuth_>`__.


extractor.flickr.contexts
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    For each photo, return the albums and pools it belongs to
    as ``set`` and ``pool`` metadata.
Note
    This requires 1 additional API call per photo.
    See `flickr.photos.getAllContexts <https://www.flickr.com/services/api/flickr.photos.getAllContexts.html>`__ for details.


extractor.flickr.exif
---------------------
Type
    ``bool``
Default
    ``false``
Description
    For each photo, return its EXIF/TIFF/GPS tags
    as ``exif`` and ``camera`` metadata.
Note
    This requires 1 additional API call per photo.
    See `flickr.photos.getExif <https://www.flickr.com/services/api/flickr.photos.getExif.html>`__ for details.


extractor.flickr.info
---------------------
Type
    ``bool``
Default
    ``false``
Description
    For each photo, retrieve its "full" metadata as provided by
    `flickr.photos.getInfo <https://www.flickr.com/services/api/flickr.photos.getInfo.html>`__
Note
    This requires 1 additional API call per photo.


extractor.flickr.metadata
-------------------------
Type
    * ``bool``
    * ``string``
    * ``list`` of ``strings``
Default
    ``false``
Example
    * ``license,last_update,machine_tags``
    * ``["license", "last_update", "machine_tags"]``
Description
    Extract additional metadata
    (license, date_taken, original_format, last_update, geo, machine_tags, o_dims)

    It is possible to specify a custom list of metadata includes.
    See `the extras parameter <https://www.flickr.com/services/api/flickr.people.getPhotos.html>`__
    in `Flickr's API docs <https://www.flickr.com/services/api/>`__
    for possible field names.


extractor.flickr.profile
------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract additional ``user`` profile metadata.
Note
    This requires 1 additional API call per user profile.
    See `flickr.people.getInfo <https://www.flickr.com/services/api/flickr.people.getInfo.html>`__ for details.


extractor.flickr.videos
-----------------------
Type
    ``bool``
Default
    ``true``
Description
    Extract and download videos.


extractor.flickr.size-max
--------------------------
Type
    * ``integer``
    * ``string``
Default
    ``null``
Description
    Sets the maximum allowed size for downloaded images.

    * If this is an ``integer``, it specifies the maximum image dimension
      (width and height) in pixels.
    * If this is a ``string``, it should be one of Flickr's format specifiers
      (``"Original"``, ``"Large"``, ... or ``"o"``, ``"k"``, ``"h"``,
      ``"l"``, ...) to use as an upper limit.


extractor.furaffinity.descriptions
----------------------------------
Type
    ``string``
Default
    ``"text"``
Description
    Controls the format of ``description`` metadata fields.

    ``"text"``
        Plain text with HTML tags removed
    ``"html"``
        Raw HTML content


extractor.furaffinity.external
------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Follow external URLs linked in descriptions.


extractor.furaffinity.include
-----------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"gallery"``
Example
    * ``"scraps,favorite"``
    * ``["scraps", "favorite"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``gallery``
    * ``scraps``
    * ``favorite``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.furaffinity.layout
----------------------------
Type
    ``string``
Default
    ``"auto"``
Description
    Selects which site layout to expect when parsing posts.

    ``"auto"``
        Automatically differentiate between ``"old"`` and ``"new"``
    ``"old"``
        Expect the *old* site layout
    ``"new"``
        Expect the *new* site layout


extractor.gelbooru.api-key & .user-id
-------------------------------------
Type
    ``string``
Default
    ``null``
Description
    Values from the `API Access Credentials` section
    found at the bottom of your account's
    `Options <https://gelbooru.com/index.php?page=account&s=options>`__
    page.


extractor.gelbooru.favorite.order-posts
---------------------------------------
Type
    ``string``
Default
    ``"desc"``
Description
    Controls the order in which favorited posts are returned.

    ``"asc"``
        Ascending favorite date order (oldest first)
    ``"desc"`` | ``"reverse"``
        Descending favorite date order (newest first)


extractor.generic.enabled
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Match **all** URLs not otherwise supported by gallery-dl,
    even ones without a ``generic:`` prefix.


extractor.gofile.api-token
--------------------------
Type
    ``string``
Default
    ``null``
Description
    API token value found at the bottom of your `profile page <https://gofile.io/myProfile>`__.

    If not set, a temporary guest token will be used.


extractor.gofile.website-token
------------------------------
Type
    ``string``
Description
    API token value used during API requests.

    An invalid or not up-to-date value
    will result in ``401 Unauthorized`` errors.

    Keeping this option unset will use an extra HTTP request
    to attempt to fetch the current value used by gofile.


extractor.gofile.recursive
--------------------------
Type
    ``bool``
Default
    ``false``
Description
    Recursively download files from subfolders.


extractor.hdoujin.cbz
---------------------
Type
    ``bool``
Default
    ``false``
Description
    Download each gallery as a single ``.cbz`` file.
Note
    Requires a
    `token <extractor.hdoujin.token_>`__


extractor.hdoujin.crt
---------------------
Type
    ``string``
Example
    * ``"0542daa9-352c-4fd5-a497-6c6d5cf07423"``
    * ``"/12345/a1b2c3d4e5f6?crt=0542daa9-352c-4fd5-a497-6c6d5cf07423"``
Description
    The ``crt`` query parameter value
    sent when fetching gallery data.

    To get this value:

    * Open your browser's Developer Tools (F12)
    * Select `Network` → `XHR`
    * Open a gallery page
    * Select the last `Network` entry and copy its ``crt`` value
Note
    You will also need your browser's
    `user-agent <extractor.*.user-agent_>`__


extractor.hdoujin.format
------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``["0", "1600", "1280", "980", "780"]``
Description
    Name(s) of the image format to download.

    When more than one format is given, the first available one is selected.

    | Possible formats are
    | ``"780"``, ``"980"``, ``"1280"``, ``"1600"``, ``"0"`` (original)


extractor.hdoujin.tags
----------------------
Type
    ``bool``
Default
    ``false``
Description
    Group ``tags`` by type and
    provide them as ``tags_<type>`` metadata fields,
    for example ``tags_artist`` or ``tags_character``.


extractor.hdoujin.token
-----------------------
Type
    ``string``
Example
    * ``"3f1a9b72-4e4d-4f4e-9e5d-4a2b99f7c893"``
    * ``"Bearer 3f1a9b72-4e4d-4f4e-9e5d-4a2b99f7c893"``
    * ``"Authorization: Bearer 3f1a9b72-4e4d-4f4e-9e5d-4a2b99f7c893"``
Description
    ``Authorization`` header value
    used for requests to ``https://api.hdoujin.org``
    to access ``favorite`` galleries
    or download
    `.cbz <extractor.hdoujin.cbz_>`__
    archives.


extractor.hentaifoundry.descriptions
------------------------------------
Type
    ``string``
Default
    ``"text"``
Description
    Controls the format of ``description`` metadata fields.

    ``"text"``
        Plain text with HTML tags removed
    ``"html"``
        Raw HTML content


extractor.hentaifoundry.include
-------------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"pictures"``
Example
    * ``"scraps,stories"``
    * ``["scraps", "stories"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``pictures``
    * ``scraps``
    * ``stories``
    * ``favorite``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.hitomi.format
-----------------------
Type
    ``string``
Default
    ``"webp"``
Description
    Selects which image format to download.
Available Formats
    * ``"webp"``
    * ``"avif"``


extractor.imagechest.access-token
---------------------------------
Type
    ``string``
Description
    Your personal Image Chest access token.

    These tokens allow using the API instead of having to scrape HTML pages,
    providing more detailed metadata.
    (``date``, ``description``, etc)

    See https://imgchest.com/docs/api/1.0/general/authorization
    for instructions on how to generate such a token.


extractor.imgur.client-id
-------------------------
Type
    ``string``
Description
    Custom Client ID value for API requests.


extractor.imgur.mp4
-------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Controls whether to choose the GIF or MP4 version of an animation.

    ``true``
        Follow Imgur's advice and choose MP4 if the
        ``prefer_video`` flag in an image's metadata is set.
    ``false``
        Always choose GIF.
    ``"always"``
        Always choose MP4.


extractor.inkbunny.orderby
--------------------------
Type
    ``string``
Default
    ``"create_datetime"``
Description
    Value of the ``orderby`` parameter for submission searches.

    (See `API#Search <https://wiki.inkbunny.net/wiki/API#Search>`__
    for details)


extractor.instagram.api
-----------------------
Type
    ``string``
Default
    ``"rest"``
Description
    Selects which API endpoints to use.

    ``"rest"``
        REST API - higher-resolution media
    ``"graphql"``
        GraphQL API - lower-resolution media


extractor.instagram.cursor
--------------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Example
    ``"3414259811154179155_25025320"``
Description
    Controls from which position to start the extraction process from.

    ``true``
        | Start from the beginning.
        | Log the most recent ``cursor`` value when interrupted before reaching the end.
    ``false``
        Start from the beginning.
    any ``string``
        Start from the position defined by this value.


extractor.instagram.include
---------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"posts"``
Example
    * ``"stories,highlights,posts"``
    * ``["stories", "highlights", "posts"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``posts``
    * ``reels``
    * ``tagged``
    * ``stories``
    * ``highlights``
    * ``info``
    * ``avatar``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.instagram.max-posts
-----------------------------
Type
    ``integer``
Default
    ``null``
Description
    Limit the number of posts to download.


extractor.instagram.metadata
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Provide extended ``user`` metadata even when referring to a user by ID,
    e.g. ``instagram.com/id:12345678``.
Note
    This metadata is always available when referring to a user by name,
    e.g. ``instagram.com/USERNAME``.


extractor.instagram.order-files
-------------------------------
Type
    ``string``
Default
    ``"asc"``
Description
    Controls the order in which files of each post are returned.

    ``"asc"``
        Same order as displayed in a post
    ``"desc"`` | ``"reverse"``
        Reverse order as displayed in a post
Note
    This option does *not* affect ``{num}``.
    To enumerate files in reverse order, use ``count - num + 1``.


extractor.instagram.order-posts
-------------------------------
Type
    ``string``
Default
    ``"asc"``
Description
    Controls the order in which posts are returned.

    ``"asc"``
        Same order as displayed
    ``"desc"`` | ``"reverse"``
        Reverse order as displayed
    ``"id"`` or ``"id_asc"``
        Ascending order by ID
    ``"id_desc"``
        Descending order by ID
Note
    This option only affects ``highlights``.


extractor.instagram.previews
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download video previews.


extractor.instagram.videos
--------------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Controls video download behavior.

    ``true`` | ``"dash"`` | ``"ytdl"``
        Download videos from ``video_dash_manifest`` data using |ytdl|
    ``"merged"``
        Download pre-merged video formats
    ``false``
        Do not download videos


extractor.instagram.warn-images
-------------------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Show a warning when downloading images
    with a resolution smaller than the `original`.

    ``true``
        Show a warning when at least one dimension
        is smaller than the reported `original` resolution
    ``"all"`` | ``"both"``
        Show a warning only when both ``width`` and ``height``
        are smaller than the reported `original` resolution
    ``false``
        Do not show a warning


extractor.instagram.warn-videos
-------------------------------
Type
    ``bool``
Default
    ``true``
Description
    Show a warning when downloading videos with a
    `User-Agent <extractor.*.user-agent_>`__
    header causing potentially lowered video quality.


extractor.instagram.stories.split
---------------------------------
Type
    * ``bool``
Default
    ``false``
Description
    Split ``stories`` elements into separate posts.


extractor.itaku.include
-----------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"gallery"``
Example
    * ``"stars,gallery"``
    * ``["stars", "gallery"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``gallery``
    * ``posts``
    * ``followers``
    * ``following``
    * ``stars``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.itaku.videos
----------------------
Type
    ``bool``
Default
    ``true``
Description
    Download video files.


extractor.iwara.include
-----------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``["user-images", "user-videos"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``user-images``
    * ``user-videos``
    * ``user-playlists``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.kemono.archives
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract additional metadata for ``archives`` files, including
    ``file``, ``file_list``, and ``password``.
Note
    This requires 1 additional HTTP request per ``archives`` file.


extractor.kemono.comments
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract ``comments`` metadata.
Note
    This requires 1 additional HTTP request per post.


extractor.kemono.duplicates
---------------------------
Type
    * ``bool``
    * ``string``
    * ``list`` of ``strings``
Default
    ``false``
Example
    * ``"attachment,inline"``
    * ``["file", "attachment"]``
Description
    Controls how to handle duplicate files in a post.

    ``true``
        Download duplicates
    ``false``
        Ignore duplicates
    any ``list`` or ``string``
        | Download a duplicate file if its ``type`` is in the given list
        | Ignore it otherwise


extractor.kemono.dms
--------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract a user's direct messages as ``dms`` metadata.


extractor.kemono.announcements
------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract a user's announcements as ``announcements`` metadata.


extractor.kemono.endpoint
-------------------------
Type
    ``string``
Default
    ``"posts"``
Description
    API endpoint to use for retrieving creator posts.

    ``"posts"`` | ``"legacy"``
        Provides only limited metadata.
    ``"posts+"`` | ``"legacy+"``
        Provides full metadata,
        but requires an additional API request for each post.


extractor.kemono.favorites
--------------------------
Type
    ``string``
Default
    ``"artist"``
Description
    Determines the type of favorites to be downloaded.

    Available types are ``artist``, and ``post``.


extractor.kemono.files
----------------------
Type
    ``list`` of ``strings``
Default
    ``["attachments", "file", "inline"]``
Description
    Determines the type and order of files to be downloaded.
Available Types
    * ``file``
    * ``attachments``
    * ``inline``


extractor.kemono.max-posts
--------------------------
Type
    ``integer``
Default
    ``null``
Description
    Limit the number of posts to download.


extractor.kemono.metadata
-------------------------
Type
    ``bool``
Default
    ``true``
Description
    Extract ``username`` and ``user_profile`` metadata.


extractor.kemono.revisions
--------------------------
Type
    * ``bool``
    * ``string``
Default
    ``false``
Description
    Extract post revisions.

    Set this to ``"unique"`` to filter out duplicate revisions.
Note
    This requires 1 additional HTTP request per post.


extractor.kemono.order-revisions
--------------------------------
Type
    ``string``
Default
    ``"desc"``
Description
    Controls the order in which
    `revisions <extractor.kemono.revisions_>`__
    are returned.

    ``"asc"`` | ``"reverse"``
        Ascending order (oldest first)
    ``"desc"``
        Descending order (newest first)


extractor.kemono.discord.order-posts
------------------------------------
Type
    ``string``
Default
    ``"asc"``
Description
    Controls the order in which
    ``discord`` posts
    are returned.

    ``"asc"``
        Ascending order (oldest first)
    ``"desc"`` | ``"reverse"``
        Descending order (newest first)


extractor.khinsider.covers
--------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download album cover images.


extractor.khinsider.format
--------------------------
Type
    ``string``
Default
    ``"mp3"``
Description
    The name of the preferred file format to download.

    Use ``"all"`` to download all available formats,
    or a (comma-separated) list to select multiple formats.

    If the selected format is not available,
    the first in the list gets chosen (usually `mp3`).


extractor.lolisafe.domain
-------------------------
Type
    ``string``
Default
    ``null``
Description
    Specifies the domain used by a ``lolisafe`` extractor
    regardless of input URL.

    Setting this option to ``"auto"``
    uses the same domain as a given input URL.


extractor.luscious.gif
----------------------
Type
    ``bool``
Default
    ``false``
Description
    Format in which to download animated images.

    Use ``true`` to download animated images as gifs and ``false``
    to download as mp4 videos.


extractor.mangadex.api-server
-----------------------------
Type
    ``string``
Default
    ``"https://api.mangadex.org"``
Description
    The server to use for API requests.


extractor.mangadex.api-parameters
---------------------------------
Type
    ``object`` (`name` → `value`)
Example
    ``{"order[updatedAt]": "desc"}``
Description
    Additional query parameters to send when fetching manga chapters.

    (See `/manga/{id}/feed <https://api.mangadex.org/docs/swagger.html#/Manga/get-manga-id-feed>`__
    and `/user/follows/manga/feed <https://api.mangadex.org/docs/swagger.html#/Feed/get-user-follows-manga-feed>`__)


extractor.mangadex.lang
-----------------------
Type
    * ``string``
    * ``list`` of ``strings``
Example
    * ``"en"``
    * ``"fr,it"``
    * ``["fr", "it"]``
Description
    |ISO 639-1| code(s) to filter chapters by.


extractor.mangadex.ratings
--------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``["safe", "suggestive", "erotica", "pornographic"]``
Example
    * ``"safe"``
    * ``"erotica,suggestive"``
    * ``["erotica", "suggestive"]``
Description
    List of acceptable content ratings for returned chapters.


extractor.mangafire.manga.lang
------------------------------
Type
    ``string``
Default
    ``"en"``
Description
    |ISO 639-1| code selecting which chapters to download.


extractor.mangareader.manga.lang
--------------------------------
Type
    ``string``
Default
    ``"en"``
Example
    ``"pt-br"``
Description
    |ISO 639-1| code selecting which chapters to download.


extractor.mangapark.source
--------------------------
Type
    * ``string``
    * ``integer``
Example
    * ``"koala:en"``
    * ``15150116``
Description
    Select chapter source and language for a manga.

    | The general syntax is ``"<source name>:<ISO 639-1 language code>"``.
    | Both are optional, meaning ``"koala"``, ``"koala:"``, ``":en"``,
      or even just ``":"`` are possible as well.

    Specifying the numeric ``ID`` of a source is also supported.


extractor.[mastodon].access-token
---------------------------------
Type
    ``string``
Default
    ``null``
Description
    The ``access-token`` value you get from `linking your account to
    gallery-dl <OAuth_>`__.
Note
    gallery-dl comes with built-in tokens for
    ``mastodon.social``, ``pawoo``, and ``baraag``.


extractor.[mastodon].cards
--------------------------
Type
    ``bool``
Default
    ``false``
Description
    Fetch media from cards.


extractor.[mastodon].reblogs
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Fetch media from reblogged posts.


extractor.[mastodon].replies
----------------------------
Type
    ``bool``
Default
    ``true``
Description
    Fetch media from replies to other posts.


extractor.[mastodon].text-posts
-------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Also emit metadata for text-only posts without media content.


extractor.[misskey].access-token
--------------------------------
Type
    ``string``
Description
    Your access token, necessary to fetch favorited notes.


extractor.[misskey].include
---------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"notes"``
Example
    * ``"avatar,background,notes"``
    * ``["avatar", "background", "notes"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``info``
    * ``avatar``
    * ``background``
    * ``notes``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.[misskey].renotes
---------------------------
Type
    ``bool``
Default
    ``false``
Description
    Fetch media from renoted notes.


extractor.[misskey].replies
---------------------------
Type
    ``bool``
Default
    ``true``
Description
    Fetch media from replies to other notes.


extractor.[moebooru].pool.metadata
----------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract extended ``pool`` metadata.
Note
    Not supported by all ``moebooru`` instances.


extractor.naver-blog.videos
---------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download videos.


extractor.naver-chzzk.offset
----------------------------
Type
    ``integer``
Default
    ``0``
Description
    Custom ``offset`` starting value when paginating over comments.


extractor.newgrounds.flash
--------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download original Adobe Flash animations instead of pre-rendered videos.


extractor.newgrounds.format
---------------------------
Type
    * ``string``
    * ``list`` of ``string``
Default
    ``"original"``
Example
    * ``"720p"``
    * ``["mp4", "mov", "1080p", "720p"]``
Description
    Selects the preferred format for video downloads.

    If the selected format is not available,
    the next smaller one gets chosen.

    If this is a ``list``, try each given
    filename extension in original resolution or recoded format
    until an available format is found.


extractor.newgrounds.include
----------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"art"``
Example
    * ``"movies,audio"``
    * ``["movies", "audio"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``art``
    * ``audio``
    * ``games``
    * ``movies``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.nijie.include
-----------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"illustration,doujin"``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``illustration``
    * ``doujin``
    * ``favorite``
    * ``nuita``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.nitter.quoted
-----------------------
Type
    ``bool``
Default
    ``false``
Description
    Fetch media from quoted Tweets.


extractor.nitter.retweets
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Fetch media from Retweets.


extractor.nitter.videos
-----------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Control video download behavior.

    ``true``
        Download videos
    ``"ytdl"``
        Download videos using |ytdl|
    ``false``
        Skip video Tweets


extractor.oauth.browser
-----------------------
Type
    ``bool``
Default
    ``true``
Description
    Controls how a user is directed to an OAuth authorization page.

    ``true``
        Use Python's |webbrowser.open()|_ method to automatically
        open the URL in the user's default browser.
    ``false``
        Ask the user to copy & paste an URL from the terminal.


extractor.oauth.cache
---------------------
Type
    ``bool``
Default
    ``true``
Description
    Store tokens received during OAuth authorizations
    in `cache <cache.file_>`__.


extractor.oauth.host
--------------------
Type
    ``string``
Default
    ``"localhost"``
Description
    Host name / IP address to bind to during OAuth authorization.


extractor.oauth.port
--------------------
Type
    ``integer``
Default
    ``6414``
Description
    Port number to listen on during OAuth authorization.
Note
    All redirects will go to port ``6414``, regardless
    of the port specified here. You'll have to manually adjust the
    port number in your browser's address bar when using a different
    port than the default.


extractor.paheal.metadata
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract additional metadata (``source``, ``uploader``)
Note
    This requires 1 additional HTTP request per post.


extractor.patreon.cursor
------------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Example
    ``"03:eyJ2IjoxLCJjIjoiMzU0NDQ1MjAiLCJ0IjoiIn0=:DTcmjBoVj01o_492YBYqHhqx"``
Description
    Controls from which position to start the extraction process from.

    ``true``
        | Start from the beginning.
        | Log the most recent ``cursor`` value when interrupted before reaching the end.
    ``false``
        Start from the beginning.
    any ``string``
        Start from the position defined by this value.


extractor.patreon.files
-----------------------
Type
    ``list`` of ``strings``
Default
    ``["images", "image_large", "attachments", "postfile", "content"]``
Description
    Determines types and order of files to download.
Available Types
    * ``postfile``
    * ``images``
    * ``image_large``
    * ``attachments``
    * ``content``


extractor.patreon.format-images
-------------------------------
Type
    ``string``
Default
    ``"download_url"``
Description
    Selects the format of ``images`` `files <extractor.patreon.files_>`__.
Available Formats
    * ``download_url`` (``"a":1,"p":1``)
    * ``url`` (``"w":620``)
    * ``original`` (``"q":100,"webp":0``)
    * ``default`` (``"w":620``)
    * ``default_small`` (``"w":360``)
    * ``default_blurred`` (``"w":620``)
    * ``default_blurred_small`` (``"w":360``)
    * ``thumbnail`` (``"h":360,"w":360``)
    * ``thumbnail_large`` (``"h":1080,"w":1080``)
    * ``thumbnail_small`` (``"h":100,"w":100``)


extractor.patreon.user.date-max
-------------------------------
Type
    |Date|_
Default
    ``0``
Description
    Sets the |Date|_ to start from.


extractor.[philomena].api-key
-----------------------------
Type
    ``string``
Default
    ``null``
Description
    Your account's API Key,
    to use your personal browsing settings and filters.


extractor.[philomena].filter
----------------------------
Type
    ``integer``
Default
    :``derpibooru``:
        ``56027`` (`Everything <https://derpibooru.org/filters/56027>`__ filter)
    :``ponybooru``:
        ``3`` (`Nah. <https://ponybooru.org/filters/3>`__ filter)
    :otherwise:
        ``2``

Description
    The content filter ID to use.

    Setting an explicit filter ID overrides any default filters and can be used
    to access 18+ content without `API Key <extractor.[philomena].api-key_>`_.

    See `Filters <https://derpibooru.org/filters>`_ for details.


extractor.[philomena].svg
-------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download SVG versions of images when available.

    Try to download the ``view_url`` version of these posts
    when this option is disabled.


extractor.pillowfort.external
-----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Follow links to external sites, e.g. Twitter,


extractor.pillowfort.inline
---------------------------
Type
    ``bool``
Default
    ``true``
Description
    Extract inline images.


extractor.pillowfort.reblogs
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract media from reblogged posts.


extractor.pinterest.domain
--------------------------
Type
    ``string``
Default
    ``"auto"``
Description
    Specifies the domain used by ``pinterest`` extractors.

    Setting this option to ``"auto"``
    uses the same domain as a given input URL.


extractor.pinterest.sections
----------------------------
Type
    ``bool``
Default
    ``true``
Description
    Include pins from board sections.


extractor.pinterest.stories
---------------------------
Type
    ``bool``
Default
    ``true``
Description
    Extract files from story pins.


extractor.pinterest.videos
--------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download from video pins.


extractor.pixeldrain.api-key
----------------------------
Type
    ``string``
Description
    Your account's `API key <https://pixeldrain.com/user/api_keys>`__


extractor.pixeldrain.recursive
------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Recursively download files from subfolders.


extractor.pixiv.include
-----------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"artworks"``
Example
    * ``"avatar,background,artworks"``
    * ``["avatar", "background", "artworks"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``artworks``
    * ``avatar``
    * ``background``
    * ``favorite``
    * ``novel-user``
    * ``novel-bookmark``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.pixiv.refresh-token
-----------------------------
Type
    ``string``
Description
    The ``refresh-token`` value you get
    from running ``gallery-dl oauth:pixiv`` (see OAuth_) or
    by using a third-party tool like
    `gppt <https://github.com/eggplants/get-pixivpy-token>`__.


extractor.pixiv.metadata
------------------------
Type
    ``bool``
Default
    ``false``
Description
    Fetch extended ``user`` metadata.


extractor.pixiv.metadata-bookmark
---------------------------------
Type
    ``bool``
Default
    ``false``
Description
    For works bookmarked by
    `your own account <extractor.pixiv.refresh-token_>`__,
    fetch bookmark tags as ``tags_bookmark`` metadata.
Note
    This requires 1 additional API request per bookmarked post.


extractor.pixiv.captions
------------------------
Type
    ``bool``
Default
    ``false``
Description
    For works with seemingly empty ``caption`` metadata,
    try to grab the actual ``caption`` value using the AJAX API.


extractor.pixiv.comments
------------------------
Type
    ``bool``
Default
    ``false``
Description
    Fetch ``comments`` metadata.
Note
    This requires 1 or more additional API requests per post,
    depending on the number of comments.


extractor.pixiv.work.related
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Also download related artworks.


extractor.pixiv.tags
--------------------
Type
    ``string``
Default
    ``"japanese"``
Description
    Controls the ``tags`` metadata field.

    * `"japanese"`: List of Japanese tags
    * `"translated"`: List of translated tags
    * `"original"`: Unmodified list with both Japanese and translated tags


extractor.pixiv.ugoira
----------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Download Pixiv's Ugoira animations.

    These animations come as a ``.zip`` archive containing all
    animation frames in JPEG format by default.

    Set this option to ``"original"``
    to download them as individual, higher-quality frames.

    Use an `ugoira` post processor to convert them
    to watchable animations. (Example__)

.. __: https://github.com/mikf/gallery-dl/blob/v1.12.3/docs/gallery-dl-example.conf#L9-L14


extractor.pixiv.max-posts
-------------------------
Type
    ``integer``
Default
    ``0``
Description
    When downloading galleries, this sets the maximum number of posts to get.
    A value of ``0`` means no limit.


extractor.pixiv.sanity
----------------------
Type
    ``bool``
Default
    ``true``
Description
    Try to fetch ``limit_sanity_level`` works via web API.


extractor.pixiv-novel.comments
------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Fetch ``comments`` metadata.
Note
    This requires 1 or more additional API requests per novel,
    depending on the number of comments.


extractor.pixiv-novel.covers
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download cover images.


extractor.pixiv-novel.embeds
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download embedded images.


extractor.pixiv-novel.full-series
---------------------------------
Type
    ``bool``
Default
    ``false``
Description
    When downloading a novel being part of a series,
    download all novels of that series.


extractor.pixiv-novel.max-posts
-------------------------------
Type
    ``integer``
Default
    ``0``
Description
    When downloading multiple novels,
    this sets the maximum number of novels to get.

    A value of ``0`` means no limit.


extractor.pixiv-novel.metadata
------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Fetch extended ``user`` metadata.


extractor.pixiv-novel.metadata-bookmark
---------------------------------------
Type
    ``bool``
Default
    ``false``
Description
    For novels bookmarked by
    `your own account <extractor.pixiv-novel.refresh-token_>`__,
    fetch bookmark tags as ``tags_bookmark`` metadata.
Note
    This requires 1 additional API request per bookmarked post.


extractor.pixiv-novel.refresh-token
-----------------------------------
Type
    ``string``
Description
    The ``refresh-token`` value you get
    from running ``gallery-dl oauth:pixiv`` (see OAuth_) or
    by using a third-party tool like
    `gppt <https://github.com/eggplants/get-pixivpy-token>`__.

    This can be the same value as `extractor.pixiv.refresh-token`_


extractor.pixiv-novel.tags
--------------------------
Type
    ``string``
Default
    ``"japanese"``
Description
    Controls the ``tags`` metadata field.

    * `"japanese"`: List of Japanese tags
    * `"translated"`: List of translated tags
    * `"original"`: Unmodified list with both Japanese and translated tags


extractor.plurk.comments
------------------------
Type
    ``bool``
Default
    ``false``
Description
    Also search Plurk comments for URLs.


extractor.[postmill].save-link-post-body
----------------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Whether or not to save the body for link/image posts.


extractor.reactor.gif
---------------------
Type
    ``bool``
Default
    ``false``
Description
    Format in which to download animated images.

    Use ``true`` to download animated images as gifs and ``false``
    to download as mp4 videos.


extractor.readcomiconline.captcha
---------------------------------
Type
    ``string``
Default
    ``"stop"``
Description
    Controls how to handle redirects to CAPTCHA pages.

    ``"stop``
        Stop the current extractor run.
    ``"wait``
        Ask the user to solve the CAPTCHA and wait.


extractor.readcomiconline.quality
---------------------------------
Type
    ``string``
Default
    ``"auto"``
Description
    Sets the ``quality`` query parameter of issue pages. (``"lq"`` or ``"hq"``)

    ``"auto"`` uses the quality parameter of the input URL
    or ``"hq"`` if not present.


extractor.reddit.api
--------------------
Type
    ``string``
Default
    ``"oauth"``
Description
    Selects which API endpoints to use.

    ``"oauth"``
        Use the OAuth API at ``https://oauth.reddit.com``

        Requires
        `client-id & user-agent <extractor.reddit.client-id & .user-agent_>`__
        and uses a
        `refresh token <extractor.reddit.refresh-token_>`__
        for authentication.

    ``"rest"``
        Use the REST API at ``https://www.reddit.com``

        Uses
        `cookies <extractor.*.cookies_>`__
        for authentication.


extractor.reddit.comments
-------------------------
Type
    ``integer``
Default
    ``0``
Description
    The value of the ``limit`` parameter when loading
    a submission and its comments.
    This number (roughly) specifies the total amount of comments
    being retrieved with the first API call.

    Reddit's internal default and maximum values for this parameter
    appear to be 200 and 500 respectively.

    The value ``0`` ignores all comments and significantly reduces the
    time required when scanning a subreddit.


extractor.reddit.morecomments
-----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Retrieve additional comments by resolving the ``more`` comment
    stubs in the base comment tree.
Note
    This requires 1 additional API call for every 100 extra comments.


extractor.reddit.embeds
-----------------------
Type
    ``bool``
Default
    ``true``
Description
    Download embedded comments media.


extractor.reddit.date-min & .date-max
-------------------------------------
Type
    |Date|_
Default
    ``0`` and ``253402210800`` (timestamp of |datetime.max|_)
Description
    Ignore all submissions posted before/after this date.


extractor.reddit.id-min & .id-max
---------------------------------
Type
    ``string``
Example
    ``"6kmzv2"``
Description
    Ignore all submissions posted before/after the submission with this ID.


extractor.reddit.limit
----------------------
Type
    ``integer``
Default
    ``null``
Description
    Number of results to return in a single API query.

    This value specifies the ``limit`` parameter
    used for API requests when retrieving paginated results.

    ``null`` means not including this parameter at all
    and letting Reddit chose a default.


extractor.reddit.previews
-------------------------
Type
    ``bool``
Default
    ``true``
Description
    For failed downloads from external URLs / child extractors,
    download Reddit's preview image/video if available.


extractor.reddit.recursion
--------------------------
Type
    ``integer``
Default
    ``0``
Description
    Reddit extractors can recursively visit other submissions
    linked to in the initial set of submissions.
    This value sets the maximum recursion depth.
Special Values
    ``0``
        Recursion is disabled
    ``-1``
        Infinite recursion (don't do this)


extractor.reddit.refresh-token
------------------------------
Type
    ``string``
Default
    ``null``
Description
    The ``refresh-token`` value you get from
    `linking your Reddit account to gallery-dl <OAuth_>`__.

    Using a ``refresh-token`` allows you to access private or otherwise
    not publicly available subreddits, given that your account is
    authorized to do so,
    but requests to the reddit API are going to be rate limited
    at 600 requests every 10 minutes/600 seconds.


extractor.reddit.selftext
-------------------------
Type
    ``bool``
Default
    * ``true`` if `comments <extractor.reddit.comments_>`__ are enabled
    * ``false`` otherwise
Description
    Follow links in the original post's ``selftext``.


extractor.reddit.videos
-----------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Control video download behavior.

    ``true``
        Download videos and use |ytdl| to handle
        HLS and DASH manifests
    ``"ytdl"``
        Download videos and let |ytdl| handle all of
        video extraction and download
    ``"dash"``
        Extract DASH manifest URLs and use |ytdl|
        to download and merge them. (*)
    ``false``
        Ignore videos
Note
    (*)
    This saves 1 HTTP request per video
    and might potentially be able to download otherwise deleted videos,
    but it will not always get the best video quality available.


extractor.redgifs.format
------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``["hd", "sd", "gif"]``
Description
    List of names of the preferred animation format.`

    If a selected format is not available, the next one in the list will be
    tried until an available format is found.

    If the format is given as ``string``, it will be extended with
    ``["hd", "sd", "gif"]``. Use a list with one element to
    restrict it to only one possible format.
Available Formats
    * ``"hd"``
    * ``"sd"``
    * ``"gif"``
    * ``"thumbnail"``
    * ``"vthumbnail"``
    * ``"poster"``


extractor.rule34.api-key & .user-id
-----------------------------------
Type
    ``string``
Default
    ``null``
Description
    Values from the `API Access Credentials` section
    found near the bottom of your account's
    `Options <https://rule34.xxx/index.php?page=account&s=options>`__
    page.

    Enable `Generate New Key?` and click `Save`
    if the value after ``&api_key=`` is empty,
    e.g. ``&api_key=&user_id=12345``


extractor.rule34xyz.format
--------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``["10", "40", "41", "2"]``
Example
    ``"33,34,4"``
Description
    Selects the file format to extract.

    When more than one format is given, the first available one is selected.


extractor.sankaku.refresh
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Refresh download URLs before they expire.


extractor.sankaku.tags
----------------------
Type
    * ``bool``
    * ``string``
Default
    ``false``
Description
    | Group ``tags`` by type and
      provide them as ``tags_<type>`` and ``tag_string_TYPE`` metadata fields,
    | for example ``tags_artist`` and ``tags_character``.

    ``true``
        Enable general ``tags`` categories

        Requires:

        * 1 additional API request per 100 tags per post

    ``"extended"``
        Group ``tags`` by the new, extended tag category system
        used on ``chan.sankakucomplex.com``

        Requires:

        * 1 additional HTTP request per post
        * authenticated `cookies <extractor.*.cookies_>`__
          to fetch full ``tags`` category data

    ``false``
        Disable ``tags`` categories


extractor.sankakucomplex.embeds
-------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download video embeds from external sites.


extractor.sankakucomplex.videos
-------------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download videos.


extractor.schalenetwork.cbz
---------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download each gallery as a single ``.cbz`` file.
Note
    Requires a
    `token <extractor.schalenetwork.token_>`__


extractor.schalenetwork.crt
---------------------------
Type
    ``string``
Example
    * ``"0542daa9-352c-4fd5-a497-6c6d5cf07423"``
    * ``"/12345/a1b2c3d4e5f6?crt=0542daa9-352c-4fd5-a497-6c6d5cf07423"``
Description
    The ``crt`` query parameter value
    sent when fetching gallery data.

    To get this value:

    * Open your browser's Developer Tools (F12)
    * Select `Network` → `XHR`
    * Open a gallery page
    * Select the last `Network` entry and copy its ``crt`` value
Note
    You will also need your browser's
    `user-agent <extractor.*.user-agent_>`__


extractor.schalenetwork.format
------------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``["0", "1600", "1280", "980", "780"]``
Description
    Name(s) of the image format to download.

    When more than one format is given, the first available one is selected.
Formats
    * ``"780"``
    * ``"980"``
    * ``"1280"``
    * ``"1600"``
    * ``"0"`` (original)


extractor.schalenetwork.tags
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Group ``tags`` by type and
    provide them as ``tags_<type>`` metadata fields,
    for example ``tags_artist`` or ``tags_character``.


extractor.schalenetwork.token
-----------------------------
Type
    ``string``
Example
    * ``"3f1a9b72-4e4d-4f4e-9e5d-4a2b99f7c893"``
    * ``"Bearer 3f1a9b72-4e4d-4f4e-9e5d-4a2b99f7c893"``
    * ``"Authorization: Bearer 3f1a9b72-4e4d-4f4e-9e5d-4a2b99f7c893"``
Description
    ``Authorization`` header value
    used for requests to ``https://api.schale.network``
    to access ``favorite`` galleries
    or download
    `.cbz <extractor.schalenetwork.cbz_>`__
    archives.


extractor.sexcom.gifs
---------------------
Type
    ``bool``
Default
    ``true``
Description
    Download animated images as ``.gif`` instead of ``.webp``


extractor.simpcity.order-posts
------------------------------
Type
    ``string``
Default
    ``"desc"``
Description
    Controls the order in which
    posts of a ``thread`` are processed.

    ``"asc"``
        Ascending order (oldest first)
    ``"desc"`` | ``"reverse"``
        Descending order (newest first)


extractor.sizebooru.metadata
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract additional metadata:

    * ``approver``
    * ``artist``
    * ``date``
    * ``date_approved``
    * ``favorite``
    * ``source``
    * ``tags``
    * ``uploader``
    * ``views``
Note
    This requires 1 additional HTTP request per post.


extractor.skeb.article
----------------------
Type
    ``bool``
Default
    ``false``
Description
    Download article images.


extractor.skeb.include
----------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    * ``["works", "sentrequests"]``
      if `sent-requests <extractor.skeb.sent-requests_>`__ are enabled
    * ``["works"]`` otherwise
Example
    * ``"works,sentrequests"``
    * ``["works", "sentrequests"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``works``
    * ``sentrequests``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.skeb.sent-requests
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download sent requests.


extractor.skeb.thumbnails
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download thumbnails.


extractor.skeb.search.filters
-----------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``["genre:art", "genre:voice", "genre:novel", "genre:video", "genre:music", "genre:correction"]``
Example
    ``"genre:music OR genre:voice"``
Description
    Filters used during searches.


extractor.smugmug.videos
------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download video files.


extractor.steamgriddb.animated
------------------------------
Type
    ``bool``
Default
    ``true``
Description
    Include ``animated`` assets
    when downloading from a list of assets.


extractor.steamgriddb.epilepsy
------------------------------
Type
    ``bool``
Default
    ``true``
Description
    Include assets tagged with ``epilepsy``
    when downloading from a list of assets.


extractor.steamgriddb.dimensions
--------------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"all"``
Example
    * ``"1024x512,512x512"``
    * ``["460x215", "920x430"]``
Description
    Only include assets that are in the specified dimensions. ``all`` can be
    used to specify all dimensions.
Valid Values
    Grids
        ``460x215`` |
        ``920x430`` |
        ``342x482`` |
        ``600x900`` |
        ``660x930`` |
        ``512x512`` |
        ``1024x1024``
    Heroes
        ``1600x650`` |
        ``1920x620`` |
        ``3840x1240``
    Logos
        N/A (will be ignored)
    Icons
        ``8x8`` | ``10x10`` | ``14x14`` | ``16x16`` | ``20x20`` | ``24x24`` |
        ``28x28`` | ``32x32`` | ``35x35`` | ``40x40`` | ``48x48`` | ``54x54`` |
        ``56x56`` | ``57x57`` | ``60x60`` | ``64x64`` | ``72x72`` | ``76x76`` |
        ``80x80`` | ``90x90`` | ``96x96`` | ``100x100`` | ``114x114`` | ``120x120`` |
        ``128x128`` | ``144x144`` | ``150x150`` | ``152x152`` | ``160x160`` |
        ``180x180`` | ``192x192`` | ``194x194`` | ``256x256`` | ``310x310`` |
        ``512x512`` | ``768x768`` | ``1024x1024``


extractor.steamgriddb.file-types
--------------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"all"``
Example
    * ``"png,jpeg"``
    * ``["jpeg", "webp"]``
Description
    Only include assets that are in the specified file types. ``all`` can be
    used to specify all file types.
Valid Values
    Grids
        ``png`` | ``jpeg`` | ``jpg`` | ``webp``
    Heroes
        ``png`` | ``jpeg`` | ``jpg`` | ``webp``
    Logos
        ``png`` | ``webp``
    Icons
        ``png`` | ``ico``


extractor.steamgriddb.download-fake-png
---------------------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download fake PNGs alongside the real file.


extractor.steamgriddb.humor
---------------------------
Type
    ``bool``
Default
    ``true``
Description
    Include assets tagged with ``humor``
    when downloading from a list of assets.


extractor.steamgriddb.languages
-------------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"all"``
Example
    * ``"en,km"``
    * ``["fr", "it"]``
Description
    Only include assets that are in the specified languages.
Valid Values
    |ISO 639-1| codes
Note
    ``all`` can be used to specify all languages.


extractor.steamgriddb.nsfw
--------------------------
Type
    ``bool``
Default
    ``true``
Description
    Include assets tagged with adult content when downloading from a list of assets.


extractor.steamgriddb.sort
--------------------------
Type
    ``string``
Default
    ``"score_desc"``
Description
    Set the chosen sorting method when downloading from a list of assets.
Supported Values
    * ``score_desc``     (Highest Score (Beta))
    * ``score_asc``      (Lowest Score (Beta))
    * ``score_old_desc`` (Highest Score (Old))
    * ``score_old_asc``  (Lowest Score (Old))
    * ``age_desc``       (Newest First)
    * ``age_asc``        (Oldest First)


extractor.steamgriddb.static
----------------------------
Type
    ``bool``
Default
    ``true``
Description
    Include static assets when downloading from a list of assets.


extractor.steamgriddb.styles
----------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"all"``
Example
    * ``"white,black"``
    * ``["no_logo", "white_logo"]``
Description
    Only include assets that are in the specified styles.
Valid Values
    Grids
        ``alternate`` | ``blurred`` | ``no_logo`` | ``material`` | ``white_logo``
    Heroes
        ``alternate`` | ``blurred`` | ``material``
    Logos
        ``official`` | ``white`` | ``black`` | ``custom``
    Icons
        ``official`` | ``custom``
Note
    ``"all"`` can be used to specify all styles.

extractor.steamgriddb.untagged
------------------------------
Type
    ``bool``
Default
    ``true``
Description
    Include untagged assets when downloading from a list of assets.


extractor.[szurubooru].username & .token
----------------------------------------
Type
    ``string``
Description
    Username and login token of your account to access private resources.

    To generate a token, visit ``/user/USERNAME/list-tokens``
    and click ``Create Token``.


extractor.tenor.format
----------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``["gif", "mp4", "webm", "webp"]``
Description
    List of names of the preferred animation format.

    If a selected format is not available, the next one in the list will be
    tried until a format is found.
Available Formats
    * ``gif``
    * ``gif_transparent``
    * ``mediumgif``
    * ``gifpreview``
    * ``tinygif``
    * ``tinygif_transparent``
    * ``mp4``
    * ``tinymp4``
    * ``webm``
    * ``webp``
    * ``webp_transparent``
    * ``tinywebp``
    * ``tinywebp_transparent``


extractor.tiktok.audio
----------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Controls audio download behavior.

    ``true``
        Download audio tracks
    ``"ytdl"``
        Download audio tracks using |ytdl|
    ``false``
        Ignore audio tracks


extractor.tiktok.videos
-----------------------
Type
    ``bool``
Default
    ``true``
Description
    Download videos using |ytdl|.


extractor.tiktok.user.avatar
----------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download user avatars.


extractor.tiktok.user.module
----------------------------
Type
    |Module|_
Default
    ``null``
Description
    The |ytdl| |Module|_
    to extract posts from a ``tiktok`` user profile with.

    See `extractor.ytdl.module`_.


extractor.tiktok.user.tiktok-range
----------------------------------
Type
    ``string``
Default
    ``""``
Example
    ``"1-20"``
Description
    Range or playlist indices of ``tiktok`` user posts to extract.

    See
    `ytdl/playlist_items <https://github.com/yt-dlp/yt-dlp/blob/3042afb5fe342d3a00de76704cd7de611acc350e/yt_dlp/YoutubeDL.py#L289>`__
    for details.


extractor.tumblr.avatar
-----------------------
Type
    ``bool``
Default
    ``false``
Description
    Download blog avatars.


extractor.tumblr.date-min & .date-max
-------------------------------------
Type
    |Date|_
Default
    ``0`` and ``null``
Description
    Ignore all posts published before/after this date.


extractor.tumblr.external
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Follow external URLs (e.g. from "Link" posts) and try to extract
    images from them.


extractor.tumblr.inline
-----------------------
Type
    ``bool``
Default
    ``true``
Description
    Search posts for inline images and videos.


extractor.tumblr.offset
-----------------------
Type
    ``integer``
Default
    ``0``
Description
    Custom ``offset`` starting value when paginating over blog posts.

    Allows skipping over posts without having to waste API calls.


extractor.tumblr.original
-------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download full-resolution ``photo`` and ``inline`` images.

    For each photo with "maximum" resolution
    (width equal to 2048 or height equal to 3072)
    or each inline image,
    use an extra HTTP request to find the URL to its full-resolution version.


extractor.tumblr.pagination
---------------------------
Type
    ``string``
Default
    * ``"before"`` if `date-max <extractor.tumblr.date-min & .date-max_>`__ is set
    * ``"offset"`` otherwise
Description
    Controls how to paginate over blog posts.

    ``"api"``
        ``next`` parameter provided by the API
        (potentially misses posts due to a
        `bug <https://github.com/tumblr/docs/issues/76>`__
        in Tumblr's API)
    ``"before"``
        Timestamp of last post
    ``"offset"``
        Post offset number


extractor.tumblr.ratelimit
--------------------------
Type
    ``string``
Default
    ``"abort"``
Description
    Selects how to handle exceeding the daily API rate limit.

    ``"abort"``
        Raise an error and stop extraction
    ``"wait"``
        Wait until rate limit reset


extractor.tumblr.reblogs
------------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    ``true``
        Extract media from reblogged posts
    ``false``
        Skip reblogged posts
    ``"same-blog"``
        Skip reblogged posts unless the original post
        is from the same blog


extractor.tumblr.posts
----------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"all"``
Example
    * ``"video,audio,link"``
    * ``["video", "audio", "link"]``
Description
    A (comma-separated) list of post types to extract images, etc. from.

    Possible types are ``text``, ``quote``, ``link``, ``answer``,
    ``video``, ``audio``, ``photo``, ``chat``.

    It is possible to use ``"all"`` instead of listing all types separately.


extractor.tumblr.fallback-delay
-------------------------------
Type
    ``float``
Default
    ``120.0``
Description
    Number of seconds to wait between retries
    for fetching full-resolution images.


extractor.tumblr.fallback-retries
---------------------------------
Type
    ``integer``
Default
    ``2``
Description
    Number of retries for fetching full-resolution images
    or ``-1`` for infinite retries.


extractor.twibooru.api-key
--------------------------
Type
    ``string``
Default
    ``null``
Description
    Your `Twibooru API Key <https://twibooru.org/users/edit>`__,
    to use your account's browsing settings and filters.


extractor.twibooru.filter
-------------------------
Type
    ``integer``
Default
    ``2`` (`Everything <https://twibooru.org/filters/2>`__ filter)
Description
    The content filter ID to use.

    Setting an explicit filter ID overrides any default filters and can be used
    to access 18+ content without `API Key <extractor.twibooru.api-key_>`__.

    See `Filters <https://twibooru.org/filters>`__ for details.


extractor.twibooru.svg
----------------------
Type
    ``bool``
Default
    ``true``
Description
    Download SVG versions of images when available.

    Try to download the ``view_url`` version of these posts
    when this option is disabled.


extractor.twitter.ads
---------------------
Type
    ``bool``
Default
    ``false``
Description
    Fetch media from promoted Tweets.


extractor.twitter.cards
-----------------------
Type
    * ``bool``
    * ``string``
Default
    ``false``
Description
    Controls how to handle `Twitter Cards <https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/abouts-cards>`__.

    ``false``
        Ignore cards
    ``true``
        Download image content from supported cards
    ``"ytdl"``
        Additionally download video content from unsupported cards using |ytdl|


extractor.twitter.cards-blacklist
---------------------------------
Type
    ``list`` of ``strings``
Example
    ``["summary", "youtube.com", "player:twitch.tv"]``
Description
    List of card types to ignore.

    Possible values are

    * card names
    * card domains
    * ``<card name>:<card domain>``


extractor.twitter.conversations
-------------------------------
Type
    * ``bool``
    * ``string``
Default
    ``false``
Description
    For input URLs pointing to a single Tweet,
    e.g. `https://twitter.com/i/web/status/<TweetID>`,
    fetch media from all Tweets and replies in this `conversation
    <https://help.twitter.com/en/using-twitter/twitter-conversations>`__.

    If this option is equal to ``"accessible"``,
    only download from conversation Tweets
    if the given initial Tweet is accessible.


extractor.twitter.csrf
----------------------
Type
    ``string``
Default
    ``"cookies"``
Description
    Controls how to handle Cross Site Request Forgery (CSRF) tokens.

    ``"auto"``
        Always auto-generate a token.
    ``"cookies"``
        Use token given by the ``ct0`` cookie if present.


extractor.twitter.cursor
------------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Example
    ``"1/DAABCgABGVKi5lE___oKAAIYbfYNcxrQLggAAwAAAAIAAA"``
Description
    Controls from which position to start the extraction process from.

    ``true``
        | Start from the beginning.
        | Log the most recent ``cursor`` value when interrupted before reaching the end.
    ``false``
        Start from the beginning.
    any ``string``
        Start from the position defined by this value.
Note
    A ``cursor`` value from one timeline cannot be used with another.


extractor.twitter.expand
------------------------
Type
    ``bool``
Default
    ``false``
Description
    For each Tweet, return *all* Tweets from that initial Tweet's
    conversation or thread, i.e. *expand* all Twitter threads.

    Going through a timeline with this option enabled is essentially the same
    as running ``gallery-dl https://twitter.com/i/web/status/<TweetID>``
    with enabled `conversations <extractor.twitter.conversations_>`__ option
    for each Tweet in said timeline.
Note
    This requires at least 1 additional API call per initial Tweet.


extractor.twitter.unavailable
-----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Try to download media marked as ``Unavailable``,
    e.g. ``Geoblocked`` videos.


extractor.twitter.include
-------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"timeline"``
Example
    * ``"avatar,background,media"``
    * ``["avatar", "background", "media"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``info``
    * ``avatar``
    * ``background``
    * ``timeline``
    * ``tweets``
    * ``media``
    * ``replies``
    * ``highlights``
    * ``likes``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.twitter.transform
---------------------------
Type
    ``bool``
Default
    ``true``
Description
    Transform Tweet and User metadata into a simpler, uniform format.


extractor.twitter.tweet-endpoint
--------------------------------
Type
    ``string``
Default
    ``"auto"``
Description
    Selects the API endpoint used to retrieve single Tweets.

    ``"restid"``
        ``/TweetResultByRestId`` - accessible to guest users
    ``"detail"``
        ``/TweetDetail`` - more stable
    ``"auto"``
        ``"detail"`` when logged in, ``"restid"`` otherwise


extractor.twitter.size
----------------------
Type
    ``list`` of ``strings``
Default
    ``["orig", "4096x4096", "large", "medium", "small"]``
Description
    The image version to download.
    Any entries after the first one will be used for potential
    `fallback <extractor.*.fallback_>`_ URLs.

    Known available sizes are

    * ``orig``
    * ``large``
    * ``medium``
    * ``small``
    * ``4096x4096``
    * ``900x900``
    * ``360x360``


extractor.twitter.logout
------------------------
Type
    ``bool``
Default
    ``false``
Description
    Logout and retry as guest when access to another user's Tweets is blocked.


extractor.twitter.pinned
------------------------
Type
    ``bool``
Default
    ``false``
Description
    Fetch media from pinned Tweets.


extractor.twitter.quoted
------------------------
Type
    ``bool``
Default
    ``false``
Description
    Fetch media from quoted Tweets.

    If this option is enabled, gallery-dl will try to fetch
    a quoted (original) Tweet when it sees the Tweet which quotes it.


extractor.twitter.ratelimit
---------------------------
Type
    ``string``
Default
    ``"wait"``
Description
    Selects how to handle exceeding the API rate limit.

    ``"abort"``
        Raise an error and stop extraction
    ``"wait"``
        Wait until rate limit reset
    ``"wait:N"``
        Wait for ``N`` seconds


extractor.twitter.locked
------------------------
Type
    ``string``
Default
    ``"abort"``
Description
    Selects how to handle "account is temporarily locked" errors.

    ``"abort"``
        Raise an error and stop extraction
    ``"wait"``
        Wait until the account is unlocked and retry


extractor.twitter.replies
-------------------------
Type
    ``bool``
Default
    ``true``
Description
    Fetch media from replies to other Tweets.

    If this value is ``"self"``, only consider replies where
    reply and original Tweet are from the same user.
Note
    Twitter will automatically expand conversations if you
    use the ``/with_replies`` timeline while logged in. For example,
    media from Tweets which the user replied to will also be downloaded.

    It is possible to exclude unwanted Tweets using `image-filter
    <extractor.*.image-filter_>`__.


extractor.twitter.retweets
--------------------------
Type
    ``bool``
Default
    ``false``
Description
    Fetch media from Retweets.

    If this value is ``"original"``, metadata for these files
    will be taken from the original Tweets, not the Retweets.


extractor.twitter.search-limit
------------------------------
Type
    ``integer``
Default
    ``20``
Description
    Number of requested results per search query.


extractor.twitter.search-pagination
-----------------------------------
Type
    ``string``
Default
    ``"cursor"``
Description
    Selects how to paginate over search results.

    ``"cursor"``
        Use ``cursor`` values provided by the API
    ``"max_id"`` | ``"maxid"`` | ``"id"``
        Update the ``max_id`` search query parameter
        to the Tweet ID value of the last retrieved Tweet.


extractor.twitter.search-stop
-----------------------------
Type
    ``integer``
Default
    * ``3`` if `search-pagination <extractor.twitter.search-pagination_>`__ is set to ``"cursor"``
    * ``0`` otherwise
Description
    Number of empty search result batches
    to accept before stopping.


extractor.twitter.timeline.strategy
-----------------------------------
Type
    ``string``
Default
    ``"auto"``
Description
    Controls the strategy / tweet source used for timeline URLs
    (``https://twitter.com/USER/timeline``).

    ``"tweets"``
        `/tweets <https://twitter.com/USER/tweets>`__ timeline + search
    ``"media"``
        `/media <https://twitter.com/USER/media>`__ timeline + search
    ``"with_replies"``
        `/with_replies <https://twitter.com/USER/with_replies>`__ timeline + search
    ``"auto"``
        ``"tweets"`` or ``"media"``, depending on `retweets <extractor.twitter.retweets_>`__ and `text-tweets <extractor.twitter.text-tweets_>`__ settings


extractor.twitter.text-tweets
-----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Also emit metadata for text-only Tweets without media content.

    This only has an effect with a ``metadata`` (or ``exec``) post processor
    with `"event": "post" <metadata.event_>`_
    and appropriate `filename <metadata.filename_>`_.


extractor.twitter.twitpic
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract `TwitPic <https://twitpic.com/>`__ embeds.


extractor.twitter.unique
------------------------
Type
    ``bool``
Default
    ``true``
Description
    Ignore previously seen Tweets.


extractor.twitter.username-alt
------------------------------
Type
    ``string``
Description
    Alternate Identifier (username, email, phone number)
    when `logging in <extractor.*.username & .password_>`__.

    When not specified and asked for by Twitter,
    this identifier will need to be entered in an interactive prompt.


extractor.twitter.users
-----------------------
Type
    ``string``
Default
    ``"user"``
Example
    ``"https://twitter.com/search?q=from:{legacy[screen_name]}"``
Description
    | Basic format string for user URLs generated from
      ``following`` and ``list-members`` queries,
    | whose replacement field values come from Twitter ``user`` objects
      (`Example <https://gist.githubusercontent.com/mikf/99d2719b3845023326c7a4b6fb88dd04/raw/275b4f0541a2c7dc0a86d3998f7d253e8f10a588/github.json>`_)
Special Values
    ``"user"``
        ``https://twitter.com/i/user/{rest_id}``
    ``"timeline"``
        ``https://twitter.com/id:{rest_id}/timeline``
    ``"tweets"``
        ``https://twitter.com/id:{rest_id}/tweets``
    ``"media"``
        ``https://twitter.com/id:{rest_id}/media``
Note
    To allow gallery-dl to follow custom URL formats, set the blacklist__
    for ``twitter`` to a non-default value, e.g. an empty string ``""``.

.. __: `extractor.*.blacklist & .whitelist`_


extractor.twitter.videos
------------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Control video download behavior.

    ``true``
        Download videos
    ``"ytdl"``
        Download videos using |ytdl|
    ``false``
        Skip video Tweets


extractor.unsplash.format
-------------------------
Type
    ``string``
Default
    ``"raw"``
Description
    Name of the image format to download.
Available Formats
    * ``"raw"``
    * ``"full"``
    * ``"regular"``
    * ``"small"``
    * ``"thumb"``


extractor.vipergirls.domain
---------------------------
Type
    ``string``
Default
    ``"viper.click"``
Description
    Specifies the domain used by ``vipergirls`` extractors.

    For example ``"viper.click"`` if the main domain is blocked or to bypass Cloudflare,


extractor.vipergirls.like
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Automatically `like` posts after downloading their images.
Note
    Requires `login <extractor.*.username & .password_>`__
    or `cookies <extractor.*.cookies_>`__


extractor.vipergirls.order-posts
--------------------------------
Type
    ``string``
Default
    ``"desc"``
Description
    Controls the order in which
    posts of a ``thread`` are processed.

    ``"asc"``
        Ascending order (oldest first)
    ``"desc"`` | ``"reverse"``
        Descending order (newest first)


extractor.vk.offset
-------------------
Type
    ``integer``
Default
    ``0``
Description
    Custom ``offset`` starting value when paginating over image results.


extractor.vsco.include
----------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"gallery"``
Example
    * ``"avatar,collection"``
    * ``["avatar", "collection"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``avatar``
    * ``gallery``
    * ``spaces``
    * ``collection``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.vsco.videos
---------------------
Type
    ``bool``
Default
    ``true``
Description
    Download video files.


extractor.wallhaven.api-key
---------------------------
Type
    ``string``
Default
    ``null``
Description
    Your `Wallhaven API Key <https://wallhaven.cc/settings/account>`__,
    to use your account's browsing settings and default filters when searching.

    See https://wallhaven.cc/help/api for more information.


extractor.wallhaven.include
---------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"uploads"``
Example
    * ``"uploads,collections"``
    * ``["uploads", "collections"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``uploads``
    * ``collections``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.wallhaven.metadata
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract additional metadata (tags, uploader)
Note
    This requires 1 additional HTTP request per post.


extractor.weasyl.api-key
------------------------
Type
    ``string``
Default
    ``null``
Description
    Your `Weasyl API Key <https://www.weasyl.com/control/apikeys>`__,
    to use your account's browsing settings and filters.


extractor.weasyl.metadata
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    | Fetch extra submission metadata during gallery downloads.
    | (``comments``, ``description``, ``favorites``, ``folder_name``,
      ``tags``, ``views``)
Note
    This requires 1 additional HTTP request per submission.


extractor.webtoons.quality
--------------------------
Type
    * ``integer``
    * ``string``
    * ``object`` (`ext` → `type`)

Default
    ``"original"``
Example
    * ``90``
    * ``"q50"``
    * ``{"jpg": "q80", "jpeg": "q80", "png": false}``
Description
    Controls the quality of downloaded files by modifying URLs' ``type`` parameter.

    ``"original"``
        Download minimally compressed versions of JPG files
    any ``integer``
        Use ``"q<VALUE>"`` as ``type`` parameter for JPEG files
    any ``string``
        Use this value as ``type`` parameter for JPEG files
    any ``object``
        | Use the given values as ``type`` parameter for URLs with the specified extensions
        | - Set a value to ``false`` to completely remove these extension's ``type`` parameter
        | - Omit an extension to leave its URLs unchanged


extractor.webtoons.banners
--------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download the active comic's ``banner``.


extractor.webtoons.thumbnails
-----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download the active episode's ``thumbnail``.

    Useful for creating CBZ archives with actual source thumbnails.


extractor.weibo.gifs
--------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Download ``gif`` files.

    Set this to ``"video"`` to download GIFs as video files.


extractor.weibo.include
-----------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"feed"``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.
Supported Values
    * ``home``
    * ``feed``
    * ``videos``
    * ``newvideo``
    * ``article``
    * ``album``
Note
    It is possible to use ``"all"`` instead of listing all values separately.


extractor.weibo.livephoto
-------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download ``livephoto`` files.


extractor.weibo.movies
----------------------
Type
    ``bool``
Default
    ``false``
Description
    Download ``movie`` videos.


extractor.weibo.retweets
------------------------
Type
    ``bool``
Default
    ``false``
Description
    Fetch media from retweeted posts.

    If this value is ``"original"``, metadata for these files
    will be taken from the original posts, not the retweeted posts.


extractor.weibo.text
--------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract full ``text`` & ``text_raw`` metadata
    for statuses with truncated ``text``.


extractor.weibo.videos
----------------------
Type
    ``bool``
Default
    ``true``
Description
    Download video files.


extractor.wikimedia.format
--------------------------
Type
    ``string``
Default
    ``fandom`` | ``wikigg``
        ``"original"``
    otherwise
        ``""``
Description
    Sets the `format` query parameter value
    added to all download URLs.


extractor.wikimedia.image-revisions
-----------------------------------
Type
    ``integer``
Default
    ``1``
Description
    Number of revisions to return for a single image.

    The dafault value of 1 only returns the latest revision.

    The value must be between 1 and 500.
Note
    The API sometimes returns image revisions on article pages even when this option is
    set to 1. However, setting it to a higher value may reduce the number of API requests.


extractor.wikimedia.limit
-------------------------
Type
    ``integer``
Default
    ``50``
Description
    Number of results to return in a single API query.

    The value must be between 10 and 500.


extractor.wikimedia.subcategories
---------------------------------
Type
    ``bool``
Default
    ``true``
Description
    For ``Category:`` pages, recursively descent into subcategories.


extractor.ytdl.cmdline-args
---------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Example
    * ``"--quiet --write-sub --merge-output-format mkv"``
    * ``["--quiet", "--write-sub", "--merge-output-format", "mkv"]``
Description
    Additional ``ytdl`` options specified as command-line arguments.

    See
    `yt-dlp options <https://github.com/yt-dlp/yt-dlp#usage-and-options>`__
    /
    `youtube-dl options <https://github.com/ytdl-org/youtube-dl#options>`__


extractor.ytdl.config-file
--------------------------
Type
    |Path|_
Example
    ``"~/.config/yt-dlp/config"``
Description
    Location of a |ytdl| configuration file to load options from.


extractor.ytdl.deprecations
---------------------------
Type
    ´´bool´´
Default
    ``false``
Description
    Allow |ytdl| to warn about deprecated options and features.


extractor.ytdl.enabled
----------------------
Type
    ``bool``
Default
    ``false``
Description
    Process URLs otherwise unsupported by gallery-dl with |ytdl|.


extractor.ytdl.format
---------------------
Type
    ``string``
Default
    | Default of the ``ytdl`` `module <extractor.ytdl.module_>`__ used.
    | (``"bestvideo*+bestaudio/best"`` for ``yt_dlp``,
       ``"bestvideo+bestaudio/best"`` for ``youtube_dl``)
Description
    ``ytdl`` format selection string.

    See
    `yt-dlp format selection <https://github.com/yt-dlp/yt-dlp#format-selection>`__
    /
    `youtube-dl format selection <https://github.com/ytdl-org/youtube-dl#format-selection>`__


extractor.ytdl.generic
----------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Enables the use of |ytdl's| ``Generic`` extractor.

    Set this option to ``"force"`` for the same effect as
    ``--force-generic-extractor``.


extractor.ytdl.generic-category
-------------------------------
Type
    ``bool``
Default
    ``true``
Description
    When using |ytdl's| ``Generic`` extractor,
    change `category` to ``"ytdl-generic"`` and
    set `subcategory` to the input URL's domain.


extractor.ytdl.logging
----------------------
Type
    ``bool``
Default
    ``true``
Description
    Route |ytdl's| output through gallery-dl's logging system.
    Otherwise it will be written directly to stdout/stderr.
Note
    Set ``quiet`` and ``no_warnings`` in
    `extractor.ytdl.raw-options`_ to ``true`` to suppress all output.


extractor.ytdl.module
---------------------
Type
    |Module|_
Default
    ``null``
Example
    * ``"yt-dlp"``
    * ``"/home/user/.local/lib/python3.13/site-packages/youtube_dl"``
Description
    The ``ytdl`` |Module|_ to import.

    Setting this to ``null`` will try to import ``"yt_dlp"``
    followed by ``"youtube_dl"`` as fallback.


extractor.ytdl.raw-options
--------------------------
Type
    ``object`` (`name` → `value`)
Example
    .. code:: json

        {
            "quiet": true,
            "writesubtitles": true,
            "merge_output_format": "mkv"
        }
Description
    Additional options passed directly to the ``YoutubeDL`` constructor.

    Available options can be found in
    `yt-dlp's docstrings <https://github.com/yt-dlp/yt-dlp/blob/2024.05.27/yt_dlp/YoutubeDL.py#L200>`__
    /
    `youtube-dl's docstrings <https://github.com/ytdl-org/youtube-dl/blob/0153b387e57e0bb8e580f1869f85596d2767fb0d/youtube_dl/YoutubeDL.py#L157>`__


extractor.zerochan.extensions
-----------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``["jpg", "png", "webp", "gif"]``
Example
    * ``"gif"``
    * ``["webp", "gif", "jpg"}``
Description
    List of filename extensions to try when dynamically building download URLs
    (`"pagination": "api" <extractor.zerochan.pagination_>`__ +
    `"metadata": false <extractor.zerochan.metadata_>`__)


extractor.zerochan.metadata
---------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract additional metadata (date, md5, tags, ...)
Note
    This requires 1-2 additional HTTP requests per post.


extractor.zerochan.pagination
-----------------------------
Type
    ``string``
Default
    ``"api"``
Description
    Controls how to paginate over tag search results.

    ``"api"``
        Use the `JSON API <https://www.zerochan.net/api>`__
        (no ``extension`` metadata)
    ``"html"``
        Parse HTML pages
        (limited to 100 pages * 24 posts)


extractor.zerochan.redirects
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Automatically follow tag redirects.


extractor.[booru].tags
----------------------
Type
    ``bool``
Default
    ``false``
Description
    Group ``tags`` by type and
    provide them as ``tags_<type>`` metadata fields,
    for example ``tags_artist`` or ``tags_character``.
Note
    This requires 1 additional HTTP request per post.


extractor.[booru].notes
-----------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract overlay notes (position and text).
Note
    This requires 1 additional HTTP request per post.


extractor.[booru].url
---------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"file_url"``
Example
    * ``"preview_url"``
    * ``["sample_url", "preview_url", "file_url"]``
Description
    Alternate field name to retrieve download URLs from.

    When multiple names are given, download the first available one.


extractor.[manga-extractor].chapter-reverse
-------------------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Reverse the order of chapter URLs extracted from manga pages.

    ``true``
        Start with the latest chapter
    ``false``
        Start with the first chapter


extractor.[manga-extractor].page-reverse
----------------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download manga chapter pages in reverse order.


Downloader Options
==================


downloader.*.enabled
--------------------
Type
    ``bool``
Default
    ``true``
Description
    Enable/Disable this downloader module.


downloader.*.filesize-min & .filesize-max
-----------------------------------------
Type
    ``string``
Default
    ``null``
Example
    ``"32000"``, ``"500k"``, ``"2.5M"``
Description
    Minimum/Maximum allowed file size in bytes.
    Any file smaller/larger than this limit will not be downloaded.

    Possible values are valid integer or floating-point numbers
    optionally followed by one of ``k``, ``m``. ``g``, ``t``, or ``p``.
    These suffixes are case-insensitive.


downloader.*.mtime
------------------
Type
    ``bool``
Default
    ``true``
Description
    Use |Last-Modified|_ HTTP response headers
    to set file modification times.


downloader.*.part
-----------------
Type
    ``bool``
Default
    ``true``
Description
    Controls the use of ``.part`` files during file downloads.

    ``true``
        Write downloaded data into ``.part`` files and rename
        them upon download completion. This mode additionally supports
        resuming incomplete downloads.
    ``false``
        Do not use ``.part`` files and write data directly
        into the actual output files.


downloader.*.part-directory
---------------------------
Type
    |Path|_
Default
    ``null``
Description
    Alternate location for ``.part`` files.

    Missing directories will be created as needed.
    If this value is ``null``, ``.part`` files are going to be stored
    alongside the actual output files.


downloader.*.progress
---------------------
Type
    ``float``
Default
    ``3.0``
Description
    Number of seconds until a download progress indicator
    for the current download is displayed.

    Set this option to ``null`` to disable this indicator.


downloader.*.rate
-----------------
Type
    * ``string``
    * ``list`` with 2 ``strings``
Default
    ``null``
Example
    * ``"32000"``
    * ``"500k"``
    * ``"1M - 2.5M"``
    * ``["1M", "2.5M"]``
Description
    Maximum download rate in bytes per second.

    Possible values are valid integer or floating-point numbers
    optionally followed by one of ``k``, ``m``. ``g``, ``t``, or ``p``.
    These suffixes are case-insensitive.

    If given as a range, the maximum download rate
    will be randomly chosen before each download.
    (see `random.randint() <https://docs.python.org/3/library/random.html#random.randint>`_)


downloader.*.retries
--------------------
Type
    ``integer``
Default
    `extractor.*.retries`_
Description
    Maximum number of retries during file downloads,
    or ``-1`` for infinite retries.


downloader.*.timeout
--------------------
Type
    ``float``
Default
    `extractor.*.timeout`_
Description
    Connection timeout during file downloads.


downloader.*.verify
-------------------
Type
    * ``bool``
    * ``string``
Default
    `extractor.*.verify`_
Description
    Certificate validation during file downloads.


downloader.*.proxy
------------------
Type
    * ``string``
    * ``object`` (`scheme` → `proxy`)
Default
    `extractor.*.proxy`_
Description
    Proxy server used for file downloads.

    Disable the use of a proxy for file downloads
    by explicitly setting this option to ``null``.


downloader.http.adjust-extensions
---------------------------------
Type
    ``bool``
Default
    ``true``
Description
    Check file headers of downloaded files
    and adjust their filename extensions if they do not match.

    For example, this will change the filename extension (``{extension}``)
    of a file called ``example.png`` from ``png`` to ``jpg`` when said file
    contains JPEG/JFIF data.


downloader.http.consume-content
-------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Controls the behavior when an HTTP response is considered
    unsuccessful

    If the value is ``true``, consume the response body. This
    avoids closing the connection and therefore improves connection
    reuse.

    If the value is ``false``, immediately close the connection
    without reading the response. This can be useful if the server
    is known to send large bodies for error responses.


downloader.http.chunk-size
--------------------------
Type
    * ``integer``
    * ``string``
Default
    ``32768``
Example
    ``"50k"``, ``"0.8M"``
Description
    Number of bytes per downloaded chunk.

    Possible values are integer numbers
    optionally followed by one of ``k``, ``m``. ``g``, ``t``, or ``p``.
    These suffixes are case-insensitive.


downloader.http.headers
-----------------------
Type
    ``object`` (`name` → `value`)
Example
    ``{"Accept": "image/webp,*/*", "Referer": "https://example.org/"}``
Description
    Additional HTTP headers to send when downloading files,


downloader.http.retry-codes
---------------------------
Type
    ``list`` of ``integers``
Default
    `extractor.*.retry-codes`_
Description
    Additional `HTTP response status codes <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status>`__
    to retry a download on.

    Codes ``200``, ``206``, and ``416`` (when resuming a `partial <downloader.*.part_>`__
    download) will never be retried and always count as success,
    regardless of this option.

    ``5xx`` codes (server error responses)  will always be retried,
    regardless of this option.


downloader.http.sleep-429
-------------------------
Type
    |Duration|_
Default
    `extractor.*.sleep-429`_
Description
    Number of seconds to sleep when receiving a `429 Too Many Requests`
    response before `retrying <downloader.*.retries_>`__ the request.
Note
    Requires
    `retry-codes <downloader.http.retry-codes_>`__
    to include ``429``.


downloader.http.validate
------------------------
Type
    ``bool``
Default
    ``true``
Description
    Check for invalid responses.

    Fail a download when a file does not pass
    instead of downloading a potentially broken file.


downloader.http.validate-html
-----------------------------
Type
    ``bool``
Default
    ``true``
Description
    Check for unexpected HTML responses.

    Fail file downloads with a ``text/html``
    `Content-Type header <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Type>`__
    when expecting a media file instead.


downloader.ytdl.cmdline-args
----------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Example
    * ``"--quiet --write-sub --merge-output-format mkv"``
    * ``["--quiet", "--write-sub", "--merge-output-format", "mkv"]``
Description
    Additional ``ytdl`` options specified as command-line arguments.

    See
    `yt-dlp options <https://github.com/yt-dlp/yt-dlp#usage-and-options>`__
    /
    `youtube-dl options <https://github.com/ytdl-org/youtube-dl#options>`__


downloader.ytdl.config-file
---------------------------
Type
    |Path|_
Example
    ``"~/.config/yt-dlp/config"``
Description
    Location of a |ytdl| configuration file to load options from.


downloader.ytdl.deprecations
----------------------------
Type
    ´´bool´´
Default
    ``false``
Description
    Allow |ytdl| to warn about deprecated options and features.


downloader.ytdl.format
----------------------
Type
    ``string``
Default
    | Default of the ``ytdl`` `module <downloader.ytdl.module_>`__ used.
    | (``"bestvideo*+bestaudio/best"`` for ``yt_dlp``,
       ``"bestvideo+bestaudio/best"`` for ``youtube_dl``)
Description
    ``ytdl`` format selection string.

    See
    `yt-dlp format selection <https://github.com/yt-dlp/yt-dlp#format-selection>`__
    /
    `youtube-dl format selection <https://github.com/ytdl-org/youtube-dl#format-selection>`__


downloader.ytdl.forward-cookies
-------------------------------
Type
    ``bool``
Default
    ``true``
Description
    Forward gallery-dl's cookies to |ytdl|.


downloader.ytdl.logging
-----------------------
Type
    ``bool``
Default
    ``true``
Description
    Route |ytdl's| output through gallery-dl's logging system.
    Otherwise it will be written directly to stdout/stderr.
Note
    Set ``quiet`` and ``no_warnings`` in
    `downloader.ytdl.raw-options`_ to ``true`` to suppress all output.


downloader.ytdl.module
----------------------
Type
    |Module|_
Default
    ``null``
Example
    * ``"yt-dlp"``
    * ``"/home/user/.local/lib/python3.13/site-packages/youtube_dl"``
Description
    The ``ytdl`` |Module|_ to import.

    Setting this to ``null`` will try to import ``"yt_dlp"``
    followed by ``"youtube_dl"`` as fallback.


downloader.ytdl.outtmpl
-----------------------
Type
    ``string``
Default
    ``null``
Description
    The `Output Template`
    used to generate filenames for files downloaded with ``ytdl``.

    See
    `yt-dlp output template <https://github.com/yt-dlp/yt-dlp#output-template>`__
    /
    `youtube-dl output template <https://github.com/ytdl-org/youtube-dl#output-template>`__.
Special Values
    ``null``
        generate filenames with `extractor.*.filename`_
    ``"default"``
        use |ytdl's| default, currently
        ``"%(title)s [%(id)s].%(ext)s"`` for yt-dlp_ /
        ``"%(title)s-%(id)s.%(ext)s"`` for youtube-dl_
Note
    An output template other than ``null`` might
    cause unexpected results in combination with certain options
    (e.g. ``"skip": "enumerate"``)


downloader.ytdl.raw-options
---------------------------
Type
    ``object`` (`name` → `value`)
Example
    .. code:: json

        {
            "quiet": true,
            "writesubtitles": true,
            "merge_output_format": "mkv"
        }

Description
    Additional options passed directly to the ``YoutubeDL`` constructor.

    Available options can be found in
    `yt-dlp's docstrings <https://github.com/yt-dlp/yt-dlp/blob/2024.05.27/yt_dlp/YoutubeDL.py#L200>`__
    /
    `youtube-dl's docstrings <https://github.com/ytdl-org/youtube-dl/blob/0153b387e57e0bb8e580f1869f85596d2767fb0d/youtube_dl/YoutubeDL.py#L157>`__



Output Options
==============


output.mode
-----------
Type
    * ``string``
    * ``object`` (`key` → `format string`)
Default
    ``"auto"``
Description
    Controls the output string format and status indicators.

    ``"null"``
        No output
    ``"pipe"``
        Suitable for piping to other processes or files
    ``"terminal"``
        Suitable for the standard Windows console
    ``"color"``
        Suitable for terminals that understand ANSI escape codes and colors
    ``"auto"``
        ``"pipe"`` if not on a TTY,
        ``"terminal"`` on Windows with `output.ansi`_ disabled,
        ``"color"`` otherwise.

    | It is possible to use custom output format strings
      by setting this option to an ``object`` and specifying
    | ``start``, ``success``, ``skip``, ``progress``, and ``progress-total``.

    For example, the following will replicate the same output as |mode: color|:

    .. code:: json

        {
            "start"  : "{}",
            "success": "\r\u001b[1;32m{}\u001b[0m\n",
            "skip"   : "\u001b[2m{}\u001b[0m\n",
            "progress"      : "\r{0:>7}B {1:>7}B/s ",
            "progress-total": "\r{3:>3}% {0:>7}B {1:>7}B/s "
        }

    ``start``, ``success``, and ``skip`` are used to output the current
    filename, where ``{}`` or ``{0}`` is replaced with said filename.
    If a given format string contains printable characters other than that,
    their number needs to be specified as ``[<number>, <format string>]``
    to get the correct results for `output.shorten`_. For example

    .. code:: json

            "start"  : [12, "Downloading {}"]

    | ``progress`` and ``progress-total`` are used when displaying the
      `download progress indicator <downloader.*.progress_>`__,
    | ``progress`` when the total number of bytes to download is unknown,
      ``progress-total`` otherwise.

    For these format strings

    * ``{0}`` is number of bytes downloaded
    * ``{1}`` is number of downloaded bytes per second
    * ``{2}`` is total number of bytes
    * ``{3}`` is percent of bytes downloaded to total bytes


output.stdout & .stdin & .stderr
--------------------------------
Type
    * ``string``
    * ``object``
Example
    .. code:: json

        "utf-8"

    .. code:: json

        {
            "encoding": "utf-8",
            "errors": "replace",
            "line_buffering": true
        }

Description
    `Reconfigure <https://docs.python.org/3/library/io.html#io.TextIOWrapper.reconfigure>`__
    a `standard stream <https://docs.python.org/3/library/sys.html#sys.stdin>`__.

    Possible options are

    * ``encoding``
    * ``errors``
    * ``newline``
    * ``line_buffering``
    * ``write_through``

    When this option is specified as a simple ``string``,
    it is interpreted as ``{"encoding": "<string-value>", "errors": "replace"}``
Note
    ``errors`` always defaults to ``"replace"``


output.shorten
--------------
Type
    ``bool``
Default
    ``true``
Description
    Controls whether the output strings should be shortened to fit
    on one console line.

    Set this option to ``"eaw"`` to also work with east-asian characters
    with a display width greater than 1.


output.colors
-------------
Type
    ``object`` (`key` → `ANSI color`)
Default
    .. code:: json

        {
            "success": "1;32",
            "skip"   : "2",
            "debug"  : "0;37",
            "info"   : "1;37",
            "warning": "1;33",
            "error"  : "1;31"
        }

Description
    Controls the
    `ANSI colors <https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797#colors--graphics-mode>`__
    used for various outputs.

    Output for |mode: color|__

    * ``success``: successfully downloaded files
    * ``skip``: skipped files

    Logging Messages:

    * ``debug``: debug logging messages
    * ``info``: info logging messages
    * ``warning``: warning logging messages
    * ``error``: error logging messages

.. __: `output.mode`_


output.ansi
-----------
Type
    ``bool``
Default
    ``true``
Description
    | On Windows, enable ANSI escape sequences and colored output
    | by setting the ``ENABLE_VIRTUAL_TERMINAL_PROCESSING`` flag for stdout and stderr.


output.skip
-----------
Type
    ``bool``
Default
    ``true``
Description
    Show skipped file downloads.


output.fallback
---------------
Type
    ``bool``
Default
    ``true``
Description
    Include fallback URLs in the output of ``-g/--get-urls``.


output.private
--------------
Type
    ``bool``
Default
    ``false``
Description
    Include private fields,
    i.e. fields whose name starts with an underscore,
    in the output of ``-K/--list-keywords`` and ``-j/--dump-json``.


output.progress
---------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Controls the progress indicator when *gallery-dl* is run with
    multiple URLs as arguments.

    ``true``
        Show the default progress indicator
        (``"[{current}/{total}] {url}"``)
    ``false``
        Do not show any progress indicator
    Any ``string``
        Show the progress indicator using this
        as a custom `format string`_. Possible replacement keys are
        ``current``, ``total``  and ``url``.


output.log
----------
Type
    * `Format String`_
    * |Logging Configuration|_
Default
    ``"[{name}][{levelname}] {message}"``
Description
    Configuration for logging output to stderr.


output.logfile
--------------
Type
    * |Path|_
    * |Logging Configuration|_
Description
    File to write logging output to.


output.unsupportedfile
----------------------
Type
    * |Path|_
    * |Logging Configuration|_
Description
    File to write external URLs unsupported by *gallery-dl* to.

    The default `Format String`_ here is ``"{message}"``.


output.errorfile
----------------
Type
    * |Path|_
    * |Logging Configuration|_
Description
    File to write input URLs which returned an error to.

    The default `Format String`_ here is also ``"{message}"``.

    When combined with
    ``-I``/``--input-file-comment`` or
    ``-x``/``--input-file-delete``,
    this option will cause *all* input URLs from these files
    to be commented/deleted after processing them
    and not just successful ones.


output.num-to-str
-----------------
Type
    ``bool``
Default
    ``false``
Description
    Convert numeric values (``integer`` or ``float``) to ``string``
    before outputting them as JSON.



Postprocessor Options
=====================

This section lists all options available inside
`Postprocessor Configuration`_ objects.

Each option is titled as ``<name>.<option>``, meaning a post processor
of type ``<name>`` will look for an ``<option>`` field inside its "body".
For example an ``exec`` post processor will recognize
an `async <exec.async_>`__,  `command <exec.command_>`__,
and `event <exec.event_>`__ field:

.. code:: json

    {
        "name"   : "exec",
        "async"  : false,
        "command": "...",
        "event"  : "after"
    }


classify.mapping
----------------
Type
    ``object`` (`directory` → `extensions`)
Default
    .. code:: json

        {
            "Pictures" : ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp",
                          "avif", "heic", "heif", "ico", "psd"],
            "Video"    : ["flv", "ogv", "avi", "mp4", "mpg", "mpeg", "3gp", "mkv",
                          "webm", "vob", "wmv", "m4v", "mov"],
            "Music"    : ["mp3", "aac", "flac", "ogg", "wma", "m4a", "wav"],
            "Archives" : ["zip", "rar", "7z", "tar", "gz", "bz2"],
            "Documents": ["txt", "pdf"]
        }

Description
    A mapping from directory names to filename extensions that should
    be stored in them.

    Files with an extension not listed will be ignored and stored
    in their default location.


compare.action
--------------
Type
    ``string``
Default
    ``"replace"``
Description
    The action to take when files do **not** compare as equal.

    ``"replace"``
        Replace/Overwrite the old version with the new one
    ``"enumerate"``
        Add an enumeration index to the filename of the new
        version like `skip = "enumerate" <extractor.*.skip_>`__


compare.equal
-------------
Type
    ``string``
Default
    ``"null"``
Description
    The action to take when files do compare as equal.

    ``"abort:N"``
        Stop the current extractor run
        after ``N`` consecutive files compared as equal.
    ``"terminate:N"``
        Stop the current extractor run,
        including parent extractors,
        after ``N`` consecutive files compared as equal.
    ``"exit:N"``
        Exit the program
        after ``N`` consecutive files compared as equal.


compare.shallow
---------------
Type
    ``bool``
Default
    ``false``
Description
    Only compare file sizes. Do not read and compare their content.


directory.event
---------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"prepare"``
Description
    The event(s) for which directory_ `Format Strings`_ are (re)evaluated.

    See `metadata.event`_ for a list of available events.


exec.archive
------------
Type
    * ``string``
    * |Path|_
Description
    Database to store IDs of executed commands in,
    similar to `extractor.*.archive`_.

    The following archive options are also supported:

    * `archive-format <extractor.*.archive-format_>`__
    * `archive-prefix <extractor.*.archive-prefix_>`__
    * `archive-pragma <extractor.*.archive-pragma_>`__
    * `archive-table  <extractor.*.archive-table_>`__


exec.async
----------
Type
    ``bool``
Default
    ``false``
Description
    Controls whether to wait for a subprocess to finish
    or to let it run asynchronously.


exec.command
------------
Type
    * ``string``
    * ``list`` of ``strings``
Example
    * ``"convert {} {}.png && rm {}"``
    * ``["echo", "{user[account]}", "{id}"]``
Description
    The command to run.

    * If this is a ``string``, it will be executed using the system's
      shell, e.g. ``/bin/sh``. Any ``{}`` will be replaced
      with the full path of a file or target directory, depending on
      `exec.event`_

    * If this is a ``list``, the first element specifies the program
      name and any further elements its arguments.

      Each element of this list is evaluated as a `Format String`_ using
      the files' metadata as well as
      ``{_path}``, ``{_temppath}``, ``{_directory}``, and ``{_filename}``.


exec.commands
-------------
Type
    ``list`` of `commands <exec.command_>`__
Example
    .. code:: json

        [
            ["echo", "{user[account]}", "{id}"]
            ["magick", "convert" "{_path}",  "\fF {_path.rpartition('.')[0]}.png"],
            "rm {}",
        ]
Description
    Multiple `commands <exec.command_>`__ to run in succession.

    All `commands <exec.command_>`__ after the first returning with a non-zero
    exit status will not be run.


exec.event
----------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"after"``
Description
    The event(s) for which `exec.command`_ is run.

    See `metadata.event`_ for a list of available events.


exec.session
------------
Type
    ``bool``
Default
    ``false``
Description
    Start subprocesses in a new session.

    On Windows, this means passing
    `CREATE_NEW_PROCESS_GROUP <https://docs.python.org/3/library/subprocess.html#subprocess.CREATE_NEW_PROCESS_GROUP>`__
    as a ``creationflags`` argument to
    `subprocess.Popen <https://docs.python.org/3/library/subprocess.html#subprocess.Popen>`__

    On POSIX systems, this means enabling the
    ``start_new_session`` argument of
    `subprocess.Popen <https://docs.python.org/3/library/subprocess.html#subprocess.Popen>`__
    to have it call ``setsid()``.


hash.chunk-size
---------------
Type
    ``integer``
Default
    ``32768``
Description
    Number of bytes read per chunk during file hash computation.


hash.event
----------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"file"``
Description
    The event(s) for which `file hashes <hash.hashes_>`__ are computed.

    See `metadata.event`_ for a list of available events.


hash.filename
-------------
Type
    * ``bool``
Default
    ``false``
Description
    Rebuild `filenames <extractor.*.filename_>`__ after computing
    `hash digests <hash.hashes_>`__ and adding them to the metadata dict.


hash.hashes
-----------
Type
    * ``string``
    * ``object`` (`field name` → `hash algorithm`)
Default
    ``"md5,sha1"``
Example
    .. code:: json

        "sha256:hash_sha,sha3_512:hash_sha3"

    .. code:: json

        {
            "hash_sha" : "sha256",
            "hash_sha3": "sha3_512"
        }

Description
    Hash digests to compute.

    For a list of available hash algorithms, run

    .. code::

        python -c "import hashlib; print('\n'.join(hashlib.algorithms_available))"

    or see `python/hashlib <https://docs.python.org/3/library/hashlib.html>`__.

    * If this is a ``string``,
      it is parsed as a a comma-separated list of algorthm-fieldname pairs:

      .. code::

          [<hash algorithm> ":"] <field name> ["," ...]

      When ``<hash algorithm>`` is omitted,
      ``<field name>`` is used as algorithm name.

    * If this is an ``object``,
      it is a ``<field name>`` to ``<algorithm name>`` mapping
      for hash digests to compute.


metadata.mode
-------------
Type
    ``string``
Default
    ``"json"``
Description
    Selects how to process metadata.

    ``"json"``
        Write metadata using |json.dump()|_
    ``"jsonl"``
        Write metadata in `JSON Lines <https://jsonlines.org/>`__ format
    ``"tags"``
        Write ``tags`` separated by newlines
    ``"custom"``
        Write the result of applying `metadata.content-format`_
        to a file's metadata dictionary
    ``"modify"``
        Add or modify metadata entries
    ``"delete"``
        Remove metadata entries


metadata.filename
-----------------
Type
    `Format String`_
Default
    ``null``
Example
    ``"{id}.data.json"``
Description
    A `Format String`_ to generate filenames for metadata files.
    (see `extractor.filename <extractor.*.filename_>`__)

    Using ``"-"`` as filename will write all output to ``stdout``.

    If this option is set, `metadata.extension`_ and
    `metadata.extension-format`_ will be ignored.


metadata.directory
------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"."``
Example
    * ``"metadata"``
    * ``["..", "metadata", "\fF {id // 500 * 500}"]``
Description
    Directory where metadata files are stored in
    relative to `metadata.base-directory`_.


metadata.base-directory
-----------------------
Type
    * ``bool``
    * |Path|_
Default
    ``false``
Description
    Selects the relative location for metadata files.

    ``false``
        Current target location for file downloads (base-directory_ + directory_)
    ``true``
        Current base-directory_ location
    any |Path|_
        Custom location


metadata.extension
------------------
Type
    ``string``
Default
    ``"json"`` or ``"txt"``
Description
    Filename extension for metadata files that will be appended to the
    original file names.


metadata.extension-format
-------------------------
Type
    `Format String`_
Example
    * ``"{extension}.json"``
    * ``"json"``
Description
    Custom `Format String`_ to generate filename extensions
    for metadata files, which will replace the original filename extension.
Note
    When this option is set, `metadata.extension`_ is ignored.


metadata.metadata-path
----------------------
Type
    ``string``
Example
    ``"_meta_path"``
Description
    Insert the path of generated files
    into metadata dictionaries as the given name.


metadata.event
--------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"file"``
Example
    * ``"prepare,file,after"``
    * ``["prepare-after", "skip"]``
Description
    The event(s) for which metadata gets written to a file.

    Available events are:

    ``init``
        After post processor initialization
        and before the first file download
    ``finalize``
        On extractor shutdown, e.g. after all files were downloaded
    ``finalize-success``
        On extractor shutdown when no error occurred
    ``finalize-error``
        On extractor shutdown when at least one error occurred
    ``prepare``
        Before a file download
    ``prepare-after``
        Before a file download,
        but after building and checking file paths
    ``file``
        When completing a file download,
        but before it gets moved to its target location
    ``after``
        After a file got moved to its target location
    ``skip``
        When skipping a file download
    ``error``
        After a file download failed
    ``post``
        When starting to download all files of a `post`,
        e.g. a Tweet on Twitter or a post on Patreon.
    ``post-after``
        After downloading all files of a `post`


metadata.include
----------------
Type
    ``list`` of ``strings``
Example
    ``["id", "width", "height", "description"]``
Description
    Include only the given top-level keys when writing JSON data.
Note
    Missing or undefined fields will be silently ignored.


metadata.exclude
----------------
Type
    ``list`` of ``strings``
Example
    ``["blocked", "watching", "status"]``
Description
    Exclude all given keys from written JSON data.
Note
    Cannot be used with `metadata.include`_.


metadata.fields
---------------
Type
    * ``list`` of ``strings``
    * ``object`` (`field name` → `Format String`_)
Example
    .. code:: json

        ["blocked", "watching", "status[creator][name]"]

    .. code:: json

        {
            "blocked"         : "***",
            "watching"        : "\fE 'yes' if watching else 'no'",
            "status[username]": "{status[creator][name]!l}"
        }

Description
    ``"mode": "delete"``
        A list of metadata field names to remove.
    ``"mode": "modify"``
        An object with metadata field names mapping to a `Format String`_
        whose result is assigned to that field name.
Note:
    Unlike standard `Format Strings`_, replacement fields here
    preserve the original type of their value
    instead of automatically converting it to |type-str|_.


metadata.content-format
-----------------------
Type
    * `Format String`_
    * ``list`` of `Format Strings`_
Example
    * ``"tags:\n\n{tags:J\n}\n"``
    * ``["tags:", "", "{tags:J\n}"]``
Description
    Custom `Format String(s)`_ to build the content of metadata files with.
Note
    Only applies to ``"mode": "custom"``.


metadata.ascii
--------------
Type
    ``bool``
Default
    ``false``
Description
    Escape all non-ASCII characters.

    See the ``ensure_ascii`` argument of |json.dump()|_ for further details.
Note
    Only applies to ``"mode": "json"`` and ``"jsonl"``.


metadata.indent
---------------
Type
    * ``integer``
    * ``string``
Default
    ``4``
Description
    Indentation level of JSON output.

    See the ``indent`` argument of |json.dump()|_ for further details.
Note
    Only applies to ``"mode": "json"``.


metadata.separators
-------------------
Type
    ``list`` with two ``string`` elements
Default
    ``[", ", ": "]``
Description
    ``<item separator>`` - ``<key separator>`` pair
    to separate JSON keys and values with.

    See the ``separators`` argument of |json.dump()|_ for further details.
Note
    Only applies to ``"mode": "json"`` and ``"jsonl"``.


metadata.sort
-------------
Type
    ``bool``
Default
    ``false``
Description
    Sort output by `key`.

    See the ``sort_keys`` argument of |json.dump()|_ for further details.
Note
    Only applies to ``"mode": "json"`` and ``"jsonl"``.


metadata.open
-------------
Type
    ``string``
Default
    ``"w"``
Description
    The ``mode`` in which metadata files get opened.

    For example,
    use ``"a"`` to append to a file's content
    or ``"w"`` to truncate it.

    See the ``mode`` argument of |open()|_ for further details.


metadata.encoding
-----------------
Type
    ``string``
Default
    ``"utf-8"``
Description
    Name of the encoding used to encode a file's content.

    See the ``encoding`` argument of |open()|_ for further details.


metadata.newline
-----------------
Type
    ``string``
Default
    ``null``
Description
    The newline sequence used in metadata files.

    If ``null``, any ``\n`` characters
    written are translated to the system default line separator.

    See the ``newline`` argument of |open()|_ for further details.
Supported Values
    ``null``
        Any ``\n`` characters
        written are translated to the system default line separator.
    ``""`` | ``"\n"``
        Don't replace newline characters.
    ``"\r"`` | ``"\r\n"``
        Replace newline characters with the given sequence.


metadata.private
----------------
Type
    ``bool``
Default
    ``false``
Description
    Include private fields,
    i.e. fields whose name starts with an underscore.


metadata.skip
-------------
Type
    ``bool``
Default
    ``false``
Description
    Do not overwrite already existing files.


metadata.archive
----------------
Type
    * ``string``
    * |Path|_
Description
    Database to store IDs of generated metadata files in,
    similar to `extractor.*.archive`_.

    The following archive options are also supported:

    * `archive-format <extractor.*.archive-format_>`__
    * `archive-prefix <extractor.*.archive-prefix_>`__
    * `archive-pragma <extractor.*.archive-pragma_>`__
    * `archive-table  <extractor.*.archive-table_>`__


metadata.mtime
--------------
Type
    ``bool``
Default
    ``false``
Description
    Set modification times of generated metadata files
    according to the accompanying downloaded file.

    Enabling this option will only have an effect
    *if* there is actual ``mtime`` metadata available, that is

    * after a file download (``"event": "file"`` (default), ``"event": "after"``)
    * when running *after* an ``mtime`` post processes for the same `event <metadata.event_>`__

    For example, a ``metadata`` post processor for ``"event": "post"`` will
    *not* be able to set its file's modification time unless an ``mtime``
    post processor with ``"event": "post"`` runs *before* it.


mtime.event
-----------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"file"``
Description
    The event(s) for which `mtime.key`_ or `mtime.value`_ get evaluated.

    See `metadata.event`_ for a list of available events.


mtime.key
---------
Type
    ``string``
Default
    ``"date"``
Description
    Name of the metadata field whose value should be used.

    This value must be either a UNIX timestamp or a
    |type-datetime|_ object.
Note
    This option is ignored if `mtime.value`_ is set.


mtime.value
-----------
Type
    `Format String`_
Default
    ``null``
Example
    * ``"{status[date]}"``
    * ``"{content[0:6]:R22/2022/D%Y%m%d/}"``
Description
    The `Format String`_ whose value should be used.

    The resulting value must be either a UNIX timestamp or a
    |type-datetime|_ object.
Note:
    Unlike standard `Format Strings`_, replacement fields here
    preserve the original type of their value
    instead of automatically converting it to |type-str|_.


python.archive
--------------
Type
    * ``string``
    * |Path|_
Description
    Database to store IDs of called Python functions in,
    similar to `extractor.*.archive`_.

    The following archive options are also supported:

    * `archive-format <extractor.*.archive-format_>`__
    * `archive-prefix <extractor.*.archive-prefix_>`__
    * `archive-pragma <extractor.*.archive-pragma_>`__
    * `archive-table  <extractor.*.archive-table_>`__


python.event
------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"file"``
Description
    The event(s) for which `python.function`_ gets called.

    See `metadata.event`_ for a list of available events.


python.expression
-----------------
Type
    Expression_
Example
    * ``"print('Foo Bar')"``
    * ``"terminate()"``
Description
    A Python Expression_ to
    `evaluate <https://docs.python.org/3/library/functions.html#eval>`__.
Note
    Only used with `"mode": "eval" <python.mode_>`__


python.function
---------------
Type
    ``string``
Example
    * ``"my_module:generate_text"``
    * ``"~/.local/share/gdl_utils.py:resize"``
Description
    The Python function to call.

    | This function is specified as ``<module>:<function name>``, where
    | ``<module>`` is a |Module|_ and
      ``<function name>`` is the name of the function in that module.

    It gets called with the current metadata dict as argument.


python.mode
-----------
Type
    ``string``
Default
    ``"function"``
Description
    Selects what Python code to run.

    ``"eval"``
        Evaluate an
        `expression <python.expression_>`__
    ``function"``
        Call a
        `function <python.function_>`__


rename.from
-----------
Type
    `Format String`_
Description
    The `Format String`_ for filenames to rename.

    When no value is given, `extractor.*.filename`_ is used.


rename.to
---------
Type
    `Format String`_
Description
    The `Format String`_ for target filenames.

    When no value is given, `extractor.*.filename`_ is used.


rename.skip
-----------
Type
    ``bool``
Default
    ``true``
Description
    Do not rename a file when another file with the target name already exists.


ugoira.extension
----------------
Type
    ``string``
Default
    ``"webm"``
Description
    Filename extension for the resulting video files.


ugoira.ffmpeg-args
------------------
Type
    ``list`` of ``strings``
Default
    ``null``
Example
    ``["-c:v", "libvpx-vp9", "-an", "-b:v", "2M"]``
Description
    Additional |ffmpeg| command-line arguments.


ugoira.mode
-----------
ugoira.ffmpeg-demuxer
---------------------
Type
    ``string``
Default
    ``"auto"``
Description
    |ffmpeg| demuxer to read and process input files with.
Supported Values
    ``"auto"``
        use ``mkvmerge`` if available, fall back to ``concat`` otherwise
    ``"concat"``
        | https://ffmpeg.org/ffmpeg-formats.html#concat-1
        | Inaccurate frame timecodes for non-uniform frame delays
    ``"image2"``
        | https://ffmpeg.org/ffmpeg-formats.html#image2-1
        | Accurate timecodes, requires nanosecond file timestamps, i.e. no Windows or macOS)
    ``"mkvmerge"``
        Accurate timecodes, only WebM or MKV, requires `mkvmerge <ugoira.mkvmerge-location_>`__)
    ``"archive"``
        Store "original" frames in a ``.zip`` archive



ugoira.ffmpeg-location
----------------------
Type
    |Path|_
Default
    ``"ffmpeg"``
Description
    Location of the ``ffmpeg`` (or ``avconv``) executable to use.


ugoira.mkvmerge-location
------------------------
Type
    |Path|_
Default
    ``"mkvmerge"``
Description
    Location of the ``mkvmerge`` executable for use with the
    `mkvmerge demuxer <ugoira.ffmpeg-demuxer_>`__.


ugoira.ffmpeg-output
--------------------
Type
    * ``bool``
    * ``string``
Default
    ``"error"``
Description
    Controls |ffmpeg| output.

    ``true``
        Enable |ffmpeg| output
    ``false``
        Disable all |ffmpeg| output
    any ``string``
        Pass ``-hide_banner`` and ``-loglevel``
        with this value as argument to |ffmpeg|


ugoira.ffmpeg-twopass
---------------------
Type
    ``bool``
Default
    ``false``
Description
    Enable Two-Pass encoding.


ugoira.framerate
----------------
Type
    ``string``
Default
    ``"auto"``
Description
    Controls the frame rate argument (``-r``) for |ffmpeg|

    ``"auto"``
        Automatically assign a fitting frame rate
        based on delays between frames.
    ``"uniform"``
        Like ``auto``, but assign an explicit frame rate
        only to Ugoira with uniform frame delays.
    any other ``string``
        Use this value as argument for ``-r``.
    ``null`` or an empty ``string``
        Don't set an explicit frame rate.


ugoira.keep-files
-----------------
Type
    ``bool``
Default
    ``false``
Description
    Keep ZIP archives after conversion.


ugoira.libx264-prevent-odd
--------------------------
Type
    ``bool``
Default
    ``true``
Description
    Prevent ``"width/height not divisible by 2"`` errors
    when using ``libx264`` or ``libx265`` encoders
    by applying a simple cropping filter. See this `Stack Overflow
    thread <https://stackoverflow.com/questions/20847674>`__
    for more information.

    This option, when ``libx264/5`` is used, automatically
    adds ``["-vf", "crop=iw-mod(iw\\,2):ih-mod(ih\\,2)"]``
    to the list of |ffmpeg| command-line arguments
    to reduce an odd width/height by 1 pixel and make them even.


ugoira.metadata
---------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    When using ``"mode": "archive"``, save Ugoira frame delay data as
    ``animation.json`` within the archive file.

    If this is a ``string``,
    use it as alternate filename for frame delay files.


ugoira.mtime
------------
Type
    ``bool``
Default
    ``true``
Description
    Set modification times of generated ugoira aniomations.


ugoira.repeat-last-frame
------------------------
Type
    ``bool``
Default
    ``true``
Description
    Allow repeating the last frame when necessary
    to prevent it from only being displayed for a very short amount of time.


ugoira.skip
-----------
Type
    ``bool``
Default
    ``true``
Description
    Do not convert frames if target file already exists.


zip.compression
---------------
Type
    ``string``
Default
    ``"store"``
Description
    Compression method to use when writing the archive.
Supported Values
    * ``"store"``
    * ``"zip"``
    * ``"bzip2"``
    * ``"lzma"``


zip.extension
-------------
Type
    ``string``
Default
    ``"zip"``
Description
    Filename extension for the created ZIP archive.


zip.files
---------
Type
    ``list`` of |Path|
Example
    ``["info.json"]``
Description
    List of extra files to be added to a ZIP archive.
Note
    Relative paths are relative to the current
    `download directory <extractor.*.directory_>`__.


zip.keep-files
--------------
Type
    ``bool``
Default
    ``false``
Description
    Keep the actual files after writing them to a ZIP archive.


zip.mode
--------
Type
    ``string``
Default
    ``"default"``
Description
    ``"default"``
        Write the central directory file header
        once after everything is done or an exception is raised.

    ``"safe"``
        Update the central directory file header
        each time a file is stored in a ZIP archive.

        This greatly reduces the chance a ZIP archive gets corrupted in
        case the Python interpreter gets shut down unexpectedly
        (power outage, SIGKILL) but is also a lot slower.



Miscellaneous Options
=====================


extractor.modules
-----------------
Type
    ``list`` of ``strings``
Default
    The ``modules`` list in
    `extractor/__init__.py <https://github.com/mikf/gallery-dl/blob/master/gallery_dl/extractor/__init__.py#L12>`__
Example
    ``["reddit", "danbooru", "mangadex"]``
Description
    List of internal modules to load when searching for a suitable
    extractor class. Useful to reduce startup time and memory usage.


extractor.module-sources
------------------------
Type
    ``list`` of |Path|_ instances
Example
    ``["~/.config/gallery-dl/modules", null]``
Description
    List of directories to load external extractor modules from.

    Any file in a specified directory with a ``.py`` filename extension
    gets `imported <https://docs.python.org/3/reference/import.html>`__
    and searched for potential extractors,
    i.e. classes with a ``pattern`` attribute.
Note
    ``null`` references internal extractors defined in
    `extractor/__init__.py <https://github.com/mikf/gallery-dl/blob/master/gallery_dl/extractor/__init__.py#L12>`__
    or by `extractor.modules`_.


extractor.category-map
----------------------
Type
    * ``object`` (`category` → `category`)
    * ``string``
Example
    .. code:: json

        {
            "danbooru": "booru",
            "gelbooru": "booru"
        }
Description
    A JSON object mapping category names to their replacements.
Special Values
    * ``"compat"``
        .. code:: json

            {
                "coomer"       : "coomerparty",
                "kemono"       : "kemonoparty",
                "schalenetwork": "koharu",
                "naver-chzzk"  : "chzzk",
                "naver-blog"   : "naver",
                "naver-webtoon": "naverwebtoon",
                "pixiv-novel"  : "pixiv",
                "pixiv-novel:novel"   : ["pixiv", "novel"],
                "pixiv-novel:user"    : ["pixiv", "novel-user"],
                "pixiv-novel:series"  : ["pixiv", "novel-series"],
                "pixiv-novel:bookmark": ["pixiv", "novel-bookmark"]
            }


extractor.config-map
--------------------
Type
    ``object`` (`category` → `category`)
Default
    .. code:: json

        {
            "coomerparty"  : "coomer",
            "kemonoparty"  : "kemono",
            "giantessbooru": "sizebooru",
            "koharu"       : "schalenetwork",
            "chzzk"        : "naver-chzzk",
            "naver"        : "naver-blog",
            "naverwebtoon" : "naver-webtoon",
            "pixiv"        : "pixiv-novel"
        }
Description
    Duplicate the configuration settings of extractor `categories`
    to other names.

    For example, a ``"naver": "naver-blog"`` key-value pair will make all
    ``naver`` config settings available for ``naver-blog`` extractors as well.


jinja.environment
-----------------
Type
    ``object`` (`name` → `value`)
Example
    .. code:: json

        {
            "variable_start_string": "(((",
            "variable_end_string"  : ")))",
            "keep_trailing_newline": true
        }
Description
    Initialization parameters for the |jinja|
    `Environment <https://jinja.palletsprojects.com/en/stable/api/#jinja2.Environment>`__
    object.


jinja.policies
--------------
Type
    ``object`` (`name` → `value`)
Example
    .. code:: json

        {
            "urlize.rel": "nofollow noopener",
            "ext.i18n.trimmed": true
        }
Description
    |jinja|
    `Policies <https://jinja.palletsprojects.com/en/stable/api/#policies>`__


jinja.filters
-------------
Type
    |Module|_
Description
    A Python |Module|_ containing custom |jinja|
    `filters <https://jinja.palletsprojects.com/en/stable/api/#custom-filters>`__


jinja.tests
-----------
Type
    |Module|_
Description
    A Python |Module|_ containing custom |jinja|
    `tests <https://jinja.palletsprojects.com/en/stable/api/#custom-tests>`__


globals
-------
Type
    |Module|_
Description
    A Python |Module|_ whose namespace,
    in addition to the ``GLOBALS`` dict in
    `util.py <https://github.com/mikf/gallery-dl/blob/v1.27.0/gallery_dl/util.py#L566-L578>`__,
    is used as |globals parameter|__ for compiled Expressions_.

.. |globals parameter| replace:: ``globals`` parameter
.. __: https://docs.python.org/3/library/functions.html#eval



cache.file
----------
Type
    |Path|_
Default
    * (``%APPDATA%`` or ``"~"``) + ``"/gallery-dl/cache.sqlite3"`` on Windows
    * (``$XDG_CACHE_HOME`` or ``"~/.cache"``) + ``"/gallery-dl/cache.sqlite3"`` on all other platforms
Description
    Path of the SQLite3 database used to cache login sessions,
    cookies and API tokens across `gallery-dl` invocations.

    Set this option to ``null`` or an invalid path to disable
    this cache.


filters-environment
-------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Evaluate Expressions_ in a special environment
    preventing them from raising fatal exceptions.

    ``true`` | ``"tryexcept"``
        Wrap expressions in a `try`/`except` block;
        Evaluate expressions raising an exception as ``false``
    ``false`` | ``"raw"``
        Do not wrap expressions in a special environment
    ``"defaultdict"``
        Prevent exceptions when accessing undefined variables
        by using a `defaultdict <https://docs.python.org/3/library/collections.html#collections.defaultdict>`__


format-separator
----------------
Type
    ``string``
Default
    ``"/"``
Description
    Character(s) used as argument separator in `Format String`_
    `format specifiers <formatting.md#format-specifiers>`__.

    For example, setting this option to ``"#"`` would allow a replacement
    operation to be ``Rold#new#`` instead of the default ``Rold/new/``


input-files
-----------
Type
    ``list`` of |Path|_
Example
    ``["~/urls.txt", "$HOME/input"]``
Description
    Additional input files.


signals-ignore
--------------
Type
    ``list`` of ``strings``
Example
    ``["SIGTTOU", "SIGTTIN", "SIGTERM"]``
Description
    The list of signal names to ignore, i.e. set
    `SIG_IGN <https://docs.python.org/3/library/signal.html#signal.SIG_IGN>`_
    as signal handler for.


signals-actions
---------------
Type
    ``object`` (`signal` → `Action(s)`_)
Example
    .. code:: json

        {
            "SIGINT" : "flag download = stop",
            "SIGUSR1": [
                "print Received SIGUSR1",
                "exec notify.sh",
                "exit 127"
            ]
        }
Description
    `Action(s)`_ to perform when a
    `signal <https://docs.python.org/3/library/signal.html>`__
    is received.


subconfigs
----------
Type
    ``list`` of |Path|_
Example
    ``["~/cfg-twitter.json", "~/cfg-reddit.json"]``
Description
    Additional configuration files to load.


warnings
--------
Type
    ``string``
Default
    ``"default"``
Description
    The `Warnings Filter action <https://docs.python.org/3/library/warnings.html#the-warnings-filter>`__
    used for (urllib3) warnings.



API Tokens & IDs
================

All configuration keys listed in this section have fully functional default
values embedded into *gallery-dl* itself, but if things unexpectedly break
or you want to use your own personal client credentials, you can follow these
instructions to get an alternative set of API tokens and IDs.


extractor.deviantart.client-id & .client-secret
-----------------------------------------------
Type
    ``string``
How To
    * login and visit DeviantArt's
      `Applications & Keys <https://www.deviantart.com/developers/apps>`__
      section
    * click "Register Application"
    * scroll to "OAuth2 Redirect URI Whitelist (Required)"
      and enter "https://mikf.github.io/gallery-dl/oauth-redirect.html"
    * scroll to the bottom and agree to the API License Agreement.
      Submission Policy, and Terms of Service.
    * click "Save"
    * copy ``client_id`` and ``client_secret`` of your new
      application and put them in your configuration file
      as ``"client-id"`` and ``"client-secret"``
    * clear your `cache <cache.file_>`__ to delete any remaining
      ``access-token`` entries. (``gallery-dl --clear-cache deviantart``)
    * get a new `refresh-token <extractor.deviantart.refresh-token_>`__ for the
      new ``client-id`` (``gallery-dl oauth:deviantart``)


extractor.flickr.api-key & .api-secret
--------------------------------------
Type
    ``string``
How To
    * login and `Create an App <https://www.flickr.com/services/apps/create/apply/>`__
      in Flickr's `App Garden <https://www.flickr.com/services/>`__
    * click "APPLY FOR A NON-COMMERCIAL KEY"
    * fill out the form with a random name and description
      and click "SUBMIT"
    * copy ``Key`` and ``Secret`` and put them in your configuration file
      as ``"api-key"`` and ``"api-secret"``


extractor.mangadex.client-id & .client-secret
---------------------------------------------
Type
    ``string``
How To
    * login and go to your `User Settings <https://mangadex.org/settings>`__
    * open the "API Clients" section
    * click "``+ Create``"
    * choose a name
    * click "``✔️ Create``"
    * wait for approval / reload the page
    * copy the value after "AUTOAPPROVED ACTIVE" in the form "personal-client-..."
      and put it in your configuration file as ``"client-id"``
    * click "``Get Secret``", then "``Copy Secret``",
      and paste it into your configuration file as ``"client-secret"``


extractor.reddit.client-id & .user-agent
----------------------------------------
Type
    ``string``
How To
    * login and visit the `apps <https://www.reddit.com/prefs/apps/>`__
      section of your account's preferences
    * click the "are you a developer? create an app..." button
    * fill out the form:

      * choose a name
      * select "installed app"
      * set "redirect uri" to http://localhost:6414/
      * solve the "I'm not a robot" challenge if needed
      * click "create app"

    * copy the client id (third line, under your application's name and
      "installed app") and put it in your configuration file
      as ``"client-id"``
    * use "``Python:<application name>:v1.0 (by /u/<username>)``" as
      ``user-agent`` and replace ``<application name>`` and ``<username>``
      accordingly (see Reddit's
      `API access rules <https://github.com/reddit/reddit/wiki/API>`__)
    * clear your `cache <cache.file_>`__ to delete any remaining
      ``access-token`` entries. (``gallery-dl --clear-cache reddit``)
    * get a `refresh-token <extractor.reddit.refresh-token_>`__ for the
      new ``client-id`` (``gallery-dl oauth:reddit``)


extractor.smugmug.api-key & .api-secret
---------------------------------------
Type
    ``string``
How To
    * login and `Apply for an API Key <https://api.smugmug.com/api/developer/apply>`__
    * fill out the form:

      * choose a random name and description
      * set "Type" to "Application"
      * set "Platform" to "All"
      * set "Use" to "Non-Commercial"
      * tick the two checkboxes at the bottom
      * click "Apply"

    * copy ``API Key`` and ``API Secret``
      and put them in your configuration file
      as ``"api-key"`` and ``"api-secret"``


extractor.tumblr.api-key & .api-secret
--------------------------------------
Type
    ``string``
How To
    * login and visit Tumblr's
      `Applications <https://www.tumblr.com/oauth/apps>`__ section
    * click "Register application"
    * fill out the form:

      * choose a random name and description
      * set "Application Website" to https://example.org/
      * set "Default callback URL" to https://example.org/
      * solve the "I'm not a robot" challenge
      * click "Register"

    * click "Show secret key" (below "OAuth Consumer Key")
    * copy your ``OAuth Consumer Key`` and ``Secret Key``
      and put them in your configuration file
      as ``"api-key"`` and ``"api-secret"``



Custom Types
============


Date
----
Type
    * ``string``
    * ``integer``
Example
    * ``"2019-01-01T00:00:00"``
    * ``"2019"`` with ``"%Y"`` as `date-format`_
    * ``1546297200``
Description
    A |Date|_ value represents a specific point in time.

    * If given as ``string``, it is parsed according to `date-format`_.
    * If given as ``integer``, it is interpreted as UTC timestamp.


Duration
--------
Type
    * ``float``
    * ``list`` with 2 ``floats``
    * ``string``
Example
    * ``2.85``
    * ``[1.5, 3.0]``
    * ``"2.85"``, ``"1.5-3.0"``
Description
    A |Duration|_ represents a span of time in seconds.

    * If given as a single ``float``, it will be used as that exact value.
    * If given as a ``list`` with 2 floating-point numbers ``a`` & ``b`` ,
      it will be randomly chosen with uniform distribution such that ``a <= N <= b``.
      (see `random.uniform() <https://docs.python.org/3/library/random.html#random.uniform>`_)
    * If given as a ``string``, it can either represent a single ``float``
      value (``"2.85"``) or a range  (``"1.5-3.0"``).


Module
------
Type
    * ``string``
    * |Path|_
Example
    * ``"gdl_utils"``
    * ``"~/.local/share/gdl/"``
    * ``"~/.local/share/gdl_utils.py"``
Description
    A Python
    `Module <https://docs.python.org/3/glossary.html#term-module>`__

    This can be one of

    * the name of an
      `importable <https://docs.python.org/3/reference/import.html>`__
      Python module
    * the |Path|_ to a Python
      `package <https://docs.python.org/3/glossary.html#term-package>`__
    * the |Path|_ to a `.py` file

    See
    `Python/Modules <https://docs.python.org/3/tutorial/modules.html>`__
    for details.


Path
----
Type
    * ``string``
    * ``list`` of ``strings``
Example
    * ``"file.ext"``
    * ``"~/path/to/file.ext"``
    * ``"$HOME/path/to/file.ext"``
    * ``["$HOME", "path", "to", "file.ext"]``
Description
    A |Path|_ is a ``string`` representing the location of a file
    or directory.

    Simple `tilde expansion <https://docs.python.org/3/library/os.path.html#os.path.expanduser>`__
    and `environment variable expansion <https://docs.python.org/3/library/os.path.html#os.path.expandvars>`__
    is supported.
Note
    In Windows environments,
    both backslashes ``\`` as well as forward slashes ``/``
    can be used as path separators.

    However, since backslashes are JSON's escape character,
    they themselves must be escaped as ``\\``.

    For example, a path like ``C:\path\to\file.ext`` has to be specified as

    * ``"C:\\path\\to\\file.ext"`` when using backslashes
    * ``"C:/path/to/file.ext"`` when using forward slashes

    in a JSON file.


Logging Configuration
---------------------
Type
    ``object``
Example
    .. code:: json

        {
            "format"     : "{asctime} {name}: {message}",
            "format-date": "%H:%M:%S",
            "path"       : "~/log.txt",
            "encoding"   : "ascii"
        }

    .. code:: json

        {
            "level" : "debug",
            "format": {
                "debug"  : "debug: {message}",
                "info"   : "[{name}] {message}",
                "warning": "Warning: {message}",
                "error"  : "ERROR: {message}"
            }
        }

Description
    Extended logging output configuration.

    * format
        * General `Format String`_ for logging messages
          or an ``object`` with `Format Strings`_ for each loglevel.

          In addition to the default
          `LogRecord attributes <https://docs.python.org/3/library/logging.html#logrecord-attributes>`__,
          it is also possible to access the current
          `extractor <https://github.com/mikf/gallery-dl/blob/v1.27.0/gallery_dl/extractor/common.py#L28>`__,
          `job <https://github.com/mikf/gallery-dl/blob/v1.27.0/gallery_dl/job.py#L33>`__,
          `path <https://github.com/mikf/gallery-dl/blob/v1.27.0/gallery_dl/path.py#L27>`__,
          and `keywords` objects and their attributes, for example
          ``"{extractor.url}"``, ``"{path.filename}"``, ``"{keywords.title}"``
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
          (see |open()|_)
        * Default: ``"w"``
    * encoding
        * File encoding
        * Default: ``"utf-8"``
Note
    path, mode, and encoding are only applied when configuring
    logging output to a file.


Postprocessor Configuration
---------------------------
Type
    ``object``
Example
    .. code:: json

        { "name": "mtime" }

    .. code:: json

        {
            "name"       : "zip",
            "compression": "store",
            "extension"  : "cbz",
            "filter"     : "extension not in ('zip', 'rar')",
            "whitelist"  : ["mangadex", "exhentai", "nhentai"]
        }
Description
    An ``object`` containing a ``"name"`` attribute specifying the
    post-processor type, as well as any of its `options <Postprocessor Options_>`__.

    It is possible to set a ``"filter"`` Condition_ similar to
    `image-filter <extractor.*.image-filter_>`_
    to only run a post-processor conditionally.

    It is also possible set a ``"whitelist"`` or ``"blacklist"`` to
    only enable or disable a post-processor for the specified
    extractor categories.

    The available post-processor types are

    ``classify``
        Categorize files by filename extension
    ``compare``
        | Compare versions of the same file and replace/enumerate them on mismatch
        | (requires `downloader.*.part`_ = ``true`` and `extractor.*.skip`_ = ``false``)
    ``directory``
        Reevaluate directory_ `Format Strings`_
    ``exec``
        Execute external commands
    ``hash``
        Compute file hash digests
    ``metadata``
        Write metadata to separate files
    ``mtime``
        Set file modification time according to its metadata
    ``python``
        Call Python functions
    ``rename``
        Rename previously downloaded files
    ``ugoira``
        Convert Pixiv Ugoira to WebM using |ffmpeg|
    ``zip``
        Store files in a ZIP archive


Action
------
Type
    ``string``
Example
    * ``"exit"``
    * ``"print Hello World"``
    * ``"raise AbortExtraction an error occured"``
    * ``"flag file = terminate"``
    * ``["print Exiting", "exit 1"]``
Description
    An Action_ is parsed as `Action Type`
    followed by (optional) arguments:
    ``<type> <arg1> <arg2> …``

    It is possible to specify more than one ``action``
    by providing them as a ``list``: ``["<action1>", "<action2>", …]``

    Supported `Action Types`:

    ``status``:
        | Modify job exit status.
        | Expected syntax is ``<operator> <value>`` (e.g. ``= 100``).

        Supported operators are
        ``=`` (assignment),
        ``&`` (bitwise AND),
        ``|`` (bitwise OR),
        ``^`` (bitwise XOR).
    ``level``:
        | Modify severity level of the current logging message.
        | Can be one of ``debug``, ``info``, ``warning``, ``error`` or an integer value.
        | Use ``0`` to ignore a message (``level = 0``).
    ``print``:
        Write argument to stdout.
    ``exec``:
        Run a shell command.
    ``abort``:
        Stop the current extractor run.
    ``terminate``:
        Stop the current extractor run, including parent extractors.
    ``restart``:
        Restart the current extractor run.
    ``raise``:
        Raise an exception.

        This can be an exception defined in
        `exception.py <https://github.com/mikf/gallery-dl/blob/master/gallery_dl/exception.py>`_
        or a
        `built-in exception <https://docs.python.org/3/library/exceptions.html#exception-hierarchy>`_
        (e.g. ``ZeroDivisionError``)
    ``flag``:
        Set a ``flag``.

        | Expected syntax is ``<flag>[ = <value>]`` (e.g. ``post = stop``)
        | ``<flag>`` can be one of ``file``, ``post``, ``child``, ``download``
        | ``<value>`` can be one of ``stop``, ``abort``, ``terminate``, ``restart`` (default ``stop``)
    ``wait``:
        | Sleep for a given Duration_ or
        | wait until Enter is pressed when no argument was given.
    ``exit``:
        Exit the program with the given argument as exit status.


Expression
----------
Type
    ``string``
Example
    * ``"1 + 2 + 3"``
    * ``"str(id) + '_' + title"``
    * ``"' - '.join(tags[:3]) if tags else 'no tags'"``
Description
    A Python Expression_ is a combination of
    values, variables, operators, and function calls
    that evaluate to a single value.
Reference
    * https://docs.python.org/3/reference/expressions.html


Condition
---------
Type
    * Expression_
    * ``list`` of `Expressions`_
Example
    * ``"not is_watching"``
    * ``"locals().get('optional')"``
    * ``"date >= datetime(2025, 7, 1) or abort()"``
    * ``["width > 800", "0.9 < width/height < 1.1"]``
Description
    A Condition_ is an Expression_
    whose result is evaluated as a |type-bool|_ value.


Format String
-------------
Type
    ``string``
Example
    * ``"foo"``
    * ``"{username}"``
    * ``"{title} ({id}).{extension}"``
    * ``"\fF {title.title()} ({num:>0:>0{len(str(a))}} / {count}).{extension}"``
Description
    A `Format String`_ allows creating dynamic text
    by embedding metadata values directly into replacement fields
    marked by curly braces ``{...}``.
Reference
    * `docs/formatting <formatting_>`__
    * https://docs.python.org/3/library/string.html#formatstrings
    * https://docs.python.org/3/library/string.html#formatspec

.. _formatting: formatting.md


.. |ytdl| replace:: `yt-dlp`_/`youtube-dl`_
.. |ytdl's| replace:: yt-dlp's/youtube-dl's
.. |ffmpeg| replace:: FFmpeg_
.. |jinja| replace:: Jinja

.. |.netrc| replace:: ``.netrc``
.. |requests.request()| replace:: ``requests.request()``
.. |timeout| replace:: ``timeout``
.. |verify| replace:: ``verify``
.. |mature_content| replace:: ``mature_content``
.. |webbrowser.open()| replace:: ``webbrowser.open()``
.. |type-str| replace:: ``str``
.. |type-bool| replace:: ``boolean``
.. |type-datetime| replace:: ``datetime``
.. |datetime.max| replace:: ``datetime.max``
.. |Date| replace:: ``Date``
.. |Duration| replace:: ``Duration``
.. |Module| replace:: ``Module``
.. |Path| replace:: ``Path``
.. |Last-Modified| replace:: ``Last-Modified``
.. |Logging Configuration| replace:: ``Logging Configuration``
.. |Postprocessor Configuration| replace:: ``Postprocessor Configuration``
.. |strptime| replace:: strftime() and strptime() Behavior
.. |postprocessors| replace:: ``postprocessors``
.. |mode: color| replace:: ``"mode": "color"``
.. |open()| replace:: the built-in ``open()`` function
.. |json.dump()| replace:: ``json.dump()``
.. |ISO 639-1| replace:: `ISO 639-1 <https://en.wikipedia.org/wiki/ISO_639-1>`__ language

.. _directory: `extractor.*.directory`_
.. _base-directory: `extractor.*.base-directory`_
.. _date-format: `extractor.*.date-format`_
.. _deviantart.metadata: `extractor.deviantart.metadata`_
.. _deviantart.comments: `extractor.deviantart.comments`_
.. _postprocessors: `extractor.*.postprocessors`_
.. _download archive: `extractor.*.archive`_
.. _Action(s): Action_
.. _Conditions: Condition_
.. _Condition(s): Condition_
.. _Expressions: Expression_
.. _Expression(s): Expression_
.. _Format Strings: `Format String`_
.. _Format String(s): `Format String`_

.. _Conversion(s):      https://gdl-org.github.io/docs/formatting.html#conversions
.. _.netrc:             https://stackoverflow.com/tags/.netrc/info
.. _Last-Modified:      https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.29
.. _type-str:           https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
.. _type-bool:          https://docs.python.org/3/library/stdtypes.html#boolean-type-bool
.. _type-datetime:      https://docs.python.org/3/library/datetime.html#datetime-objects
.. _datetime.max:       https://docs.python.org/3/library/datetime.html#datetime.datetime.max
.. _strptime:           https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
.. _webbrowser.open():  https://docs.python.org/3/library/webbrowser.html
.. _open():             https://docs.python.org/3/library/functions.html#open
.. _json.dump():        https://docs.python.org/3/library/json.html#json.dump
.. _mature_content:     https://www.deviantart.com/developers/http/v1/20160316/object/deviation
.. _Authentication:     https://github.com/mikf/gallery-dl#authentication
.. _OAuth:              https://github.com/mikf/gallery-dl#oauth
.. _youtube-dl:         https://github.com/ytdl-org/youtube-dl
.. _yt-dlp:             https://github.com/yt-dlp/yt-dlp
.. _FFmpeg:             https://www.ffmpeg.org/
.. _requests.request(): https://requests.readthedocs.io/en/master/api/#requests.request
.. _timeout:            https://requests.readthedocs.io/en/master/user/advanced/#timeouts
.. _verify:             https://requests.readthedocs.io/en/master/user/advanced/#ssl-cert-verification
.. _`Requests' proxy documentation`: https://requests.readthedocs.io/en/master/user/advanced/#proxies
