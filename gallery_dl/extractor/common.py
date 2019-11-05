# -*- coding: utf-8 -*-

# Copyright 2014-2019 Mike Fährmann
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
import http.cookiejar
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

    def __init__(self, match):
        self.session = requests.Session()
        self.log = logging.getLogger(self.category)
        self.url = match.string

        self._cookiefile = None
        self._cookiejar = self.session.cookies
        self._retries = self.config("retries", 4)
        self._timeout = self.config("timeout", 30)
        self._verify = self.config("verify", True)

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
        return config.interpolate(
            ("extractor", self.category, self.subcategory, key), default)

    def request(self, url, *, method="GET", session=None, retries=None,
                encoding=None, fatal=True, notfound=None, **kwargs):
        tries = 1
        retries = self._retries if retries is None else retries
        session = self.session if session is None else session
        kwargs.setdefault("timeout", self._timeout)
        kwargs.setdefault("verify", self._verify)

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
                if 200 <= code < 400 or fatal is None and \
                        (400 <= code < 500) or not fatal and \
                        (400 <= code < 429 or 431 <= code < 500):
                    if encoding:
                        response.encoding = encoding
                    return response
                if notfound and code == 404:
                    raise exception.NotFoundError(notfound)
                if cloudflare.is_challenge(response):
                    self.log.info("Solving Cloudflare challenge")
                    url, domain, cookies = cloudflare.solve_challenge(
                        session, response, kwargs)
                    cloudflare.cookies.update(self.category, (domain, cookies))
                    continue
                if cloudflare.is_captcha(response):
                    try:
                        import OpenSSL  # noqa
                    except ImportError:
                        msg = " - Install 'pyOpenSSL' and try again"
                    else:
                        msg = ""
                    self.log.warning("Cloudflare CAPTCHA" + msg)

                msg = "'{} {}' for '{}'".format(code, response.reason, url)
                if code < 500 and code != 429 and code != 430:
                    break

            self.log.debug("%s (%s/%s)", msg, tries, retries+1)
            if tries > retries:
                break
            time.sleep(min(2 ** (tries-1), 1800))
            tries += 1

        raise exception.HttpError(msg)

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
        cookies = self.config("cookies")
        if cookies:
            if isinstance(cookies, dict):
                self._update_cookies_dict(cookies, self.cookiedomain)
            elif isinstance(cookies, str):
                cookiefile = util.expand_path(cookies)
                cookiejar = http.cookiejar.MozillaCookieJar()
                try:
                    cookiejar.load(cookiefile)
                except OSError as exc:
                    self.log.warning("cookies: %s", exc)
                else:
                    self._cookiejar.update(cookiejar)
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
        if self._cookiefile and self.config("cookies-update", False):
            cookiejar = http.cookiejar.MozillaCookieJar()
            for cookie in self._cookiejar:
                cookiejar.set_cookie(cookie)
            try:
                cookiejar.save(self._cookiefile)
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
        if domain is None:
            domain = self.cookiedomain
        try:
            for name in cookienames:
                self._cookiejar._find(name, domain)
        except KeyError:
            return False
        return True

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
        page = self.request(self.gallery_url).text
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
            yield Message.Url, url, text.nameext_from_url(url, data)

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

    def config(self, key, default=None, *, sentinel=object()):
        value = Extractor.config(self, key, sentinel)
        if value is sentinel:
            cat, self.category = self.category, self.basecategory
            value = Extractor.config(self, key, default)
            self.category = cat
        return value


def generate_extractors(extractor_data, symtable, classes):
    """Dynamically generate Extractor classes"""
    extractors = config.get(("extractor", classes[0].basecategory))
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


# Reduce strictness of the expected magic string in cookiejar files.
# (This allows the use of Wget-generated cookiejars without modification)
http.cookiejar.MozillaCookieJar.magic_re = re.compile(
    "#( Netscape)? HTTP Cookie File", re.IGNORECASE)

# Replace default cipher list of urllib3 to avoid Cloudflare CAPTCHAs
ciphers = config.get(("ciphers",), True)
if ciphers:
    logging.getLogger("gallery-dl").debug("Updating urllib3 ciphers")

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
