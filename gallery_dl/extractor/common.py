# -*- coding: utf-8 -*-

# Copyright 2014-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by extractor modules."""

import re
import time
import netrc
import queue
import logging
import datetime
import requests
import threading
from .message import Message
from .. import config, text, util, exception, cloudflare


class Extractor():

    category = ""
    subcategory = ""
    categorytransfer = False
    directory_fmt = ("{category}",)
    filename_fmt = "{filename}.{extension}"
    archive_fmt = ""
    cookiedomain = ""
    root = ""
    test = None
    _request_last = 0
    _request_interval = 0

    def __init__(self, match):
        self.session = requests.Session()
        self.log = logging.getLogger(self.category)
        self.url = match.string

        self._cookiefile = None
        self._cookiejar = self.session.cookies
        self._parentdir = ""

        self._cfgpath = ("extractor", self.category, self.subcategory)
        self._write_pages = self.config("write-pages", False)
        self._retries = self.config("retries", 4)
        self._timeout = self.config("timeout", 30)
        self._verify = self.config("verify", True)
        self._request_interval = self.config(
            "sleep-request", self._request_interval)

        if self._retries < 0:
            self._retries = float("inf")

        self._init_headers()
        self._init_cookies()
        self._init_proxies()

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

    def request(self, url, *, method="GET", session=None, retries=None,
                encoding=None, fatal=True, notfound=None, **kwargs):
        tries = 1
        retries = self._retries if retries is None else retries
        session = self.session if session is None else session
        kwargs.setdefault("timeout", self._timeout)
        kwargs.setdefault("verify", self._verify)
        response = None

        if self._request_interval:
            seconds = (self._request_interval -
                       (time.time() - Extractor._request_last))
            if seconds > 0:
                self.log.debug("Sleeping for %.5s seconds", seconds)
                time.sleep(seconds)

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

                reason = response.reason
                if cloudflare.is_challenge(response):
                    self.log.info("Solving Cloudflare challenge")
                    response, domain, cookies = cloudflare.solve_challenge(
                        session, response, kwargs)
                    if cookies:
                        cloudflare.cookies.update(
                            self.category, (domain, cookies))
                        return response
                if cloudflare.is_captcha(response):
                    self.log.warning("Cloudflare CAPTCHA")

                msg = "'{} {}' for '{}'".format(code, reason, url)
                if code < 500 and code != 429 and code != 430:
                    break
            finally:
                Extractor._request_last = time.time()

            self.log.debug("%s (%s/%s)", msg, tries, retries+1)
            if tries > retries:
                break
            time.sleep(tries)
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
                epoch = datetime.datetime(1970, 1, 1)
                until = (until - epoch) / datetime.timedelta(0, 1)
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

    def _init_headers(self):
        """Initialize HTTP headers for the 'session' object"""
        headers = self.session.headers
        headers.clear()

        headers["User-Agent"] = self.config(
            "user-agent", ("Mozilla/5.0 (X11; Linux x86_64; rv:68.0) "
                           "Gecko/20100101 Firefox/68.0"))
        headers["Accept"] = "*/*"
        headers["Accept-Language"] = "en-US,en;q=0.5"
        headers["Accept-Encoding"] = "gzip, deflate"
        headers["Connection"] = "keep-alive"
        headers["Upgrade-Insecure-Requests"] = "1"

    def _init_proxies(self):
        """Update the session's proxy map"""
        proxies = self.config("proxy")
        if proxies:
            if isinstance(proxies, str):
                proxies = {"http": proxies, "https": proxies}
            if isinstance(proxies, dict):
                for scheme, proxy in proxies.items():
                    if "://" not in proxy:
                        proxies[scheme] = "http://" + proxy.lstrip("/")
                self.session.proxies = proxies
            else:
                self.log.warning("invalid proxy specifier: %s", proxies)

    def _init_cookies(self):
        """Populate the session's cookiejar"""
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
                        cookies = util.load_cookiestxt(fp)
                except Exception as exc:
                    self.log.warning("cookies: %s", exc)
                else:
                    self._update_cookies(cookies)
                    self._cookiefile = cookiefile
            else:
                self.log.warning(
                    "expected 'dict' or 'str' value for 'cookies' option, "
                    "got '%s' (%s)", cookies.__class__.__name__, cookies)

        cookies = cloudflare.cookies(self.category)
        if cookies:
            domain, cookies = cookies
            self._update_cookies_dict(cookies, domain)

    def _store_cookies(self):
        """Store the session's cookiejar in a cookies.txt file"""
        if self._cookiefile and self.config("cookies-update", True):
            try:
                with open(self._cookiefile, "w") as fp:
                    util.save_cookiestxt(fp, self._cookiejar)
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
            if cookie.name in names and cookie.domain == domain:
                if cookie.expires and cookie.expires < now:
                    self.log.warning("Cookie '%s' has expired", cookie.name)
                else:
                    names.discard(cookie.name)
                    if not names:
                        return True
        return False

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
            Extractor._dump_sanitize('_', response.url)
        )[:250]

        try:
            with open(fname + ".dump", 'wb') as fp:
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
            images = zip(
                range(1, data["count"]+1),
                imgs,
            )
        else:
            try:
                data["count"] = len(imgs)
            except TypeError:
                pass
            images = enumerate(imgs, 1)

        yield Message.Version, 1
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

        yield Message.Version, 1
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


