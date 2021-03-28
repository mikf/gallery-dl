# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.erome.com/"""

from .common import Extractor, Message
from .. import text, util
from ..cache import cache
import itertools
import time

BASE_PATTERN = r"(?:https?://)?(?:www\.)?erome\.com"


class EromeExtractor(Extractor):
    category = "erome"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{album_id} {title} {num:>02}.{extension}"
    archive_fmt = "{album_id}_{num}"
    root = "https://www.erome.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.item = match.group(1)
        self.__cookies = True

    def items(self):
        for album_id in self.albums():
            url = "{}/a/{}".format(self.root, album_id)
            page = self.request(url).text

            title, pos = text.extract(
                page, 'property="og:title" content="', '"')
            pos = page.index('<div class="user-profile', pos)
            user, pos = text.extract(
                page, 'href="https://www.erome.com/', '"', pos)
            data = {
                "album_id": album_id,
                "title"   : text.unescape(title),
                "user"    : text.unquote(user),
            }

            yield Message.Directory, data
            groups = page.split('<div class="media-group"')
            for data["num"], group in enumerate(util.advance(groups, 1), 1):
                url = (text.extract(group, '<source src="', '"')[0] or
                       text.extract(group, 'data-src="', '"')[0])
                if url:
                    yield Message.Url, url, text.nameext_from_url(url, data)

    def albums(self):
        return ()

    def request(self, url, **kwargs):
        if self.__cookies:
            self.__cookies = False
            self.session.cookies.update(_cookie_cache())

        for _ in range(5):
            response = Extractor.request(self, url, **kwargs)
            if response.cookies:
                _cookie_cache.update("", response.cookies)
            if response.content.find(
                    b"<title>Please wait a few moments</title>", 0, 600) < 0:
                return response
            time.sleep(5)

    def _pagination(self, url, params):
        for params["page"] in itertools.count(1):
            page = self.request(url, params=params).text

            album_ids = EromeAlbumExtractor.pattern.findall(page)
            yield from album_ids

            if len(album_ids) < 36:
                return


class EromeAlbumExtractor(EromeExtractor):
    """Extractor for albums on erome.com"""
    subcategory = "album"
    pattern = BASE_PATTERN + r"/a/(\w+)"
    test = ("https://www.erome.com/a/TyFMI7ik", {
        "pattern": r"https://s\d+\.erome\.com/\d+/TyFMI7ik/\w+",
        "count": 9,
        "keyword": {
            "album_id": "TyFMI7ik",
            "num": int,
            "title": "Ryan Ryans",
            "user": "xanub",
        },
    })

    def albums(self):
        return (self.item,)


class EromeUserExtractor(EromeExtractor):
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!a/|search\?)([^/?#]+)"
    test = ("https://www.erome.com/xanub", {
        "range": "1-25",
        "count": 25,
    })

    def albums(self):
        url = "{}/{}".format(self.root, self.item)
        return self._pagination(url, {})


class EromeSearchExtractor(EromeExtractor):
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search\?q=([^&#]+)"
    test = ("https://www.erome.com/search?q=cute", {
        "range": "1-25",
        "count": 25,
    })

    def albums(self):
        url = self.root + "/search"
        params = {"q": text.unquote(self.item)}
        return self._pagination(url, params)


@cache()
def _cookie_cache():
    return ()
