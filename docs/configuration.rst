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
The ``category`` is the lowercase site name without any spaces or special
characters, which is usually just the module name
(``pixiv``, ``danbooru``, ...).
The ``subcategory`` is a lowercase word describing the general functionality
of that extractor (``user``, ``favorite``, ``manga``, ...).

Each one of the following options can be specified on multiple levels of the
configuration tree:

================== =======
Base level:        ``extractor.<option-name>``
Category level:    ``extractor.<category>.<option-name>``
Subcategory level: ``extractor.<category>.<subcategory>.<option-name>``
================== =======

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
Type
    * ``string``
    * ``object`` (`condition` -> `format string`_)
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
    A `format string`_ to build filenames for downloaded files with.

    If this is an ``object``, it must contain Python expressions mapping to the
    filename format strings to use.
    These expressions are evaluated in the order as specified in Python 3.6+
    and in an undetermined order in Python 3.4 and 3.5.

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

    Note: Even if the value of the ``extension`` key is missing or
    ``None``, it will be filled in later when the file download is
    starting. This key is therefore always available to provide
    a valid filename extension.


extractor.*.directory
---------------------
Type
    * ``list`` of ``strings``
    * ``object`` (`condition` -> `format strings`_)
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
    A list of `format strings`_ to build target directory paths with.

    If this is an ``object``, it must contain Python expressions mapping to the
    list of format strings to use.

    Each individual string in such a list represents a single path
    segment, which will be joined together and appended to the
    base-directory_ to form the complete target directory path.


extractor.*.base-directory
--------------------------
Type
    |Path|_
Default
    ``"./gallery-dl/"``
Description
    Directory path used as base for all download destinations.


extractor.*.parent-directory
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Use an extractor's current target directory as
    `base-directory <extractor.*.base-directory_>`__
    for any spawned child extractors.


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
    * ``object`` (`character` -> `replacement character(s)`)
Default
    ``"auto"``
Example
    * ``"/!? (){}"``
    * ``{" ": "_", "/": "-", "|": "-", ":": "_-_", "*": "_+_"}``
Description
    | A string of characters to be replaced with the value of
      `path-replace <extractor.*.path-replace_>`__
    | or an object mapping invalid/unwanted characters to their replacements
    | for generated path segment names.

    Special values:

    * ``"auto"``: Use characters from ``"unix"`` or ``"windows"``
      depending on the local operating system
    * ``"unix"``: ``"/"``
    * ``"windows"``: ``"\\\\|/<>:\"?*"``
    * ``"ascii"``: ``"^0-9A-Za-z_."`` (only ASCII digits, letters, underscores, and dots)
    * ``"ascii+"``: ``"^0-9@-[\\]-{ #-)+-.;=!}~"`` (all ASCII characters except the ones not allowed by Windows)

    Implementation Detail: For ``strings`` with length >= 2, this option uses a
    `Regular Expression Character Set <https://www.regular-expressions.info/charclass.html>`__,
    meaning that:

    * using a caret ``^`` as first character inverts the set
    * character ranges are supported (``0-9a-z``)
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

    Note: In a string with 2 or more characters, ``[]^-\`` need to be
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

    Special values:

    * ``"auto"``: Use characters from ``"unix"`` or ``"windows"``
      depending on the local operating system
    * ``"unix"``: ``""``
    * ``"windows"``: ``". "``


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
    ``object`` (`extension` -> `replacement`)
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
Description
    Controls the behavior when downloading files that have been
    downloaded before, i.e. a file with the same filename already
    exists or its ID is in a `download archive <extractor.*.archive_>`__.

    * ``true``: Skip downloads
    * ``false``: Overwrite already existing files

    * ``"abort"``: Stop the current extractor run
    * ``"abort:N"``: Skip downloads and stop the current extractor run
      after ``N`` consecutive skips

    * ``"terminate"``: Stop the current extractor run, including parent extractors
    * ``"terminate:N"``: Skip downloads and stop the current extractor run,
      including parent extractors, after ``N`` consecutive skips

    * ``"exit"``: Exit the program altogether
    * ``"exit:N"``: Skip downloads and exit the program
      after ``N`` consecutive skips

    * ``"enumerate"``: Add an enumeration index to the beginning of the
      filename extension (``file.1.ext``, ``file.2.ext``, etc.)


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


extractor.*.sleep-request
-------------------------
Type
    |Duration|_
Default
    * ``"0.5-1.5"``
        ``[Danbooru]``, ``[E621]``, ``[foolfuuka]``, ``itaku``,
        ``newgrounds``, ``[philomena]``, ``pixiv:novel``, ``plurk``,
        ``poipiku`` , ``pornpics``, ``soundgasm``, ``urlgalleries``,
        ``vk``, ``zerochan``
    * ``"1.0-2.0"``
        ``flickr``, ``weibo``, ``[wikimedia]``
    * ``"2.0-4.0"``
        ``behance``, ``imagefap``, ``[Nijie]``
    * ``"3.0-6.0"``
        ``exhentai``, ``idolcomplex``, ``[reactor]``, ``readcomiconline``
    * ``"6.0-6.1"``
        ``twibooru``
    * ``"6.0-12.0"``
        ``instagram``
    * ``0``
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

    Specifying username and password is required for

    * ``nijie``
    * ``horne``

    and optional for

    * ``aibooru`` (*)
    * ``aryion``
    * ``atfbooru`` (*)
    * ``bluesky``
    * ``booruvar`` (*)
    * ``coomerparty``
    * ``danbooru`` (*)
    * ``deviantart``
    * ``e621`` (*)
    * ``e6ai`` (*)
    * ``e926`` (*)
    * ``exhentai``
    * ``idolcomplex``
    * ``imgbb``
    * ``inkbunny``
    * ``kemonoparty``
    * ``mangadex``
    * ``mangoxo``
    * ``pillowfort``
    * ``sankaku``
    * ``subscribestar``
    * ``tapas``
    * ``tsumino``
    * ``twitter``
    * ``vipergirls``
    * ``zerochan``

    These values can also be specified via the
    ``-u/--username`` and ``-p/--password`` command-line options or
    by using a |.netrc|_ file. (see Authentication_)

    (*) The password value for these sites should be
    the API key found in your user profile, not the actual account password.

    Note: Leave the ``password`` value empty or undefined
    to be prompted for a passeword when performing a login
    (see `getpass() <https://docs.python.org/3/library/getpass.html#getpass.getpass>`__).


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
    * ``object`` (`name` -> `value`)
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
      * The optional fourth entry is a (Firefox) container name (``"none"`` for only cookies with no container)
      * The optional fifth entry is the domain to extract cookies for. Prefix it with a dot ``.`` to include cookies for subdomains. Has no effect when also specifying a container.

      .. code:: json

        ["firefox"]
        ["firefox", null, null, "Personal"]
        ["chromium", "Private", "kwallet", null, ".twitter.com"]


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
    * ``object`` (`scheme` -> `proxy`)
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

    Note: If a proxy URLs does not include a scheme,
    ``http://`` is assumed.


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
    ``"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"``
Description
    User-Agent header value to be used for HTTP requests.

    Setting this value to ``"browser"`` will try to automatically detect
    and use the User-Agent used by the system's default browser.

    Note: This option has no effect on
    `pixiv`, `e621`, and `mangadex`
    extractors, as these need specific values to function correctly.


extractor.*.browser
-------------------
Type
    ``string``
Default
    * ``"firefox"``: ``artstation``, ``mangasee``, ``patreon``, ``pixiv:series``, ``twitter``
    * ``null``: otherwise
Example
    * ``"chrome:macos"``
Description
    Try to emulate a real browser (``firefox`` or ``chrome``)
    by using their default HTTP headers and TLS ciphers for HTTP requests.

    Optionally, the operating system used in the ``User-Agent`` header can be
    specified after a ``:`` (``windows``, ``linux``, or ``macos``).

    Note: ``requests`` and ``urllib3`` only support HTTP/1.1, while a real
    browser would use HTTP/2.


