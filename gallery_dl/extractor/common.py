# -*- coding: utf-8 -*-

# Copyright 2014-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by extractor modules."""

import os
import re
import time
import netrc
import queue
import logging
import requests
import threading
import http.cookiejar
from .message import Message
from .. import config, text, exception


class Extractor():

    category = ""
    subcategory = ""
    categorytransfer = False
    directory_fmt = ["{category}"]
    filename_fmt = "{name}.{extension}"
    archive_fmt = ""
    cookiedomain = ""

    def __init__(self):
        self.session = requests.Session()
        self.log = logging.getLogger(self.category)
        self._set_headers()
        self._set_cookies()
        self._set_proxies()
        self._retries = self.config("retries", 5)
        self._timeout = self.config("timeout", 30)
        self._verify = self.config("verify", True)

    def __iter__(self):
        return self.items()

    def items(self):
        yield Message.Version, 1

    def skip(self, num):
        return 0

    def config(self, key, default=None):
        return config.interpolate(
            ("extractor", self.category, self.subcategory, key), default)

    def request(self, url, method="GET", *,
                encoding=None, expect=(), retries=None, **kwargs):
        tries = 0
        retries = retries or self._retries
        kwargs.setdefault("timeout", self._timeout)
        kwargs.setdefault("verify", self._verify)

        while True:
            try:
                response = self.session.request(method, url, **kwargs)
            except (requests.ConnectionError, requests.Timeout) as exc:
                msg = exc
            except requests.exceptions.RequestException as exc:
                raise exception.HttpError(exc)
            else:
                code = response.status_code
                if 200 <= code < 400 or code in expect:
                    if encoding:
                        response.encoding = encoding
                    return response

                msg = "{}: {} for url: {}".format(code, response.reason, url)
                if code < 500 and code != 429:
                    break

            self.log.debug("%s (%d/%d)", msg, tries + 1, retries)
            if tries >= retries:
                break
            time.sleep(2 ** tries)
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

    def _set_headers(self):
        """Set additional headers for the 'session' object"""
        self.session.headers["Accept-Language"] = "en-US,en;q=0.5"
        self.session.headers["User-Agent"] = self.config(
            "user-agent", ("Mozilla/5.0 (X11; Linux x86_64; rv:62.0) "
                           "Gecko/20100101 Firefox/62.0"))

    def _set_cookies(self):
        """Populate the session's cookiejar"""
        cookies = self.config("cookies")
        if cookies:
            if isinstance(cookies, dict):
                setcookie = self.session.cookies.set
                for name, value in cookies.items():
                    setcookie(name, value, domain=self.cookiedomain)
            else:
                try:
                    cj = http.cookiejar.MozillaCookieJar()
                    cj.load(cookies)
                    self.session.cookies.update(cj)
                except OSError as exc:
                    self.log.warning("cookies: %s", exc)

    def _set_proxies(self):
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

    def _check_cookies(self, cookienames, domain=None):
        """Check if all 'cookienames' are in the session's cookiejar"""
        if not domain and self.cookiedomain:
            domain = self.cookiedomain
        for name in cookienames:
            try:
                self.session.cookies._find(name, domain)
            except KeyError:
                return False
        return True


class AsynchronousExtractor(Extractor):

    def __init__(self):
        Extractor.__init__(self)
        queue_size = int(config.get(("queue-size",), 5))
        self.__queue = queue.Queue(queue_size)
        self.__thread = threading.Thread(target=self.async_items, daemon=True)

    def __iter__(self):
        get = self.__queue.get
        done = self.__queue.task_done

        self.__thread.start()
        while True:
            task = get()
            if task is None:
                return
            if isinstance(task, Exception):
                raise task
            yield task
            done()

    def async_items(self):
        put = self.__queue.put
        try:
            for task in self.items():
                put(task)
        except Exception as exc:
            put(exc)
        put(None)


class ChapterExtractor(Extractor):

    subcategory = "chapter"
    directory_fmt = [
        "{category}", "{manga}",
        "{volume:?v/ />02}c{chapter:>03}{chapter_minor:?//}{title:?: //}"]
    filename_fmt = (
        "{manga}_c{chapter:>03}{chapter_minor:?//}_{page:>03}.{extension}")
    archive_fmt = (
        "{manga}_{chapter}{chapter_minor}_{page}")

    def __init__(self, url):
        Extractor.__init__(self)
        self.url = url

    def items(self):
        page = self.request(self.url).text
        data = self.get_metadata(page)
        imgs = self.get_images(page)

        if "count" in data:
            images = zip(
                range(1, data["count"]+1),
                imgs
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

    def get_metadata(self, page):
        """Return a dict with general metadata"""

    def get_images(self, page):
        """Return a list of all (image-url, metadata)-tuples"""


class MangaExtractor(Extractor):

    subcategory = "manga"
    categorytransfer = True
    scheme = "http"
    root = ""
    reverse = True

    def __init__(self, match, url=None):
        Extractor.__init__(self)
        self.url = url or self.scheme + "://" + match.group(1)

    def items(self):
        page = self.request(self.url).text

        chapters = self.chapters(page)
        if self.reverse:
            chapters.reverse()

        yield Message.Version, 1
        for chapter, data in chapters:
            yield Message.Queue, chapter, data

    def chapters(self, page):
        """Return a list of all (chapter-url, metadata)-tuples"""


class SharedConfigExtractor(Extractor):

    basecategory = ""

    def config(self, key, default=None, sentinel=object()):
        value = Extractor.config(self, key, sentinel)
        if value is sentinel:
            cat, self.category = self.category, self.basecategory
            value = Extractor.config(self, key, default)
            self.category = cat
        return value


# Reduce strictness of the expected magic string in cookiejar files.
# (This allows the use of Wget-generated cookiejars without modification)

http.cookiejar.MozillaCookieJar.magic_re = re.compile(
    "#( Netscape)? HTTP Cookie File", re.IGNORECASE)


# The first import of requests happens inside this file.
# If we are running on Windows and the from requests expected certificate file
# is missing (which happens in a standalone executable from py2exe), the
# requests.Session object gets monkey patched to always set its 'verify'
# attribute to False to avoid an exception being thrown when attempting to
# access https:// URLs.

if os.name == "nt":
    import os.path
    import requests.certs
    import requests.packages.urllib3 as ulib3
    if not os.path.isfile(requests.certs.where()):
        def patched_init(self):
            session_init(self)
            self.verify = False
        session_init = requests.Session.__init__
        requests.Session.__init__ = patched_init
        ulib3.disable_warnings(ulib3.exceptions.InsecureRequestWarning)
