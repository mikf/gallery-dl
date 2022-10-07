# -*- coding: utf-8 -*-

# Copyright 2014-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by extractor modules."""

import os
import re
import ssl
import time
import netrc
import queue
import logging
import datetime
import requests
import threading
from requests.adapters import HTTPAdapter
from .message import Message
from .. import config, text, util, exception


class Extractor():

    category = ""
    subcategory = ""
    basecategory = ""
    categorytransfer = False
    directory_fmt = ("{category}",)
    filename_fmt = "{filename}.{extension}"
    archive_fmt = ""
    cookiedomain = ""
    browser = None
    root = ""
    test = None
    request_interval = 0.0
    request_interval_min = 0.0
    request_timestamp = 0.0
    tls12 = True

    def __init__(self, match):
        self.log = logging.getLogger(self.category)
        self.url = match.string
        self.finalize = None

        if self.basecategory:
            self.config = self._config_shared
            self.config_accumulate = self._config_shared_accumulate
        self._cfgpath = ("extractor", self.category, self.subcategory)
        self._parentdir = ""

        self._write_pages = self.config("write-pages", False)
        self._retries = self.config("retries", 4)
        self._timeout = self.config("timeout", 30)
        self._verify = self.config("verify", True)
        self._proxies = util.build_proxy_map(self.config("proxy"), self.log)
        self._interval = util.build_duration_func(
            self.config("sleep-request", self.request_interval),
            self.request_interval_min,
        )

        if self._retries < 0:
            self._retries = float("inf")

        self._init_session()
        self._init_cookies()

    @classmethod
    def from_url(cls, url):
        if isinstance(cls.pattern, str):
            cls.pattern = re.compile(cls.pattern)
        match = cls.pattern.match(url)
        return cls(match) if match else None

    def __iter__(self):
        return self.items()

    def items(self):
        yield Message.Version, 1

    def skip(self, num):
        return 0

    def config(self, key, default=None):
        return config.interpolate(self._cfgpath, key, default)

    def config_accumulate(self, key):
        return config.accumulate(self._cfgpath, key)

    def _config_shared(self, key, default=None):
        return config.interpolate_common(("extractor",), (
            (self.category, self.subcategory),
            (self.basecategory, self.subcategory),
        ), key, default)

    def _config_shared_accumulate(self, key):
        values = config.accumulate(self._cfgpath, key)
        conf = config.get(("extractor",), self.basecategory)
        if conf:
            values[:0] = config.accumulate((self.subcategory,), key, conf=conf)
        return values

    def request(self, url, *, method="GET", session=None, retries=None,
                encoding=None, fatal=True, notfound=None, **kwargs):
        if session is None:
            session = self.session
        if retries is None:
            retries = self._retries
        if "proxies" not in kwargs:
            kwargs["proxies"] = self._proxies
        if "timeout" not in kwargs:
            kwargs["timeout"] = self._timeout
        if "verify" not in kwargs:
            kwargs["verify"] = self._verify
        response = None
        tries = 1

        if self._interval:
            seconds = (self._interval() -
                       (time.time() - Extractor.request_timestamp))
            if seconds > 0.0:
                self.sleep(seconds, "request")

        while True:
            try:
                response = session.request(method, url, **kwargs)
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    requests.exceptions.ChunkedEncodingError,
                    requests.exceptions.ContentDecodingError) as exc:
                msg = exc
            except (requests.exceptions.RequestException) as exc:
                raise exception.HttpError(exc)
            else:
                code = response.status_code
                if self._write_pages:
                    self._dump_response(response)
                if 200 <= code < 400 or fatal is None and \
                        (400 <= code < 500) or not fatal and \
                        (400 <= code < 429 or 431 <= code < 500):
                    if encoding:
                        response.encoding = encoding
                    return response
                if notfound and code == 404:
                    raise exception.NotFoundError(notfound)

                msg = "'{} {}' for '{}'".format(code, response.reason, url)
                server = response.headers.get("Server")
                if server and server.startswith("cloudflare"):
                    if code == 503 and \
                            (b"_cf_chl_opt" in response.content or
                             b"jschl-answer" in response.content):
                        self.log.warning("Cloudflare IUAM challenge")
                        break
                    if code == 403 and \
                            b'name="captcha-bypass"' in response.content:
                        self.log.warning("Cloudflare CAPTCHA")
                        break
                if code < 500 and code != 429 and code != 430:
                    break

            finally:
                Extractor.request_timestamp = time.time()

            self.log.debug("%s (%s/%s)", msg, tries, retries+1)
            if tries > retries:
                break
            self.sleep(
                max(tries, self._interval()) if self._interval else tries,
                "retry")
            tries += 1

        raise exception.HttpError(msg, response)

    def wait(self, *, seconds=None, until=None, adjust=1.0,
             reason="rate limit reset"):
        now = time.time()

        if seconds:
            seconds = float(seconds)
            until = now + seconds
        elif until:
            if isinstance(until, datetime.datetime):
                # convert to UTC timestamp
                until = util.datetime_to_timestamp(until)
            else:
                until = float(until)
            seconds = until - now
        else:
            raise ValueError("Either 'seconds' or 'until' is required")

        seconds += adjust
        if seconds <= 0.0:
            return

        if reason:
            t = datetime.datetime.fromtimestamp(until).time()
            isotime = "{:02}:{:02}:{:02}".format(t.hour, t.minute, t.second)
            self.log.info("Waiting until %s for %s.", isotime, reason)
        time.sleep(seconds)

    def sleep(self, seconds, reason):
        self.log.debug("Sleeping %.2f seconds (%s)",
                       seconds, reason)
        time.sleep(seconds)

    def _get_auth_info(self):
        """Return authentication information as (username, password) tuple"""
        username = self.config("username")
        password = None

        if username:
            password = self.config("password")
        elif self.config("netrc", False):
            try:
                info = netrc.netrc().authenticators(self.category)
                username, _, password = info
            except (OSError, netrc.NetrcParseError) as exc:
                self.log.error("netrc: %s", exc)
            except TypeError:
                self.log.warning("netrc: No authentication info")

        return username, password

    def _init_session(self):
        self.session = session = requests.Session()
        headers = session.headers
        headers.clear()
        ssl_options = ssl_ciphers = 0

        browser = self.config("browser")
        if browser is None:
            browser = self.browser
        if browser and isinstance(browser, str):
            browser, _, platform = browser.lower().partition(":")

            if not platform or platform == "auto":
                platform = ("Windows NT 10.0; Win64; x64"
                            if util.WINDOWS else "X11; Linux x86_64")
            elif platform == "windows":
                platform = "Windows NT 10.0; Win64; x64"
            elif platform == "linux":
                platform = "X11; Linux x86_64"
            elif platform == "macos":
                platform = "Macintosh; Intel Mac OS X 11.5"

            if browser == "chrome":
                if platform.startswith("Macintosh"):
                    platform = platform.replace(".", "_") + "_2"
            else:
                browser = "firefox"

            for key, value in HTTP_HEADERS[browser]:
                if value and "{}" in value:
                    headers[key] = value.format(platform)
                else:
                    headers[key] = value

            ssl_options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 |
                            ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
            ssl_ciphers = SSL_CIPHERS[browser]
        else:
            headers["User-Agent"] = self.config("user-agent", (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; "
                "rv:102.0) Gecko/20100101 Firefox/102.0"))
            headers["Accept"] = "*/*"
            headers["Accept-Language"] = "en-US,en;q=0.5"

        if BROTLI:
            headers["Accept-Encoding"] = "gzip, deflate, br"
        else:
            headers["Accept-Encoding"] = "gzip, deflate"

        custom_headers = self.config("headers")
        if custom_headers:
            headers.update(custom_headers)

        custom_ciphers = self.config("ciphers")
        if custom_ciphers:
            if isinstance(custom_ciphers, list):
                ssl_ciphers = ":".join(custom_ciphers)
            else:
                ssl_ciphers = custom_ciphers

        source_address = self.config("source-address")
        if source_address:
            if isinstance(source_address, str):
                source_address = (source_address, 0)
            else:
                source_address = (source_address[0], source_address[1])

        tls12 = self.config("tls12")
        if tls12 is None:
            tls12 = self.tls12
        if not tls12:
            ssl_options |= ssl.OP_NO_TLSv1_2
            self.log.debug("TLS 1.2 disabled.")

        adapter = _build_requests_adapter(
            ssl_options, ssl_ciphers, source_address)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

    def _init_cookies(self):
        """Populate the session's cookiejar"""
        self._cookiefile = None
        self._cookiejar = self.session.cookies
        if self.cookiedomain is None:
            return

        cookies = self.config("cookies")
        if cookies:
            if isinstance(cookies, dict):
                self._update_cookies_dict(cookies, self.cookiedomain)

            elif isinstance(cookies, str):
                cookiefile = util.expand_path(cookies)
                try:
                    with open(cookiefile) as fp:
                        util.cookiestxt_load(fp, self._cookiejar)
                except Exception as exc:
                    self.log.warning("cookies: %s", exc)
                else:
                    self._cookiefile = cookiefile

            elif isinstance(cookies, (list, tuple)):
                key = tuple(cookies)
                cookiejar = _browser_cookies.get(key)

                if cookiejar is None:
                    from ..cookies import load_cookies
                    cookiejar = self._cookiejar.__class__()
                    try:
                        load_cookies(cookiejar, cookies)
                    except Exception as exc:
                        self.log.warning("cookies: %s", exc)
                    else:
                        _browser_cookies[key] = cookiejar
                else:
                    self.log.debug("Using cached cookies from %s", key)

                setcookie = self._cookiejar.set_cookie
                for cookie in cookiejar:
                    setcookie(cookie)

            else:
                self.log.warning(
                    "Expected 'dict', 'list', or 'str' value for 'cookies' "
                    "option, got '%s' (%s)",
                    cookies.__class__.__name__, cookies)

    def _store_cookies(self):
        """Store the session's cookiejar in a cookies.txt file"""
        if self._cookiefile and self.config("cookies-update", True):
            try:
                with open(self._cookiefile, "w") as fp:
                    util.cookiestxt_store(fp, self._cookiejar)
            except OSError as exc:
                self.log.warning("cookies: %s", exc)

    def _update_cookies(self, cookies, *, domain=""):
        """Update the session's cookiejar with 'cookies'"""
        if isinstance(cookies, dict):
            self._update_cookies_dict(cookies, domain or self.cookiedomain)
        else:
            setcookie = self._cookiejar.set_cookie
            try:
                cookies = iter(cookies)
            except TypeError:
                setcookie(cookies)
            else:
                for cookie in cookies:
                    setcookie(cookie)

    def _update_cookies_dict(self, cookiedict, domain):
        """Update cookiejar with name-value pairs from a dict"""
        setcookie = self._cookiejar.set
        for name, value in cookiedict.items():
            setcookie(name, value, domain=domain)

    def _check_cookies(self, cookienames, *, domain=None):
        """Check if all 'cookienames' are in the session's cookiejar"""
        if not self._cookiejar:
            return False

        if domain is None:
            domain = self.cookiedomain
        names = set(cookienames)
        now = time.time()

        for cookie in self._cookiejar:
            if cookie.name in names and (
                    not domain or cookie.domain == domain):

                if cookie.expires:
                    diff = int(cookie.expires - now)

                    if diff <= 0:
                        self.log.warning(
                            "Cookie '%s' has expired", cookie.name)
                        continue

                    elif diff <= 86400:
                        hours = diff // 3600
                        self.log.warning(
                            "Cookie '%s' will expire in less than %s hour%s",
                            cookie.name, hours + 1, "s" if hours else "")

                names.discard(cookie.name)
                if not names:
                    return True
        return False

    def _prepare_ddosguard_cookies(self):
        if not self._cookiejar.get("__ddg2", domain=self.cookiedomain):
            self._cookiejar.set(
                "__ddg2", util.generate_token(), domain=self.cookiedomain)

    def _get_date_min_max(self, dmin=None, dmax=None):
        """Retrieve and parse 'date-min' and 'date-max' config values"""
        def get(key, default):
            ts = self.config(key, default)
            if isinstance(ts, str):
                try:
                    ts = int(datetime.datetime.strptime(ts, fmt).timestamp())
                except ValueError as exc:
                    self.log.warning("Unable to parse '%s': %s", key, exc)
                    ts = default
            return ts
        fmt = self.config("date-format", "%Y-%m-%dT%H:%M:%S")
        return get("date-min", dmin), get("date-max", dmax)

    def _dispatch_extractors(self, extractor_data, default=()):
        """ """
        extractors = {
            data[0].subcategory: data
            for data in extractor_data
        }

        include = self.config("include", default) or ()
        if include == "all":
            include = extractors
        elif isinstance(include, str):
            include = include.split(",")

        result = [(Message.Version, 1)]
        for category in include:
            if category in extractors:
                extr, url = extractors[category]
                result.append((Message.Queue, url, {"_extractor": extr}))
        return iter(result)

    @classmethod
    def _get_tests(cls):
        """Yield an extractor's test cases as (URL, RESULTS) tuples"""
        tests = cls.test
        if not tests:
            return

        if len(tests) == 2 and (not tests[1] or isinstance(tests[1], dict)):
            tests = (tests,)

        for test in tests:
            if isinstance(test, str):
                test = (test, None)
            yield test

    def _dump_response(self, response, history=True):
        """Write the response content to a .dump file in the current directory.

        The file name is derived from the response url,
        replacing special characters with "_"
        """
        if history:
            for resp in response.history:
                self._dump_response(resp, False)

        if hasattr(Extractor, "_dump_index"):
            Extractor._dump_index += 1
        else:
            Extractor._dump_index = 1
            Extractor._dump_sanitize = re.compile(r"[\\\\|/<>:\"?*&=#]+").sub

        fname = "{:>02}_{}".format(
            Extractor._dump_index,
            Extractor._dump_sanitize('_', response.url),
        )

        if util.WINDOWS:
            path = os.path.abspath(fname)[:255]
        else:
            path = fname[:251]

        try:
            with open(path + ".txt", 'wb') as fp:
                util.dump_response(
                    response, fp, headers=(self._write_pages == "all"))
        except Exception as e:
            self.log.warning("Failed to dump HTTP request (%s: %s)",
                             e.__class__.__name__, e)