extractor.*.referer
-------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Send `Referer <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referer>`__
    headers with all outgoing HTTP requests.

    If this is a ``string``, send it as Referer
    instead of the extractor's ``root`` domain.


extractor.*.headers
-------------------
Type
    ``object`` (`name` -> `value`)
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


extractor.*.ciphers
-------------------
Type
    ``list`` of ``strings``
Example
    .. code:: json

      ["ECDHE-ECDSA-AES128-GCM-SHA256",
       "ECDHE-RSA-AES128-GCM-SHA256",
       "ECDHE-ECDSA-CHACHA20-POLY1305",
       "ECDHE-RSA-CHACHA20-POLY1305"]

Description
    List of TLS/SSL cipher suites in
    `OpenSSL cipher list format <https://www.openssl.org/docs/manmaster/man1/openssl-ciphers.html>`__
    to be passed to
    `ssl.SSLContext.set_ciphers() <https://docs.python.org/3/library/ssl.html#ssl.SSLContext.set_ciphers>`__


extractor.*.tls12
-----------------
Type
    ``bool``
Default
    * ``false``: ``patreon``, ``pixiv:series``
    * ``true``: otherwise
Description
    Allow selecting TLS 1.2 cipher suites.

    Can be disabled to alter TLS fingerprints
    and potentially bypass Cloudflare blocks.


extractor.*.keywords
--------------------
Type
    ``object`` (`name` -> `value`)
Example
    ``{"type": "Pixel Art", "type_id": 123}``
Description
    Additional name-value pairs to be added to each metadata dictionary.


extractor.*.keywords-default
----------------------------
Type
    any
Default
    ``"None"``
Description
    Default value used for missing or undefined keyword names in
    `format strings`_.


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
    `PathFormat <https://github.com/mikf/gallery-dl/blob/v1.24.2/gallery_dl/path.py#L27>`__
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
    `Extractor <https://github.com/mikf/gallery-dl/blob/v1.26.2/gallery_dl/extractor/common.py#L26>`__
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

    Note: Any ``blacklist`` setting will automatically include
    ``"oauth"``, ``"recursive"``, and ``"test"``.


extractor.*.archive
-------------------
Type
    |Path|_
Default
    ``null``
Example
    ``"$HOME/.archives/{category}.sqlite3"``
Description
    File to store IDs of downloaded files in. Downloads of files
    already recorded in this archive file will be
    `skipped <extractor.*.skip_>`__.

    The resulting archive file is not a plain text file but an SQLite3
    database, as either lookup operations are significantly faster or
    memory requirements are significantly lower when the
    amount of stored IDs gets reasonably large.

    Note: Archive files that do not already exist get generated automatically.

    Note: Archive paths support regular `format string`_ replacements,
    but be aware that using external inputs for building local paths
    may pose a security risk.


extractor.*.archive-format
--------------------------
Type
    ``string``
Example
    ``"{id}_{offset}"``
Description
    An alternative `format string`_ to build archive IDs with.


extractor.*.archive-prefix
--------------------------
Type
    ``string``
Default
    ``"{category}"``
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

    See `<https://www.sqlite.org/pragma.html>`__
    for available ``PRAGMA`` statements and further details.


extractor.*.actions
-------------------
Type
    * ``object`` (`pattern` -> `action`)
    * ``list`` of ``lists`` with 2 ``strings`` as elements
Example
    .. code:: json

        {
            "error"                   : "status |= 1",
            "warning:(?i)unable to .+": "exit 127",
            "info:Logging in as .+"   : "level = debug"
        }

    .. code:: json

        [
            ["error"                   , "status |= 1"  ],
            ["warning:(?i)unable to .+", "exit 127"     ],
            ["info:Logging in as .+"   , "level = debug"]
        ]

Description
    Perform an ``action`` when logging a message matched by ``pattern``.

    ``pattern`` is parsed as severity level (``debug``, ``info``, ``warning``, ``error``, or integer value)
    followed by an optional `Python Regular Expression <https://docs.python.org/3/library/re.html#regular-expression-syntax>`__
    separated by a colon ``:``.
    Using ``*`` as `level` or leaving it empty
    matches logging messages of all levels
    (e.g. ``*:<re>`` or ``:<re>``).

    ``action`` is parsed as action type
    followed by (optional) arguments.

    Supported Action Types:

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
    ``print``
        Write argument to stdout.
    ``restart``:
        Restart the current extractor run.
    ``wait``:
        Stop execution until Enter is pressed.
    ``exit``:
        Exit the program with the given argument as exit status.


extractor.*.postprocessors
--------------------------
Type
    ``list`` of |Postprocessor Configuration|_ objects
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
    ``object`` (`name` -> `value`)
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
Examples
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

    Note: The index of the first file is ``1``.


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
    * ``string``
    * ``list`` of ``strings``
Examples
    * ``"re.search(r'foo(bar)+', description)"``
    * ``["width >= 1200", "width/height > 1.2"]``
Description
    Python expression controlling which files to download.

    A file only gets downloaded when *all* of the given expressions evaluate to ``True``.

    Available values are the filename-specific ones listed by ``-K`` or ``-j``.


extractor.*.chapter-filter
--------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Examples
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

    Note: Despite its name, this option does **not** control how
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

    Special values:

    * ``"all"``: Include HTTP request and response headers. Hide ``Authorization``, ``Cookie``, and ``Set-Cookie`` values.
    * ``"ALL"``: Include all HTTP request and response headers.



Extractor-specific Options
==========================


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


extractor.artstation.previews
-----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download video previews.


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

    * ``true``: Start on users' main gallery pages and recursively
      descend into subfolders
    * ``false``: Get posts from "Latest Updates" pages


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

    Supported module types are
    ``image``, ``video``, ``mediacollection``, ``embed``, ``text``.


extractor.blogger.videos
------------------------
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
    ``"media"``
Example
    * ``"avatar,background,posts"``
    * ``["avatar", "background", "posts"]``
Description
    A (comma-separated) list of subcategories to include
    when processing a user profile.

    Possible values are
    ``"avatar"``,
    ``"background"``,
    ``"posts"``,
    ``"replies"``,
    ``"media"``,
    ``"likes"``,

    It is possible to use ``"all"`` instead of listing all values separately.


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

    * ``facets``: ``hashtags``, ``mentions``, and ``uris``
    * ``user``: detailed ``user`` metadata for the user referenced in the input URL
      (See `app.bsky.actor.getProfile <https://www.docs.bsky.app/docs/api/app-bsky-actor-get-profile>`__).



extractor.bluesky.post.depth
----------------------------
Type
    ``integer``
Default
    ``0``
Description
    Sets the maximum depth of returned reply posts.

    (See `depth` parameter of `app.bsky.feed.getPostThread <https://www.docs.bsky.app/docs/api/app-bsky-feed-get-post-thread>`__)


extractor.bluesky.reposts
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Process reposts.


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


extractor.danbooru.external
---------------------------
Type
    ``bool``
Default
    ``false``
Description
    For unavailable or restricted posts,
    follow the ``source`` and download from there if possible.


extractor.danbooru.ugoira
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Controls the download target for Ugoira posts.

    * ``true``: Original ZIP archives
    * ``false``: Converted video files


extractor.[Danbooru].metadata
-----------------------------
Type
    * ``bool``
    * ``string``
    * ``list`` of ``strings``
Default
    ``false``
Example
    * ``replacements,comments,ai_tags``
    * ``["replacements", "comments", "ai_tags"]``