class SharedConfigMixin():
    """Enable sharing of config settings based on 'basecategory'"""
    basecategory = ""

    def config(self, key, default=None):
        return config.interpolate_common(
            ("extractor",), (
                (self.category, self.subcategory),
                (self.basecategory, self.subcategory),
            ), key, default,
        )


def generate_extractors(extractor_data, symtable, classes):
    """Dynamically generate Extractor classes"""
    extractors = config.get(("extractor",), classes[0].basecategory)
    ckey = extractor_data.get("_ckey")
    prev = None

    if extractors:
        extractor_data.update(extractors)

    for category, info in extractor_data.items():

        if not isinstance(info, dict):
            continue

        root = info["root"]
        domain = root[root.index(":") + 3:]
        pattern = info.get("pattern") or re.escape(domain)
        name = (info.get("name") or category).capitalize()

        for cls in classes:

            class Extr(cls):
                pass
            Extr.__module__ = cls.__module__
            Extr.__name__ = Extr.__qualname__ = \
                name + cls.subcategory.capitalize() + "Extractor"
            Extr.__doc__ = \
                "Extractor for " + cls.subcategory + "s from " + domain
            Extr.category = category
            Extr.pattern = r"(?:https?://)?" + pattern + cls.pattern_fmt
            Extr.test = info.get("test-" + cls.subcategory)
            Extr.root = root

            if "extra" in info:
                for key, value in info["extra"].items():
                    setattr(Extr, key, value)
            if prev and ckey:
                setattr(Extr, ckey, prev)

            symtable[Extr.__name__] = prev = Extr


# Undo automatic pyOpenSSL injection by requests
pyopenssl = config.get((), "pyopenssl", False)
if not pyopenssl:
    try:
        from requests.packages.urllib3.contrib import pyopenssl  # noqa
        pyopenssl.extract_from_urllib3()
    except ImportError:
        pass
del pyopenssl


# Replace urllib3's default cipher list to avoid Cloudflare CAPTCHAs
ciphers = config.get((), "ciphers", True)
if ciphers:

    if ciphers is True:
        ciphers = (
            # Firefox's list
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
            "DHE-RSA-AES128-SHA:"
            "DHE-RSA-AES256-SHA:"
            "AES128-SHA:"
            "AES256-SHA:"
            "DES-CBC3-SHA"
        )
    elif isinstance(ciphers, list):
        ciphers = ":".join(ciphers)

    from requests.packages.urllib3.util import ssl_  # noqa
    ssl_.DEFAULT_CIPHERS = ciphers
    del ssl_
del ciphers