class GalleryExtractor(Extractor):

    subcategory = "gallery"
    filename_fmt = "{category}_{gallery_id}_{num:>03}.{extension}"
    directory_fmt = ("{category}", "{gallery_id} {title}")
    archive_fmt = "{gallery_id}_{num}"
    enum = "num"

    def __init__(self, match, url=None):
        Extractor.__init__(self, match)
        self.gallery_url = self.root + match.group(1) if url is None else url

    def items(self):
        self.login()
        page = self.request(self.gallery_url, notfound=self.subcategory).text
        data = self.metadata(page)
        imgs = self.images(page)

        if "count" in data:
            if self.config("page-reverse"):
                images = util.enumerate_reversed(imgs, 1, data["count"])
            else:
                images = zip(
                    range(1, data["count"]+1),
                    imgs,
                )
        else:
            enum = enumerate
            try:
                data["count"] = len(imgs)
            except TypeError:
                pass
            else:
                if self.config("page-reverse"):
                    enum = util.enumerate_reversed
            images = enum(imgs, 1)

        yield Message.Directory, data
        for data[self.enum], (url, imgdata) in images:
            if imgdata:
                data.update(imgdata)
                if "extension" not in imgdata:
                    text.nameext_from_url(url, data)
            else:
                text.nameext_from_url(url, data)
            yield Message.Url, url, data

    def login(self):
        """Login and set necessary cookies"""

    def metadata(self, page):
        """Return a dict with general metadata"""

    def images(self, page):
        """Return a list of all (image-url, metadata)-tuples"""


