# -*- coding: utf-8 -*-

# Copyright 2014-2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga chapters from https://bato.to/"""

from .common import Extractor, AsynchronousExtractor, Message
from .. import text, iso639_1, config, exception
from ..cache import cache
import re


class BatotoExtractor(Extractor):
    """Base class for batoto extractors"""
    category = "batoto"
    root = "https://bato.to"

    def login(self):
        """Login and set necessary cookies"""
        username = config.interpolate(("extractor", "batoto", "username"))
        password = config.interpolate(("extractor", "batoto", "password"))
        if username and password:
            cookies = self._login_impl(username, password)
            for key, value in cookies.items():
                self.session.cookies.set(
                    key, value, domain=".bato.to", path="/")

    @cache(maxage=360*24*60*60, keyarg=1)
    def _login_impl(self, username, password):
        """Actual login implementation"""
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
        return {c: response.cookies[c] for c in ("member_id", "pass_hash")}


class BatotoMangaExtractor(BatotoExtractor):
    """Extractor for mangas from bato.to"""
    subcategory = "manga"
    pattern = [r"(?:https?://)?(?:www\.)?bato\.to/comic/_/comics/.*-r\d+"]
    test = [("http://bato.to/comic/_/comics/aria-r2007", {
        "url": "a38585b0339587666d772ee06f2a60abdbf42a97",
    })]

    def __init__(self, match):
        BatotoExtractor.__init__(self)
        self.url = match.group(0)

    def items(self):
        self.login()
        yield Message.Version, 1
        for chapter in self.get_chapters():
            yield Message.Queue, chapter

    def get_chapters(self):
        """Return a list of all chapter urls"""
        # TODO: filter by language / translator
        needle = ('<td style="border-top:0;">\n           '
                  '<a href="http://bato.to/reader#')
        page = self.request(self.url).text
        return reversed([
            self.root + "/reader#" + mangahash
            for mangahash in text.extract_iter(page, needle, '"')
        ])


class BatotoChapterExtractor(BatotoExtractor, AsynchronousExtractor):
    """Extractor for manga-chapters from bato.to"""
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "c{chapter:>03} - {title}"]
    filename_fmt = "{manga}_c{chapter:>03}_{page:>03}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?bato\.to/reader#([0-9a-f]+)"]
    test = [
        ("http://bato.to/reader#459878c8fda07502", {
            "url": "432d7958506ad913b0a9e42664a89e46a63e9296",
            "keyword": "75a3a86d32aecfc21c44865b4043490757f73d77",
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
        response = self.session.get(self.reader_url, params=params)
        if response.status_code == 405:
            error = text.extract(response.text, "ERROR [", "]")[0]
            if error == "10030":
                raise exception.AuthorizationError()
            elif error == "10020":
                raise exception.NotFoundError("chapter")
            else:
                raise Exception("[batoto] unexpected error code: " + error)
        page = response.text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data.copy()
        for i in range(int(data["count"])):
            next_url, image_url = self.get_page_urls(page)
            text.nameext_from_url(image_url, data)
            data["page"] = i+1
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
        match = re.match(r"(Vol.(\d+) )?Ch\.([^:]+)(: (.+))?", cinfo)
        return {
            "token": self.token,
            "manga": text.unescape(manga),
            "volume": match.group(2) or "",
            "chapter": match.group(3),
            "title": match.group(5) or "",
            "group": group,
            "lang": iso639_1.language_to_code(lang),
            "language": lang,
            "count": count,
        }

    @staticmethod
    def get_page_urls(page):
        """Collect next- and image-url for one manga-page"""
        _   , pos = text.extract(page, 'title="Next Chapter"', '')
        nurl, pos = text.extract(page, '<a href="', '"', pos)
        _   , pos = text.extract(page, '<div id="full_image"', '', pos)
        iurl, pos = text.extract(page, '<img src="', '"', pos)
        return nurl if "_" in nurl else None, iurl
