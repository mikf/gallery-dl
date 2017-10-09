# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga chapters from https://bato.to/"""

from .common import MangaExtractor, AsynchronousExtractor, Message
from .. import text, util, exception
from ..cache import cache
import re


class BatotoExtractor():
    """Base class for batoto extractors"""
    category = "batoto"
    scheme = "https"
    root = "https://bato.to"
    cookienames = ("member_id", "pass_hash")
    cookiedomain = ".bato.to"

    def login(self):
        """Login and set necessary cookies"""
        if self._check_cookies(self.cookienames):
            return
        username, password = self._get_auth_info()
        if username:
            cookies = self._login_impl(username, password)
            for key, value in cookies.items():
                self.session.cookies.set(
                    key, value, domain=self.cookiedomain)

    @cache(maxage=7*24*60*60, keyarg=1)
    def _login_impl(self, username, password):
        """Actual login implementation"""
        self.log.info("Logging in as %s", username)
        page = self.request(self.root).text
        auth = text.extract(page, "name='auth_key' value='", "'")[0]
        params = {
            "app": "core",
            "module": "global",
            "section": "login",
            "do": "process",
        }
        data = {
            "auth_key": auth,
            "referer": self.root,
            "ips_username": username,
            "ips_password": password,
            "rememberMe": "1",
            "anonymous": "1",
        }
        response = self.request(self.root + "/forums/index.php",
                                method="POST", params=params, data=data)
        if "Sign In - " in response.text:
            raise exception.AuthenticationError()
        return {c: response.cookies[c] for c in self.cookienames}

    @staticmethod
    def parse_chapter_string(data):
        """Parse 'chapter_string' value contained in 'data'"""
        data["chapter_string"] = text.unescape(data["chapter_string"])
        pattern = r"(?:Vol\.(\d+) )?Ch\.(\d+)([^ :]*)(?::? (.+))"
        match = re.match(pattern, data["chapter_string"])

        volume, chapter, data["chapter_minor"], title = match.groups()
        data["volume"] = util.safe_int(volume)
        data["chapter"] = util.safe_int(chapter)
        data["title"] = title if title != "Read Online" else ""
        return data


class BatotoMangaExtractor(BatotoExtractor, MangaExtractor):
    """Extractor for manga from bato.to"""
    pattern = [r"(?:https?://)?(?:www\.)?(bato\.to"
               r"/comic/_/comics/[^/?&#]*-r\d+)"]
    test = [("http://bato.to/comic/_/comics/aria-r2007", {
        "url": "a38585b0339587666d772ee06f2a60abdbf42a97",
        "keyword": "c33ea7b97e3714530384e2411fae62ae51aae50d",
    })]

    def chapters(self, page):
        pos = 0
        results = []
        page = text.extract(
            page, '<h3 class="maintitle">Chapters</h3>', '</tbody>')[0]

        while True:
            data, pos = text.extract_all(page, (
                ("language"   , '<tr class="row lang_', ' '),
                ("token"      , '/reader#', '"'),
                ("chapter_string", 'title="', ' | Sort: '),
                (None         , '<a href="https://bato.to/group/', ''),
                ("group"      , '>', '<'),
                (None         , '<a href="https://bato.to/forums/user/', ''),
                ("contributor", '>', '<'),
            ), pos)

            if not data["token"]:
                return results

            self.parse_chapter_string(data)
            data["lang"] = util.language_to_code(data["language"])
            data["group"] = text.unescape(data["group"])
            data["contributor"] = text.unescape(data["contributor"])
            url = self.root + "/reader#" + data["token"]

            results.append((url, data))


class BatotoChapterExtractor(BatotoExtractor, AsynchronousExtractor):
    """Extractor for manga-chapters from bato.to"""
    subcategory = "chapter"
    directory_fmt = [
        "{category}", "{manga}",
        "{volume:?v/ />02}c{chapter:>03}{chapter_minor}{title:?: //}"]
    filename_fmt = (
        "{manga}_c{chapter:>03}{chapter_minor}_{page:>03}.{extension}")
    pattern = [r"(?:https?://)?(?:www\.)?bato\.to/reader#([0-9a-f]+)"]
    test = [
        ("http://bato.to/reader#459878c8fda07502", {
            "url": "432d7958506ad913b0a9e42664a89e46a63e9296",
            "keyword": "96598b6f94d2b26d11c2780f8173cd6ab5fe9906",
        }),
        ("http://bato.to/reader#459878c8fda07503", {
            "exception": exception.NotFoundError,
        }),
    ]
    reader_url = "https://bato.to/areader"

    def __init__(self, match):
        super().__init__()
        self.token = match.group(1)

    def items(self):
        self.login()
        self.session.headers.update({
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.root + "/reader",
        })
        params = {
            "id": self.token,
            "p": 1,
            "supress_webtoon": "t",
        }
        response = self.request(self.reader_url, params=params, fatal=False)
        if response.status_code == 405:
            error = text.extract(response.text, "ERROR [", "]")[0]
            if error == "10030":
                raise exception.AuthorizationError()
            elif error == "10020":
                raise exception.NotFoundError("chapter")
            else:
                raise Exception("error code: " + error)
        page = response.text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data.copy()
        for data["page"] in range(1, data["count"]+1):
            next_url, image_url = self.get_page_urls(page)
            text.nameext_from_url(image_url, data)
            yield Message.Url, image_url, data.copy()
            if next_url:
                params["p"] += 1
                page = self.request(self.reader_url, params=params).text

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        extr = text.extract
        _    , pos = extr(page, '<select name="chapter_select"', '')
        cinfo, pos = extr(page, 'selected="selected">', '</option>', pos)
        _    , pos = extr(page, '<select name="group_select"', '', pos)
        group, pos = extr(page, 'selected="selected">', ' - ', pos)
        lang , pos = extr(page, '', '</option>', pos)
        _    , pos = extr(page, '<select name="page_select"', '', pos)
        _    , pos = extr(page, '</select>', '', pos)
        count, pos = extr(page, '>page ', '<', pos-35)
        manga, pos = extr(page, "document.title = '", " - ", pos)
        data = {
            "token": self.token,
            "manga": text.unescape(manga),
            "chapter_string": cinfo,
            "group": text.unescape(group),
            "lang": util.language_to_code(lang),
            "language": lang,
            "count": util.safe_int(count),
        }
        return self.parse_chapter_string(data)

    @staticmethod
    def get_page_urls(page):
        """Collect next- and image-url for one manga-page"""
        _   , pos = text.extract(page, 'title="Next Chapter"', '')
        nurl, pos = text.extract(page, '<a href="', '"', pos)
        _   , pos = text.extract(page, '<div id="full_image"', '', pos)
        iurl, pos = text.extract(page, '<img src="', '"', pos)
        return nurl if "_" in nurl else None, iurl