class ChapterExtractor(GalleryExtractor):

    subcategory = "chapter"
    directory_fmt = (
        "{category}", "{manga}",
        "{volume:?v/ />02}c{chapter:>03}{chapter_minor:?//}{title:?: //}")
    filename_fmt = (
        "{manga}_c{chapter:>03}{chapter_minor:?//}_{page:>03}.{extension}")
    archive_fmt = (
        "{manga}_{chapter}{chapter_minor}_{page}")
    enum = "page"


class MangaExtractor(Extractor):

    subcategory = "manga"
    categorytransfer = True
    chapterclass = None
    reverse = True

    def __init__(self, match, url=None):
        Extractor.__init__(self, match)
        self.manga_url = url or self.root + match.group(1)

        if self.config("chapter-reverse", False):
            self.reverse = not self.reverse

    def items(self):
        self.login()
        page = self.request(self.manga_url).text

        chapters = self.chapters(page)
        if self.reverse:
            chapters.reverse()

        for chapter, data in chapters:
            data["_extractor"] = self.chapterclass
            yield Message.Queue, chapter, data

    def login(self):
        """Login and set necessary cookies"""

    def chapters(self, page):
        """Return a list of all (chapter-url, metadata)-tuples"""


class AsynchronousMixin():
    """Run info extraction in a separate thread"""

    def __iter__(self):
        messages = queue.Queue(5)
        thread = threading.Thread(
            target=self.async_items,
            args=(messages,),
            daemon=True,
        )

        thread.start()
        while True:
            msg = messages.get()
            if msg is None:
                thread.join()
                return
            if isinstance(msg, Exception):
                thread.join()
                raise msg
            yield msg
            messages.task_done()

    def async_items(self, messages):
        try:
            for msg in self.items():
                messages.put(msg)
        except Exception as exc:
            messages.put(exc)
        messages.put(None)


