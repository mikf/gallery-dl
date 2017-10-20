# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
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
from .. import config, exception


class Extractor():

    category = ""
    subcategory = ""
    categorytransfer = False
    directory_fmt = ["{category}"]
    filename_fmt = "{filename}"
    cookiedomain = ""

    def __init__(self):
        self.session = requests.Session()
        self.log = logging.getLogger(self.category)
        self._set_cookies(self.config("cookies"))

    def __iter__(self):
        return self.items()

    def items(self):
        yield Message.Version, 1

    def skip(self, num):
        return 0

    def config(self, key, default=None):
        return config.interpolate(
            ("extractor", self.category, self.subcategory, key), default)

    def request(self, url, method="GET", encoding=None, fatal=True, retries=3,
                allow_empty=False, *args, **kwargs):
        max_retries = retries
        while True:
            try:
                response = None
                response = self.session.request(method, url, *args, **kwargs)
                if fatal:
                    response.raise_for_status()
                if encoding:
                    response.encoding = encoding
                if response.content or allow_empty:
                    return response
                msg = "empty response body"
            except requests.exceptions.RequestException as exc:
                msg = exc
            if not retries:
                raise exception.HttpError(msg)
            if response and response.status_code == 429:  # Too Many Requests
                waittime = float(response.headers.get("Retry-After", 10.0))
            else:
                waittime = 1
            retries -= 1
            time.sleep(waittime * (max_retries - retries))

    def _get_auth_info(self):
        """Return authentication information as (username, password) tuple"""
        username = self.config("username")
        password = None

        if username:
            password = self.config("password")
        elif config.get(("netrc",), False):
            try:
                info = netrc.netrc().authenticators(self.category)
                username, _, password = info
            except (OSError, netrc.NetrcParseError) as exc:
                self.log.error("netrc: %s", exc)
            except TypeError:
                self.log.warning("netrc: No authentication info")

        return username, password

    def _set_cookies(self, cookies):
        """Populate the cookiejar with 'cookies'"""
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
        self.login()
        page = self.request(self.url).text

        chapters = self.chapters(page)
        if self.reverse:
            chapters.reverse()

        yield Message.Version, 1
        for chapter, data in chapters:
            yield Message.Queue, chapter, data

    def login(self):
        """Login and set necessary cookies"""

    def chapters(self, page):
        """Return a list of all (url, metadata)-tuples"""
        return []


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