Description
    Extract additional metadata
    (notes, artist commentary, parent, children, uploader)

    It is possible to specify a custom list of metadata includes.
    See `available_includes <https://github.com/danbooru/danbooru/blob/2cf7baaf6c5003c1a174a8f2d53db010cf05dca7/app/models/post.rb#L1842-L1849>`__
    for possible field names. ``aibooru`` also supports ``ai_metadata``.

    Note: This requires 1 additional HTTP request per 200-post batch.


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

    Note: Changing this setting is normally not necessary. When the value is
    greater than the per-page limit, gallery-dl will stop after the first
    batch. The value cannot be less than 1.


extractor.derpibooru.api-key
----------------------------
Type
    ``string``
Default
    ``null``
Description
    Your `Derpibooru API Key <https://derpibooru.org/registrations/edit>`__,
    to use your account's browsing settings and filters.


extractor.derpibooru.filter
---------------------------
Type
    ``integer``
Default
    ``56027`` (`Everything <https://derpibooru.org/filters/56027>`_ filter)
Description
    The content filter ID to use.

    Setting an explicit filter ID overrides any default filters and can be used
    to access 18+ content without `API Key <extractor.derpibooru.api-key_>`_.

    See `Filters <https://derpibooru.org/filters>`_ for details.


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

    Note: Enabling this option also enables deviantart.comments_.


extractor.deviantart.extra
--------------------------
Type
    ``bool``
Default
    ``false``
Description
    Download extra Sta.sh resources from
    description texts and journals.

    Note: Enabling this option also enables deviantart.metadata_.


extractor.deviantart.flat
-------------------------
Type
    ``bool``
Default
    ``true``
Description
    Select the directory structure created by the Gallery- and
    Favorite-Extractors.

    * ``true``: Use a flat directory structure.
    * ``false``: Collect a list of all gallery-folders or
      favorites-collections and transfer any further work to other
      extractors (``folder`` or ``collection``), which will then
      create individual subdirectories for each of them.

      Note: Going through all gallery folders will not be able to
      fetch deviations which aren't in any folder.


extractor.deviantart.folders
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Provide a ``folders`` metadata field that contains the names of all
    folders a deviation is present in.

    Note: Gathering this information requires a lot of API calls.
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

    Special values:

    * ``"skip"``: Skip groups


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

    Possible values are
    ``"avatar"``,
    ``"background"``,
    ``"gallery"``,
    ``"scraps"``,
    ``"journal"``,
    ``"favorite"``,
    ``"status"``.

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

    * ``"html"``: HTML with (roughly) the same layout as on DeviantArt.
    * ``"text"``: Plain text with image references and HTML tags removed.
    * ``"none"``: Don't download textual content.


extractor.deviantart.jwt
------------------------
Type
    ``bool``
Default
    ``false``
Description
    Update `JSON Web Tokens <https://jwt.io/>`__ (the ``token`` URL parameter)
    of otherwise non-downloadable, low-resolution images
    to be able to download them in full resolution.

    Note: No longer functional as of 2023-10-11


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

    * ``camera``     : EXIF information (if available)
    * ``stats``      : deviation statistics
    * ``submission`` : submission information
    * ``collection`` : favourited folder information (requires a `refresh token <extractor.deviantart.refresh-token_>`__)
    * ``gallery``    : gallery folder information (requires a `refresh token <extractor.deviantart.refresh-token_>`__)

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
    everything else (archives, etc.).


extractor.deviantart.pagination
-------------------------------
Type
    ``string``
Default
    ``"api"``
Description
    Controls when to stop paginating over API results.

    * ``"api"``: Trust the API and stop when ``has_more`` is ``false``.
    * ``"manual"``: Disregard ``has_more`` and only stop when a batch of results is empty.


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

    Note: The ``refresh-token`` becomes invalid
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

    Note: This requires 0-2 additional HTTP requests per post.


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

    Note: Changing this setting is normally not necessary. When the value is
    greater than the per-page limit, gallery-dl will stop after the first
    batch. The value cannot be less than 1.


extractor.exhentai.domain
-------------------------
Type
    ``string``
Default
    ``"auto"``
Description
    * ``"auto"``: Use ``e-hentai.org`` or ``exhentai.org``
      depending on the input URL
    * ``"e-hentai.org"``: Use ``e-hentai.org`` for all URLs
    * ``"exhentai.org"``: Use ``exhentai.org`` for all URLs


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

    Note: Set this to `"favdel"` to remove galleries from your favorites.

    Note: This will remove any Favorite Notes when applied
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
    Sets a custom image download limit and
    stops extraction when it gets exceeded.


extractor.exhentai.metadata
---------------------------
Type
    ``bool``
Default
    ``false``
Description
    Load extended gallery metadata from the
    `API <https://ehwiki.org/wiki/API#Gallery_Metadata>`_.

    Adds ``archiver_key``, ``posted``, and ``torrents``.
    Makes ``date`` and ``filesize`` more precise.


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

    * ``"hitomi"``:  Download the corresponding gallery from ``hitomi.la``


extractor.fanbox.embeds
-----------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Control behavior on embedded content from external sites.

    * ``true``: Extract embed URLs and download them if supported
      (videos are not downloaded).
    * ``"ytdl"``: Like ``true``, but let `youtube-dl`_ handle video
      extraction and download for YouTube, Vimeo and SoundCloud embeds.
    * ``false``: Ignore embeds.


extractor.fanbox.metadata
-------------------------
Type
    * ``bool``
    * ``string``
    * ``list`` of ``strings``
Default
    ``false``
Example
    * ``user,plan``
    * ``["user", "plan"]``
Description
    Extract ``plan`` and extended ``user`` metadata.


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

    Note: This requires 1 additional API call per photo.
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

    Note: This requires 1 additional API call per photo.
    See `flickr.photos.getExif <https://www.flickr.com/services/api/flickr.photos.getExif.html>`__ for details.


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

    * ``"text"``: Plain text with HTML tags removed
    * ``"html"``: Raw HTML content


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

    Possible values are
    ``"gallery"``, ``"scraps"``, ``"favorite"``.

    It is possible to use ``"all"`` instead of listing all values separately.


extractor.furaffinity.layout
----------------------------
Type
    ``string``
Default
    ``"auto"``
Description
    Selects which site layout to expect when parsing posts.

    * ``"auto"``: Automatically differentiate between ``"old"`` and ``"new"``
    * ``"old"``: Expect the *old* site layout
    * ``"new"``: Expect the *new* site layout


extractor.gelbooru.api-key & .user-id
-------------------------------------
Type
    ``string``
Default
    ``null``
Description
    Values from the API Access Credentials section found at the bottom of your
    `Account Options <https://gelbooru.com/index.php?page=account&s=options>`__
    page.


extractor.gelbooru.favorite.order-posts
---------------------------------------
Type
    ``string``
Default
    ``"desc"``
Description
    Controls the order in which favorited posts are returned.

    * ``"asc"``: Ascending favorite date order (oldest first)
    * ``"desc"``: Descending favorite date order (newest first)
    * ``"reverse"``: Same as ``"asc"``


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

    Possible values are
    ``"pictures"``, ``"scraps"``, ``"stories"``, ``"favorite"``.

    It is possible to use ``"all"`` instead of listing all values separately.


extractor.hitomi.format
-----------------------
Type
    ``string``
Default
    ``"webp"``
Description
    Selects which image format to download.

    Available formats are ``"webp"`` and ``"avif"``.

    ``"original"`` will try to download the original ``jpg`` or ``png`` versions,
    but is most likely going to fail with ``403 Forbidden`` errors.


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

    * ``true``: Follow Imgur's advice and choose MP4 if the
      ``prefer_video`` flag in an image's metadata is set.
    * ``false``: Always choose GIF.
    * ``"always"``: Always choose MP4.


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

    * ``"rest"``: REST API - higher-resolution media
    * ``"graphql"``: GraphQL API - lower-resolution media


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

    Possible values are
    ``"posts"``,
    ``"reels"``,
    ``"tagged"``,
    ``"stories"``,
    ``"highlights"``,
    ``"avatar"``.

    It is possible to use ``"all"`` instead of listing all values separately.