class BaseExtractor(Extractor):
    instances = ()

    def __init__(self, match):
        if not self.category:
            self._init_category(match)
        Extractor.__init__(self, match)

    def _init_category(self, match):
        for index, group in enumerate(match.groups()):
            if group is not None:
                if index:
                    self.category, self.root = self.instances[index-1]
                    if not self.root:
                        self.root = text.root_from_url(match.group(0))
                else:
                    self.root = group
                    self.category = group.partition("://")[2]
                break

    @classmethod
    def update(cls, instances):
        extra_instances = config.get(("extractor",), cls.basecategory)
        if extra_instances:
            for category, info in extra_instances.items():
                if isinstance(info, dict) and "root" in info:
                    instances[category] = info

        pattern_list = []
        instance_list = cls.instances = []
        for category, info in instances.items():
            root = info["root"]
            if root:
                root = root.rstrip("/")
            instance_list.append((category, root))

            pattern = info.get("pattern")
            if not pattern:
                pattern = re.escape(root[root.index(":") + 3:])
            pattern_list.append(pattern + "()")

        return (
            r"(?:" + cls.basecategory + r":(https?://[^/?#]+)|"
            r"(?:https?://)?(?:" + "|".join(pattern_list) + r"))"
        )


class RequestsAdapter(HTTPAdapter):

    def __init__(self, ssl_context=None, source_address=None):
        self.ssl_context = ssl_context
        self.source_address = source_address
        HTTPAdapter.__init__(self)

    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = self.ssl_context
        kwargs["source_address"] = self.source_address
        return HTTPAdapter.init_poolmanager(self, *args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs["ssl_context"] = self.ssl_context
        kwargs["source_address"] = self.source_address
        return HTTPAdapter.proxy_manager_for(self, *args, **kwargs)


def _build_requests_adapter(ssl_options, ssl_ciphers, source_address):
    key = (ssl_options, ssl_ciphers, source_address)
    try:
        return _adapter_cache[key]
    except KeyError:
        pass

    if ssl_options or ssl_ciphers:
        ssl_context = ssl.create_default_context()
        if ssl_options:
            ssl_context.options |= ssl_options
        if ssl_ciphers:
            ssl_context.set_ecdh_curve("prime256v1")
            ssl_context.set_ciphers(ssl_ciphers)
    else:
        ssl_context = None

    adapter = _adapter_cache[key] = RequestsAdapter(
        ssl_context, source_address)
    return adapter


_adapter_cache = {}
_browser_cookies = {}


HTTP_HEADERS = {
    "firefox": (
        ("User-Agent", "Mozilla/5.0 ({}; rv:102.0) "
                       "Gecko/20100101 Firefox/102.0"),
        ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,"
                   "image/avif,image/webp,*/*;q=0.8"),
        ("Accept-Language", "en-US,en;q=0.5"),
        ("Accept-Encoding", None),
        ("Referer", None),
        ("DNT", "1"),
        ("Connection", "keep-alive"),
        ("Upgrade-Insecure-Requests", "1"),
        ("Cookie", None),
        ("Sec-Fetch-Dest", "empty"),
        ("Sec-Fetch-Mode", "no-cors"),
        ("Sec-Fetch-Site", "same-origin"),
        ("TE", "trailers"),
    ),
    "chrome": (
        ("Upgrade-Insecure-Requests", "1"),
        ("User-Agent", "Mozilla/5.0 ({}) AppleWebKit/537.36 (KHTML, "
                       "like Gecko) Chrome/92.0.4515.131 Safari/537.36"),
        ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,"
                   "image/webp,image/apng,*/*;q=0.8"),
        ("Referer", None),
        ("Accept-Encoding", None),
        ("Accept-Language", "en-US,en;q=0.9"),
        ("Cookie", None),
    ),
}

