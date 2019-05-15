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
import requests
import threading
import http.cookiejar
from .message import Message
from .. import config, text, exception, cloudflare


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
        self._init_headers()
        self._init_cookies()
        self._init_proxies()
        self._retries = self.config("retries", 5)
        self._timeout = self.config("timeout", 30)
        self._verify = self.config("verify", True)

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

    def request(self, url, method="GET", *, session=None,
                encoding=None, expect=(), retries=None, **kwargs):
        tries = 0
        retries = retries or self._retries
        session = session or self.session
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
                if 200 <= code < 400 or code in expect:
                    if encoding:
                        response.encoding = encoding
                    return response
                if cloudflare.is_challenge(response):
                    self.log.info("Solving Cloudflare challenge")
                    url, domain, cookies = cloudflare.solve_challenge(
                        session, response, kwargs)
                    cloudflare.cookies.update(self.category, (domain, cookies))
                    continue

                msg = "{}: {} for url: {}".format(code, response.reason, url)
                if code < 500 and code != 429:
                    break

            tries += 1
            self.log.debug("%s (%d/%d)", msg, tries, retries)
            if tries >= retries:
                break
            time.sleep(2 ** tries)

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
        """Set additional headers for the 'session' object"""
        headers = self.session.headers
        headers.clear()

        headers["User-Agent"] = self.config(
            "user-agent", ("Mozilla/5.0 (X11; Linux x86_64; rv:62.0) "
                           "Gecko/20100101 Firefox/62.0"))
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
            else:
                cookiejar = http.cookiejar.MozillaCookieJar()
                try:
                    cookiejar.load(cookies)
                except OSError as exc:
                    self.log.warning("cookies: %s", exc)
                else:
                    self.session.cookies.update(cookiejar)

        cookies = cloudflare.cookies(self.category)
        if cookies:
            domain, cookies = cookies
            self._update_cookies_dict(cookies, domain)

    def _update_cookies(self, cookies, *, domain=""):
        """Update the session's cookiejar with 'cookies'"""
        if isinstance(cookies, dict):
            self._update_cookies_dict(cookies, domain or self.cookiedomain)
        else:
            setcookie = self.session.cookies.set_cookie
            try:
                cookies = iter(cookies)
            except TypeError:
                setcookie(cookies)
            else:
                for cookie in cookies:
                    setcookie(cookie)

    def _update_cookies_dict(self, cookiedict, domain):
        """Update cookiejar with name-value pairs from a dict"""
        setcookie = self.session.cookies.set
        for name, value in cookiedict.items():
            setcookie(name, value, domain=domain)

    def _check_cookies(self, cookienames, *, domain=""):
        """Check if all 'cookienames' are in the session's cookiejar"""
        if not domain:
            domain = self.cookiedomain
        try:
            for name in cookienames:
                self.session.cookies._find(name, domain)
        except KeyError:
            return False
        return True

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


class ChapterExtractor(Extractor):

    subcategory = "chapter"
    directory_fmt = (
        "{category}", "{manga}",
        "{volume:?v/ />02}c{chapter:>03}{chapter_minor:?//}{title:?: //}")
    filename_fmt = (
        "{manga}_c{chapter:>03}{chapter_minor:?//}_{page:>03}.{extension}")
    archive_fmt = (
        "{manga}_{chapter}{chapter_minor}_{page}")

    def __init__(self, match, url=None):
        Extractor.__init__(self, match)
        self.chapter_url = url or self.root + match.group(1)

    def items(self):
        self.login()
        page = self.request(self.chapter_url).text
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
        for data["page"], (url, imgdata) in images:
            if imgdata:
                data.update(imgdata)
            yield Message.Url, url, text.nameext_from_url(url, data)

    def login(self):
        """Login and set necessary cookies"""

    def metadata(self, page):
        """Return a dict with general metadata"""

    def images(self, page):
        """Return a list of all (image-url, metadata)-tuples"""


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


class GalleryExtractor(ChapterExtractor):

    subcategory = "gallery"
    filename_fmt = "{category}_{gallery_id}_{page:>03}.{extension}"
    directory_fmt = ("{category}", "{gallery_id} {title}")
    archive_fmt = "{gallery_id}_{page}"


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

# Update default cipher list of urllib3 < 1.25
# to fix issues with Cloudflare and, by extension, Artstation (#227)
import requests.packages.urllib3 as urllib3  # noqa
if urllib3.__version__ < "1.25":
    from requests.packages.urllib3.util import ssl_
    logging.getLogger("gallery-dl").debug(
        "updating default urllib3 ciphers")
    # cipher list taken from urllib3 1.25
    # https://github.com/urllib3/urllib3/blob/1.25/src/urllib3/util/ssl_.py
    # with additions from
    # https://github.com/Anorov/cloudflare-scrape/pull/242
    ssl_.DEFAULT_CIPHERS = (
        "ECDHE+AESGCM:"
        "ECDHE+CHACHA20:"
        "DHE+AESGCM:"
        "DHE+CHACHA20:"
        "ECDH+AESGCM:"
        "DH+AESGCM:"
        "ECDH+AES:"
        "DH+AES:"
        "RSA+AESGCM:"
        "RSA+AES:"
        "!ECDHE+SHA:"
        "!AES128-SHA:"
        "!aNULL:"
        "!eNULL:"
        "!MD5:"
        "!DSS"
    )