extractor.instagram.metadata
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Provide extended ``user`` metadata even when referring to a user by ID,
    e.g. ``instagram.com/id:12345678``.

    Note: This metadata is always available when referring to a user by name,
    e.g. ``instagram.com/USERNAME``.


extractor.instagram.order-files
-------------------------------
Type
    ``string``
Default
    ``"asc"``
Description
    Controls the order in which files of each post are returned.

    * ``"asc"``: Same order as displayed in a post
    * ``"desc"``: Reverse order as displayed in a post
    * ``"reverse"``: Same as ``"desc"``

    Note: This option does *not* affect ``{num}``.
    To enumerate files in reverse order, use ``count - num + 1``.


extractor.instagram.order-posts
-------------------------------
Type
    ``string``
Default
    ``"asc"``
Description
    Controls the order in which posts are returned.

    * ``"asc"``: Same order as displayed
    * ``"desc"``: Reverse order as displayed
    * ``"id"`` or ``"id_asc"``: Ascending order by ID
    * ``"id_desc"``: Descending order by ID
    * ``"reverse"``: Same as ``"desc"``

    Note: This option only affects ``highlights``.


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
    ``bool``
Default
    ``true``
Description
    Download video files.


extractor.itaku.videos
----------------------
Type
    ``bool``
Default
    ``true``
Description
    Download video files.


extractor.kemonoparty.comments
------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract ``comments`` metadata.

    Note: This requires 1 additional HTTP request per post.


extractor.kemonoparty.duplicates
--------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Controls how to handle duplicate files in a post.

    * ``true``: Download duplicates
    * ``false``: Ignore duplicates


extractor.kemonoparty.dms
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract a user's direct messages as ``dms`` metadata.


extractor.kemonoparty.announcements
-----------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract a user's announcements as ``announcements`` metadata.


extractor.kemonoparty.favorites
-------------------------------
Type
    ``string``
Default
    ``artist``
Description
    Determines the type of favorites to be downloaded.

    Available types are ``artist``, and ``post``.


extractor.kemonoparty.files
---------------------------
Type
    ``list`` of ``strings``
Default
    ``["attachments", "file", "inline"]``
Description
    Determines the type and order of files to be downloaded.

    Available types are ``file``, ``attachments``, and ``inline``.


extractor.kemonoparty.max-posts
-------------------------------
Type
    ``integer``
Default
    ``null``
Description
    Limit the number of posts to download.


extractor.kemonoparty.metadata
------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract ``username`` metadata.


extractor.kemonoparty.revisions
-------------------------------
Type
    * ``bool``
    * ``string``
Default
    ``false``
Description
    Extract post revisions.

    Set this to ``"unique"`` to filter out duplicate revisions.

    Note: This requires 1 additional HTTP request per post.


extractor.kemonoparty.order-revisions
-------------------------------------
Type
    ``string``
Default
    ``"desc"``
Description
    Controls the order in which
    `revisions <extractor.kemonoparty.revisions_>`__
    are returned.

    * ``"asc"``: Ascending order (oldest first)
    * ``"desc"``: Descending order (newest first)
    * ``"reverse"``: Same as ``"asc"``


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
    ``object`` (`name` -> `value`)
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
    `ISO 639-1 <https://en.wikipedia.org/wiki/ISO_639-1>`__ language codes
    to filter chapters by.


extractor.mangadex.ratings
--------------------------
Type
    ``list`` of ``strings``
Default
    ``["safe", "suggestive", "erotica", "pornographic"]``
Description
    List of acceptable content ratings for returned chapters.


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

    Note: gallery-dl comes with built-in tokens for ``mastodon.social``,
    ``pawoo`` and ``baraag``. For other instances, you need to obtain an
    ``access-token`` in order to use usernames in place of numerical
    user IDs.


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

    Note: Not supported by all ``moebooru`` instances.


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
    ``string``
Default
    ``"original"``
Example
    ``"720p"``
Description
    Selects the preferred format for video downloads.

    If the selected format is not available,
    the next smaller one gets chosen.


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

    Possible values are
    ``"art"``, ``"audio"``, ``"games"``, ``"movies"``.

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

    Possible values are
    ``"illustration"``, ``"doujin"``, ``"favorite"``, ``"nuita"``.

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

    * ``true``: Download videos
    * ``"ytdl"``: Download videos using `youtube-dl`_
    * ``false``: Skip video Tweets


extractor.oauth.browser
-----------------------
Type
    ``bool``
Default
    ``true``
Description
    Controls how a user is directed to an OAuth authorization page.

    * ``true``: Use Python's |webbrowser.open()|_ method to automatically
      open the URL in the user's default browser.
    * ``false``: Ask the user to copy & paste an URL from the terminal.


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

    Note: All redirects will go to port ``6414``, regardless
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

    Note: This requires 1 additional HTTP request per post.


extractor.patreon.files
-----------------------
Type
    ``list`` of ``strings``
Default
    ``["images", "image_large", "attachments", "postfile", "content"]``
Description
    Determines the type and order of files to be downloaded.

    Available types are
    ``postfile``, ``images``, ``image_large``, ``attachments``, and ``content``.


extractor.photobucket.subalbums
-------------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download subalbums.


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

    Possible values are
    ``"artworks"``,
    ``"avatar"``,
    ``"background"``,
    ``"favorite"``,
    ``"novel-user"``,
    ``"novel-bookmark"``.

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


extractor.pixiv.embeds
----------------------
Type
    ``bool``
Default
    ``false``
Description
    Download images embedded in novels.


extractor.pixiv.novel.full-series
---------------------------------
Type
    ``bool``
Default
    ``false``
Description
    When downloading a novel being part of a series,
    download all novels of that series.


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

    Note: This requires 1 additional API call per bookmarked post.


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
    ``bool``
Default
    ``true``