SSL_CIPHERS = {
    "firefox": (
        "TLS_AES_128_GCM_SHA256:"
        "TLS_CHACHA20_POLY1305_SHA256:"
        "TLS_AES_256_GCM_SHA384:"
        "ECDHE-ECDSA-AES128-GCM-SHA256:"
        "ECDHE-RSA-AES128-GCM-SHA256:"
        "ECDHE-ECDSA-CHACHA20-POLY1305:"
        "ECDHE-RSA-CHACHA20-POLY1305:"
        "ECDHE-ECDSA-AES256-GCM-SHA384:"
        "ECDHE-RSA-AES256-GCM-SHA384:"
        "ECDHE-ECDSA-AES256-SHA:"
        "ECDHE-ECDSA-AES128-SHA:"
        "ECDHE-RSA-AES128-SHA:"
        "ECDHE-RSA-AES256-SHA:"
        "AES128-GCM-SHA256:"
        "AES256-GCM-SHA384:"
        "AES128-SHA:"
        "AES256-SHA"
    ),
    "chrome": (
        "TLS_AES_128_GCM_SHA256:"
        "TLS_AES_256_GCM_SHA384:"
        "TLS_CHACHA20_POLY1305_SHA256:"
        "ECDHE-ECDSA-AES128-GCM-SHA256:"
        "ECDHE-RSA-AES128-GCM-SHA256:"
        "ECDHE-ECDSA-AES256-GCM-SHA384:"
        "ECDHE-RSA-AES256-GCM-SHA384:"
        "ECDHE-ECDSA-CHACHA20-POLY1305:"
        "ECDHE-RSA-CHACHA20-POLY1305:"
        "ECDHE-RSA-AES128-SHA:"
        "ECDHE-RSA-AES256-SHA:"
        "AES128-GCM-SHA256:"
        "AES256-GCM-SHA384:"
        "AES128-SHA:"
        "AES256-SHA:"
        "DES-CBC3-SHA"
    ),
}


urllib3 = requests.packages.urllib3

# detect brotli support
try:
    BROTLI = urllib3.response.brotli is not None
except AttributeError:
    BROTLI = False

# set (urllib3) warnings filter
action = config.get((), "warnings", "default")
if action:
    try:
        import warnings
        warnings.simplefilter(action, urllib3.exceptions.HTTPWarning)
    except Exception:
        pass
del action

# Undo automatic pyOpenSSL injection by requests
pyopenssl = config.get((), "pyopenssl", False)
if not pyopenssl:
    try:
        from requests.packages.urllib3.contrib import pyopenssl  # noqa
        pyopenssl.extract_from_urllib3()
    except ImportError:
        pass
del pyopenssl