Description
    Download Pixiv's Ugoira animations or ignore them.

    These animations come as a ``.zip`` file containing all
    animation frames in JPEG format.

    Use an `ugoira` post processor to convert them
    to watchable videos. (Example__)

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

    * ``"stop``: Stop the current extractor run.
    * ``"wait``: Ask the user to solve the CAPTCHA and wait.


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

    Note: This requires 1 additional API call for every 100 extra comments.


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

    Special values:

    * ``0``: Recursion is disabled
    * ``-1``: Infinite recursion (don't do this)


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


extractor.reddit.videos
-----------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    Control video download behavior.

    * ``true``: Download videos and use `youtube-dl`_ to handle
      HLS and DASH manifests
    * ``"ytdl"``: Download videos and let `youtube-dl`_ handle all of
      video extraction and download
    * ``"dash"``: Extract DASH manifest URLs and use `youtube-dl`_
      to download and merge them. (*)
    * ``false``: Ignore videos

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
    List of names of the preferred animation format, which can be
    ``"hd"``,
    ``"sd"``,
    ``"gif"``,
    ``"thumbnail"``,
    ``"vthumbnail"``, or
    ``"poster"``.

    If a selected format is not available, the next one in the list will be
    tried until an available format is found.

    If the format is given as ``string``, it will be extended with
    ``["hd", "sd", "gif"]``. Use a list with one element to
    restrict it to only one possible format.


extractor.sankaku.id-format
---------------------------
Type
    ``string``
Default
    ``"numeric"``
Description
    Format of ``id`` metadata fields.

    * ``"alphanumeric"`` or ``"alnum"``: 11-character alphanumeric IDs (``y0abGlDOr2o``)
    * ``"numeric"`` or ``"legacy"``: numeric IDs (``360451``)


extractor.sankaku.refresh
-------------------------
Type
    ``bool``
Default
    ``false``
Description
    Refresh download URLs before they expire.


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


extractor.skeb.article
----------------------
Type
    ``bool``
Default
    ``false``
Description
    Download article images.


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
    Include animated assets when downloading from a list of assets.


extractor.steamgriddb.epilepsy
------------------------------
Type
    ``bool``
Default
    ``true``
Description
    Include assets tagged with epilepsy when downloading from a list of assets.


extractor.steamgriddb.dimensions
--------------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"all"``
Examples
    * ``"1024x512,512x512"``
    * ``["460x215", "920x430"]``
Description
    Only include assets that are in the specified dimensions. ``all`` can be
    used to specify all dimensions. Valid values are:

    * Grids: ``460x215``, ``920x430``, ``600x900``, ``342x482``, ``660x930``,
      ``512x512``, ``1024x1024``
    * Heroes: ``1920x620``, ``3840x1240``, ``1600x650``
    * Logos: N/A (will be ignored)
    * Icons: ``8x8``, ``10x10``, ``14x14``, ``16x16``, ``20x20``, ``24x24``,
      ``28x28``, ``32x32``, ``35x35``, ``40x40``, ``48x48``, ``54x54``,
      ``56x56``, ``57x57``, ``60x60``, ``64x64``, ``72x72``, ``76x76``,
      ``80x80``, ``90x90``, ``96x96``, ``100x100``, ``114x114``, ``120x120``,
      ``128x128``, ``144x144``, ``150x150``, ``152x152``, ``160x160``,
      ``180x180``, ``192x192``, ``194x194``, ``256x256``, ``310x310``,
      ``512x512``, ``768x768``, ``1024x1024``


extractor.steamgriddb.file-types
--------------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"all"``
Examples
    * ``"png,jpeg"``
    * ``["jpeg", "webp"]``
Description
    Only include assets that are in the specified file types. ``all`` can be
    used to specify all file types. Valid values are:

    * Grids: ``png``, ``jpeg``, ``jpg``, ``webp``
    * Heroes: ``png``, ``jpeg``, ``jpg``, ``webp``
    * Logos: ``png``, ``webp``
    * Icons: ``png``, ``ico``


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
    Include assets tagged with humor when downloading from a list of assets.


extractor.steamgriddb.languages
-------------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Default
    ``"all"``
Examples
    * ``"en,km"``
    * ``["fr", "it"]``
Description
    Only include assets that are in the specified languages. ``all`` can be
    used to specify all languages. Valid values are `ISO 639-1 <https://en.wikipedia.org/wiki/ISO_639-1>`__
    language codes.


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
    ``score_desc``
Description
    Set the chosen sorting method when downloading from a list of assets. Can be one of:

    * ``score_desc`` (Highest Score (Beta))
    * ``score_asc`` (Lowest Score (Beta))
    * ``score_old_desc`` (Highest Score (Old))
    * ``score_old_asc`` (Lowest Score (Old))
    * ``age_desc`` (Newest First)
    * ``age_asc`` (Oldest First)


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
    ``all``
Examples
    * ``white,black``
    * ``["no_logo", "white_logo"]``
Description
    Only include assets that are in the specified styles. ``all`` can be used
    to specify all styles. Valid values are:

    * Grids: ``alternate``, ``blurred``, ``no_logo``, ``material``, ``white_logo``
    * Heroes: ``alternate``, ``blurred``, ``material``
    * Logos: ``official``, ``white``, ``black``, ``custom``
    * Icons: ``official``, ``custom``


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


extractor.tumblr.ratelimit
--------------------------
Type
    ``string``
Default
    ``"abort"``
Description
    Selects how to handle exceeding the daily API rate limit.

    * ``"abort"``: Raise an error and stop extraction
    * ``"wait"``: Wait until rate limit reset


extractor.tumblr.reblogs
------------------------
Type
    * ``bool``
    * ``string``
Default
    ``true``
Description
    * ``true``: Extract media from reblogged posts
    * ``false``: Skip reblogged posts
    * ``"same-blog"``: Skip reblogged posts unless the original post
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

    * ``false``: Ignore cards
    * ``true``: Download image content from supported cards
    * ``"ytdl"``: Additionally download video content from unsupported cards using `youtube-dl`_


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

    * ``"auto"``: Always auto-generate a token.
    * ``"cookies"``: Use token given by the ``ct0`` cookie if present.


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

    Note: This requires at least 1 additional API call per initial Tweet.


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

    Possible values are
    ``"avatar"``,
    ``"background"``,
    ``"timeline"``,
    ``"tweets"``,
    ``"media"``,
    ``"replies"``,
    ``"likes"``.

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

    * ``"restid"``: ``/TweetResultByRestId`` - accessible to guest users
    * ``"detail"``: ``/TweetDetail`` - more stable
    * ``"auto"``: ``"detail"`` when logged in, ``"restid"`` otherwise


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
    ``4096x4096``, ``orig``, ``large``, ``medium``, and ``small``.


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

    * ``"abort"``: Raise an error and stop extraction
    * ``"wait"``: Wait until rate limit reset


extractor.twitter.locked
------------------------
Type
    ``string``
Default
    ``"abort"``
Description
    Selects how to handle "account is temporarily locked" errors.

    * ``"abort"``: Raise an error and stop extraction
    * ``"wait"``: Wait until the account is unlocked and retry


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

    Note: Twitter will automatically expand conversations if you
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


extractor.twitter.timeline.strategy
-----------------------------------
Type
    ``string``
Default
    ``"auto"``
Description
    Controls the strategy / tweet source used for timeline URLs
    (``https://twitter.com/USER/timeline``).

    * ``"tweets"``: `/tweets <https://twitter.com/USER/tweets>`__ timeline + search
    * ``"media"``: `/media <https://twitter.com/USER/media>`__ timeline + search
    * ``"with_replies"``: `/with_replies <https://twitter.com/USER/with_replies>`__ timeline + search
    * ``"auto"``: ``"tweets"`` or ``"media"``, depending on `retweets <extractor.twitter.retweets_>`__ and `text-tweets <extractor.twitter.text-tweets_>`__ settings


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


extractor.twitter.users
-----------------------
Type
    ``string``
Default
    ``"user"``
Example
    ``"https://twitter.com/search?q=from:{legacy[screen_name]}"``
Description
    | Format string for user URLs generated from
      ``following`` and ``list-members`` queries,
    | whose replacement field values come from Twitter ``user`` objects
      (`Example <https://gist.githubusercontent.com/mikf/99d2719b3845023326c7a4b6fb88dd04/raw/275b4f0541a2c7dc0a86d3998f7d253e8f10a588/github.json>`_)

    Special values:

    * ``"user"``: ``https://twitter.com/i/user/{rest_id}``
    * ``"timeline"``: ``https://twitter.com/id:{rest_id}/timeline``
    * ``"tweets"``: ``https://twitter.com/id:{rest_id}/tweets``
    * ``"media"``: ``https://twitter.com/id:{rest_id}/media``

    Note: To allow gallery-dl to follow custom URL formats, set the blacklist__
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

    * ``true``: Download videos
    * ``"ytdl"``: Download videos using `youtube-dl`_
    * ``false``: Skip video Tweets


extractor.unsplash.format
-------------------------
Type
    ``string``
Default
    ``"raw"``
Description
    Name of the image format to download.

    Available formats are
    ``"raw"``, ``"full"``, ``"regular"``, ``"small"``, and ``"thumb"``.


extractor.vipergirls.domain
---------------------------
Type
    ``string``
Default
    ``"vipergirls.to"``
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

    Note: Requires `login <extractor.*.username & .password_>`__
    or `cookies <extractor.*.cookies_>`__


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

    Possible values are
    ``"uploads"``, ``"collections"``.

    It is possible to use ``"all"`` instead of listing all values separately.


extractor.wallhaven.metadata
----------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract additional metadata (tags, uploader)

    Note: This requires 1 additional HTTP request per post.


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

    Note: This requires 1 additional HTTP request per submission.


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

    Possible values are
    ``"home"``,
    ``"feed"``,
    ``"videos"``,
    ``"newvideo"``,
    ``"article"``,
    ``"album"``.

    It is possible to use ``"all"`` instead of listing all values separately.


extractor.weibo.livephoto
-------------------------
Type
    ``bool``
Default
    ``true``
Description
    Download ``livephoto`` files.


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


extractor.weibo.videos
----------------------
Type
    ``bool``
Default
    ``true``
Description
    Download video files.


extractor.ytdl.enabled
----------------------
Type
    ``bool``
Default
    ``false``
Description
    Match **all** URLs, even ones without a ``ytdl:`` prefix.


extractor.ytdl.format
---------------------
Type
    ``string``
Default
    youtube-dl's default, currently ``"bestvideo+bestaudio/best"``
Description
    Video `format selection
    <https://github.com/ytdl-org/youtube-dl#format-selection>`__
    directly passed to youtube-dl.


extractor.ytdl.generic
----------------------
Type
    ``bool``
Default
    ``true``
Description
    Controls the use of youtube-dl's generic extractor.

    Set this option to ``"force"`` for the same effect as youtube-dl's
    ``--force-generic-extractor``.


extractor.ytdl.logging
----------------------
Type
    ``bool``
Default
    ``true``
Description
    Route youtube-dl's output through gallery-dl's logging system.
    Otherwise youtube-dl will write its output directly to stdout/stderr.

    Note: Set ``quiet`` and ``no_warnings`` in
    `extractor.ytdl.raw-options`_ to ``true`` to suppress all output.


extractor.ytdl.module
---------------------
Type
    ``string``
Default
    ``null``
Description
    Name of the youtube-dl Python module to import.

    Setting this to ``null`` will try to import ``"yt_dlp"``
    followed by ``"youtube_dl"`` as fallback.


extractor.ytdl.raw-options
--------------------------
Type
    ``object`` (`name` -> `value`)
Example
    .. code:: json

        {
            "quiet": true,
            "writesubtitles": true,
            "merge_output_format": "mkv"
        }

Description
    Additional options passed directly to the ``YoutubeDL`` constructor.

    All available options can be found in `youtube-dl's docstrings
    <https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L138-L318>`__.


extractor.ytdl.cmdline-args
---------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Example
    * ``"--quiet --write-sub --merge-output-format mkv"``
    * ``["--quiet", "--write-sub", "--merge-output-format", "mkv"]``
Description
    Additional options specified as youtube-dl command-line arguments.


extractor.ytdl.config-file
--------------------------
Type
    |Path|_
Example
    ``"~/.config/youtube-dl/config"``
Description
    Location of a youtube-dl configuration file to load options from.


extractor.zerochan.metadata
---------------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract additional metadata (date, md5, tags, ...)

    Note: This requires 1-2 additional HTTP requests per post.


extractor.zerochan.pagination
-----------------------------
Type
    ``string``
Default
    ``"api"``
Description
    Controls how to paginate over tag search results.

    * ``"api"``: Use the `JSON API <https://www.zerochan.net/api>`__
      (no ``extension`` metadata)
    * ``"html"``: Parse HTML pages
      (limited to 100 pages * 24 posts)


extractor.[booru].tags
----------------------
Type
    ``bool``
Default
    ``false``
Description
    Categorize tags by their respective types
    and provide them as ``tags_<type>`` metadata fields.

    Note: This requires 1 additional HTTP request per post.


extractor.[booru].notes
-----------------------
Type
    ``bool``
Default
    ``false``
Description
    Extract overlay notes (position and text).

    Note: This requires 1 additional HTTP request per post.


extractor.[booru].url
---------------------
Type
    ``string``
Default
    ``"file_url"``
Example
    ``"preview_url"``
Description
    Alternate field name to retrieve download URLs from.


extractor.[manga-extractor].chapter-reverse
-------------------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Reverse the order of chapter URLs extracted from manga pages.

    * ``true``: Start with the latest chapter
    * ``false``: Start with the first chapter


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

    * ``true``: Write downloaded data into ``.part`` files and rename
      them upon download completion. This mode additionally supports
      resuming incomplete downloads.
    * ``false``: Do not use ``.part`` files and write data directly
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
    ``string``
Default
    ``null``
Example
    ``"32000"``, ``"500k"``, ``"2.5M"``
Description
    Maximum download rate in bytes per second.

    Possible values are valid integer or floating-point numbers
    optionally followed by one of ``k``, ``m``. ``g``, ``t``, or ``p``.
    These suffixes are case-insensitive.


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
    * ``object`` (`scheme` -> `proxy`)
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
    ``object`` (`name` -> `value`)
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


downloader.ytdl.format
----------------------
Type
    ``string``
Default
    youtube-dl's default, currently ``"bestvideo+bestaudio/best"``
Description
    Video `format selection
    <https://github.com/ytdl-org/youtube-dl#format-selection>`__
    directly passed to youtube-dl.


downloader.ytdl.forward-cookies
-------------------------------
Type
    ``bool``
Default
    ``false``
Description
    Forward cookies to youtube-dl.


downloader.ytdl.logging
-----------------------
Type
    ``bool``
Default
    ``true``
Description
    Route youtube-dl's output through gallery-dl's logging system.
    Otherwise youtube-dl will write its output directly to stdout/stderr.

    Note: Set ``quiet`` and ``no_warnings`` in
    `downloader.ytdl.raw-options`_ to ``true`` to suppress all output.


downloader.ytdl.module
----------------------
Type
    ``string``
Default
    ``null``
Description
    Name of the youtube-dl Python module to import.

    Setting this to ``null`` will first try to import ``"yt_dlp"``
    and use ``"youtube_dl"`` as fallback.


downloader.ytdl.outtmpl
-----------------------
Type
    ``string``
Default
    ``null``
Description
    The `Output Template <https://github.com/ytdl-org/youtube-dl#output-template>`__
    used to generate filenames for files downloaded with youtube-dl.

    Special values:

    * ``null``: generate filenames with `extractor.*.filename`_
    * ``"default"``: use youtube-dl's default, currently ``"%(title)s-%(id)s.%(ext)s"``

    Note: An output template other than ``null`` might
    cause unexpected results in combination with other options
    (e.g. ``"skip": "enumerate"``)


downloader.ytdl.raw-options
---------------------------
Type
    ``object`` (`name` -> `value`)
Example
    .. code:: json

        {
            "quiet": true,
            "writesubtitles": true,
            "merge_output_format": "mkv"
        }

Description
    Additional options passed directly to the ``YoutubeDL`` constructor.

    All available options can be found in `youtube-dl's docstrings
    <https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L138-L318>`__.


downloader.ytdl.cmdline-args
----------------------------
Type
    * ``string``
    * ``list`` of ``strings``
Example
    * ``"--quiet --write-sub --merge-output-format mkv"``
    * ``["--quiet", "--write-sub", "--merge-output-format", "mkv"]``
Description
    Additional options specified as youtube-dl command-line arguments.


downloader.ytdl.config-file
---------------------------
Type
    |Path|_
Example
    ``"~/.config/youtube-dl/config"``
Description
    Location of a youtube-dl configuration file to load options from.



Output Options
==============


output.mode
-----------
Type
    * ``string``
    * ``object`` (`key` -> `format string`)
Default
    ``"auto"``
Description
    Controls the output string format and status indicators.

    * ``"null"``: No output
    * ``"pipe"``: Suitable for piping to other processes or files
    * ``"terminal"``: Suitable for the standard Windows console
    * ``"color"``: Suitable for terminals that understand ANSI escape codes and colors
    * ``"auto"``: ``"terminal"`` on Windows with `output.ansi`_ disabled,
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

    Note: ``errors`` always defaults to ``"replace"``


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
    ``object`` (`key` -> `ANSI color`)
Default
    ``{"success": "1;32", "skip": "2"}``
Description
    Controls the `ANSI colors <https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797#colors--graphics-mode>`__
    used with |mode: color|__ for successfully downloaded or skipped files.

.. __: `output.mode`_


output.ansi
-----------
Type
    ``bool``
Default
    ``false``
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

    * ``true``: Show the default progress indicator
      (``"[{current}/{total}] {url}"``)
    * ``false``: Do not show any progress indicator
    * Any ``string``: Show the progress indicator using this
      as a custom `format string`_. Possible replacement keys are
      ``current``, ``total``  and ``url``.


output.log
----------
Type
    * ``string``
    * |Logging Configuration|_
Default
    ``"[{name}][{levelname}] {message}"``
Description
    Configuration for logging output to stderr.

    If this is a simple ``string``, it specifies
    the format string for logging messages.


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

    The default format string here is ``"{message}"``.


output.errorfile
----------------
Type
    * |Path|_
    * |Logging Configuration|_
Description
    File to write input URLs which returned an error to.

    The default format string here is also ``"{message}"``.

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
    ``object`` (`directory` -> `extensions`)
Default
    .. code:: json

        {
            "Pictures": ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp"],
            "Video"   : ["flv", "ogv", "avi", "mp4", "mpg", "mpeg", "3gp", "mkv", "webm", "vob", "wmv"],
            "Music"   : ["mp3", "aac", "flac", "ogg", "wma", "m4a", "wav"],
            "Archives": ["zip", "rar", "7z", "tar", "gz", "bz2"]
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

    * ``"replace"``: Replace/Overwrite the old version with the new one

    * ``"enumerate"``: Add an enumeration index to the filename of the new
      version like `skip = "enumerate" <extractor.*.skip_>`__


compare.equal
-------------
Type
    ``string``
Default
    ``"null"``
Description
    The action to take when files do compare as equal.

    * ``"abort:N"``: Stop the current extractor run
      after ``N`` consecutive files compared as equal.

    * ``"terminate:N"``: Stop the current extractor run,
      including parent extractors,
      after ``N`` consecutive files compared as equal.

    * ``"exit:N"``: Exit the program
      after ``N`` consecutive files compared as equal.


compare.shallow
---------------
Type
    ``bool``
Default
    ``false``
Description
    Only compare file sizes. Do not read and compare their content.


exec.archive
------------
Type
    |Path|_
Description
    File to store IDs of executed commands in,
    similar to `extractor.*.archive`_.

    ``archive-format``, ``archive-prefix``, and ``archive-pragma`` options,
    akin to
    `extractor.*.archive-format`_,
    `extractor.*.archive-prefix`_, and
    `extractor.*.archive-pragma`_, are supported as well.


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
      Each element of this list is treated as a `format string`_ using
      the files' metadata as well as ``{_path}``, ``{_directory}``,
      and ``{_filename}``.


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


metadata.mode
-------------
Type
    ``string``
Default
    ``"json"``
Description
    Selects how to process metadata.

    * ``"json"``: write metadata using |json.dump()|_
    * ``"jsonl"``: write metadata in `JSON Lines
      <https://jsonlines.org/>`__ format
    * ``"tags"``: write ``tags`` separated by newlines
    * ``"custom"``: write the result of applying `metadata.content-format`_
      to a file's metadata dictionary
    * ``"modify"``: add or modify metadata entries
    * ``"delete"``: remove metadata entries


metadata.filename
-----------------
Type
    ``string``
Default
    ``null``
Example
    ``"{id}.data.json"``
Description
    A `format string`_ to build the filenames for metadata files with.
    (see `extractor.filename <extractor.*.filename_>`__)

    Using ``"-"`` as filename will write all output to ``stdout``.

    If this option is set, `metadata.extension`_ and
    `metadata.extension-format`_ will be ignored.


metadata.directory
------------------
Type
    ``string``
Default
    ``"."``
Example
    ``"metadata"``
Description
    Directory where metadata files are stored in relative to the
    current target location for file downloads.


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
    ``string``
Example
    * ``"{extension}.json"``
    * ``"json"``
Description
    Custom format string to build filename extensions for metadata
    files with, which will replace the original filename extensions.

    Note: `metadata.extension`_ is ignored if this option is set.


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
    ``post``
        When starting to download all files of a `post`,
        e.g. a Tweet on Twitter or a post on Patreon.
    ``post-after``
        After downloading all files of a `post`


metadata.fields
---------------
Type
    * ``list`` of ``strings``
    * ``object`` (`field name` -> `format string`_)
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
    * ``"mode": "delete"``:
        A list of metadata field names to remove.
    * ``"mode": "modify"``:
        An object with metadata field names mapping to a `format string`_
        whose result is assigned to said field name.


metadata.content-format
-----------------------
Type
    * ``string``
    * ``list`` of ``strings``
Example
    * ``"tags:\n\n{tags:J\n}\n"``
    * ``["tags:", "", "{tags:J\n}"]``
Description
    Custom format string to build the content of metadata files with.

    Note: Only applies for ``"mode": "custom"``.


metadata.ascii
--------------
Type
    ``bool``
Default
    ``false``
Description
    Escape all non-ASCII characters.

    See the ``ensure_ascii`` argument of |json.dump()|_ for further details.

    Note: Only applies for ``"mode": "json"`` and ``"jsonl"``.


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

    Note: Only applies for ``"mode": "json"``.


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

    Note: Only applies for ``"mode": "json"`` and ``"jsonl"``.


metadata.sort
-------------
Type
    ``bool``
Default
    ``false``
Description
    Sort output by `key`.

    See the ``sort_keys`` argument of |json.dump()|_ for further details.

    Note: Only applies for ``"mode": "json"`` and ``"jsonl"``.


metadata.open
-------------
Type
    ``string``
Defsult
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
Defsult
    ``"utf-8"``
Description
    Name of the encoding used to encode a file's content.

    See the ``encoding`` argument of |open()|_ for further details.


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
    |Path|_
Description
    File to store IDs of generated metadata files in,
    similar to `extractor.*.archive`_.

    ``archive-format``, ``archive-prefix``, and ``archive-pragma`` options,
    akin to
    `extractor.*.archive-format`_,
    `extractor.*.archive-prefix`_, and
    `extractor.*.archive-pragma`_, are supported as well.


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
    |datetime|_ object.

    Note: This option gets ignored if `mtime.value`_ is set.


mtime.value
-----------
Type
    ``string``
Default
    ``null``
Example
    * ``"{status[date]}"``
    * ``"{content[0:6]:R22/2022/D%Y%m%d/}"``
Description
    A `format string`_ whose value should be used.

    The resulting value must be either a UNIX timestamp or a
    |datetime|_ object.


python.archive
--------------
Type
    |Path|_
Description
    File to store IDs of called Python functions in,
    similar to `extractor.*.archive`_.

    ``archive-format``, ``archive-prefix``, and ``archive-pragma`` options,
    akin to
    `extractor.*.archive-format`_,
    `extractor.*.archive-prefix`_, and
    `extractor.*.archive-pragma`_, are supported as well.


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


python.function
---------------
Type
    ``string``
Example
    * ``"my_module:generate_text"``
    * ``"~/.local/share/gdl-utils.py:resize"``
Description
    The Python function to call.

    This function is specified as ``<module>:<function name>``
    and gets called with the current metadata dict as argument.

    ``module`` is either an importable Python module name
    or the |Path|_ to a `.py` file,


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
    Additional FFmpeg command-line arguments.


ugoira.ffmpeg-demuxer
---------------------
Type
    ``string``
Default
    ``auto``
Description
    FFmpeg demuxer to read and process input files with. Possible values are

    * "`concat <https://ffmpeg.org/ffmpeg-formats.html#concat-1>`_" (inaccurate frame timecodes for non-uniform frame delays)
    * "`image2 <https://ffmpeg.org/ffmpeg-formats.html#image2-1>`_" (accurate timecodes, requires nanosecond file timestamps, i.e. no Windows or macOS)
    * "mkvmerge" (accurate timecodes, only WebM or MKV, requires `mkvmerge <ugoira.mkvmerge-location_>`__)

    `"auto"` will select `mkvmerge` if available and fall back to `concat` otherwise.


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
    Controls FFmpeg output.

    * ``true``: Enable FFmpeg output
    * ``false``: Disable all FFmpeg output
    * any ``string``: Pass ``-hide_banner`` and ``-loglevel``
      with this value as argument to FFmpeg


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
    Controls the frame rate argument (``-r``) for FFmpeg

    * ``"auto"``: Automatically assign a fitting frame rate
      based on delays between frames.
    * ``"uniform"``: Like ``auto``, but assign an explicit frame rate
      only to Ugoira with uniform frame delays.
    * any other ``string``:  Use this value as argument for ``-r``.
    * ``null`` or an empty ``string``: Don't set an explicit frame rate.


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
    to the list of FFmpeg command-line arguments
    to reduce an odd width/height by 1 pixel and make them even.


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


zip.compression
---------------
Type
    ``string``
Default
    ``"store"``
Description
    Compression method to use when writing the archive.

    Possible values are ``"store"``, ``"zip"``, ``"bzip2"``, ``"lzma"``.

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

    Note: Relative paths are relative to the current
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
    * ``"default"``: Write the central directory file header
      once after everything is done or an exception is raised.

    * ``"safe"``: Update the central directory file header
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
    `extractor/__init__.py <../gallery_dl/extractor/__init__.py#L12>`__
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

    Note: ``null`` references internal extractors defined in
    `extractor/__init__.py <../gallery_dl/extractor/__init__.py#L12>`__
    or by `extractor.modules`_.


globals
-------
Type
    * |Path|_
    * ``string``
Example
    * ``"~/.local/share/gdl-globals.py"``
    * ``"gdl-globals"``
Description
    | Path to or name of an
      `importable <https://docs.python.org/3/reference/import.html>`__
      Python module,
    | whose namespace,
      in addition to the ``GLOBALS`` dict in `util.py <../gallery_dl/util.py>`__,
      gets used as |globals parameter|__ for compiled Python expressions.

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


format-separator
----------------
Type
    ``string``
Default
    ``"/"``
Description
    Character(s) used as argument separator in format string
    `format specifiers <formatting.md#format-specifiers>`__.

    For example, setting this option to ``"#"`` would allow a replacement
    operation to be ``Rold#new#`` instead of the default ``Rold/new/``


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
      * set ``http://localhost:6414/`` as "redirect uri"
      * solve the "I'm not a robot" reCAPTCHA if needed
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
    * use a random name and description,
      set "Type" to "Application", "Platform" to "All",
      and "Use" to "Non-Commercial"
    * fill out the two checkboxes at the bottom and click "Apply"
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
    * fill out the form: use a random name and description, set
      https://example.org/ as "Application Website" and "Default
      callback URL"
    * solve Google's "I'm not a robot" challenge and click "Register"
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

    In Windows environments, backslashes (``"\"``) can, in addition to
    forward slashes (``"/"``), be used as path separators.
    Because backslashes are JSON's escape character,
    they themselves have to be escaped.
    The path ``C:\path\to\file.ext`` has therefore to be written as
    ``"C:\\path\\to\\file.ext"`` if you want to use backslashes.


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
        * General format string for logging messages
          or a dictionary with format strings for each loglevel.

          In addition to the default
          `LogRecord attributes <https://docs.python.org/3/library/logging.html#logrecord-attributes>`__,
          it is also possible to access the current
          `extractor <https://github.com/mikf/gallery-dl/blob/v1.24.2/gallery_dl/extractor/common.py#L26>`__,
          `job <https://github.com/mikf/gallery-dl/blob/v1.24.2/gallery_dl/job.py#L21>`__,
          `path <https://github.com/mikf/gallery-dl/blob/v1.24.2/gallery_dl/path.py#L27>`__,
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

    Note: path, mode, and encoding are only applied when configuring
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

    It is possible to set a ``"filter"`` expression similar to
    `image-filter <extractor.*.image-filter_>`_ to only run a post-processor
    conditionally.

    It is also possible set a ``"whitelist"`` or ``"blacklist"`` to
    only enable or disable a post-processor for the specified
    extractor categories.

    The available post-processor types are

    ``classify``
        Categorize files by filename extension
    ``compare``
        | Compare versions of the same file and replace/enumerate them on mismatch
        | (requires `downloader.*.part`_ = ``true`` and `extractor.*.skip`_ = ``false``)
    ``exec``
        Execute external commands
    ``metadata``
        Write metadata to separate files
    ``mtime``
        Set file modification time according to its metadata
    ``python``
        Call Python functions
    ``ugoira``
        Convert Pixiv Ugoira to WebM using `FFmpeg <https://www.ffmpeg.org/>`__
    ``zip``
        Store files in a ZIP archive



.. |.netrc| replace:: ``.netrc``
.. |requests.request()| replace:: ``requests.request()``
.. |timeout| replace:: ``timeout``
.. |verify| replace:: ``verify``
.. |mature_content| replace:: ``mature_content``
.. |webbrowser.open()| replace:: ``webbrowser.open()``
.. |datetime| replace:: ``datetime``
.. |datetime.max| replace:: ``datetime.max``
.. |Date| replace:: ``Date``
.. |Duration| replace:: ``Duration``
.. |Path| replace:: ``Path``
.. |Last-Modified| replace:: ``Last-Modified``
.. |Logging Configuration| replace:: ``Logging Configuration``
.. |Postprocessor Configuration| replace:: ``Postprocessor Configuration``
.. |strptime| replace:: strftime() and strptime() Behavior
.. |postprocessors| replace:: ``postprocessors``
.. |mode: color| replace:: ``"mode": "color"``
.. |open()| replace:: the built-in ``open()`` function
.. |json.dump()| replace:: ``json.dump()``

.. _base-directory: `extractor.*.base-directory`_
.. _date-format: `extractor.*.date-format`_
.. _deviantart.metadata: `extractor.deviantart.metadata`_
.. _deviantart.comments: `extractor.deviantart.comments`_
.. _postprocessors: `extractor.*.postprocessors`_
.. _download archive: `extractor.*.archive`_

.. _.netrc:             https://stackoverflow.com/tags/.netrc/info
.. _Last-Modified:      https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.29
.. _datetime:           https://docs.python.org/3/library/datetime.html#datetime-objects
.. _datetime.max:       https://docs.python.org/3/library/datetime.html#datetime.datetime.max
.. _strptime:           https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
.. _webbrowser.open():  https://docs.python.org/3/library/webbrowser.html
.. _open():             https://docs.python.org/3/library/functions.html#open
.. _json.dump():        https://docs.python.org/3/library/json.html#json.dump
.. _mature_content:     https://www.deviantart.com/developers/http/v1/20160316/object/deviation
.. _Authentication:     https://github.com/mikf/gallery-dl#authentication
.. _OAuth:              https://github.com/mikf/gallery-dl#oauth
.. _format string:      formatting.md
.. _format strings:     formatting.md
.. _youtube-dl:         https://github.com/ytdl-org/youtube-dl
.. _requests.request(): https://requests.readthedocs.io/en/master/api/#requests.request
.. _timeout:            https://requests.readthedocs.io/en/master/user/advanced/#timeouts
.. _verify:             https://requests.readthedocs.io/en/master/user/advanced/#ssl-cert-verification
.. _`Requests' proxy documentation`: https://requests.readthedocs.io/en/master/user/advanced/#proxies
