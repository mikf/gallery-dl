# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for http://www.keenspot.com/"""

from .common import Extractor, Message
from .. import text


class KeenspotComicExtractor(Extractor):
    """Extractor for webcomics from keenspot.com"""
    category = "keenspot"
    subcategory = "comic"
    directory_fmt = ("{category}", "{comic}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{comic}_{filename}"
    pattern = r"(?:https?://)?(?!www\.|forums\.)([\w-]+)\.keenspot\.com(/.+)?"
    example = "http://COMIC.keenspot.com/"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.comic = match.group(1).lower()
        self.path = match.group(2)
        self.root = "http://" + self.comic + ".keenspot.com"

        self._needle = ""
        self._image = 'class="ksc"'
        self._next = self._next_needle

    def items(self):
        data = {"comic": self.comic}
        yield Message.Directory, data

        with self.request(self.root + "/") as response:
            if response.history:
                url = response.request.url
                self.root = url[:url.index("/", 8)]
            page = response.text
            del response

        url = self._first(page)
        if self.path:
            url = self.root + self.path

        prev = None
        ilen = len(self._image)
        while url and url != prev:
            prev = url
            page = self.request(text.urljoin(self.root, url)).text

            pos = 0
            while True:
                pos = page.find(self._image, pos)
                if pos < 0:
                    break
                img, pos = text.extract(page, 'src="', '"', pos + ilen)
                if img.endswith(".js"):
                    continue
                if img[0] == "/":
                    img = self.root + img
                elif "youtube.com/" in img:
                    img = "ytdl:" + img
                yield Message.Url, img, text.nameext_from_url(img, data)

            url = self._next(page)

    def _first(self, page):
        if self.comic == "brawlinthefamily":
            self._next = self._next_brawl
            self._image = '<div id="comic">'
            return "http://brawlinthefamily.keenspot.com/comic/theshowdown/"

        url = text.extr(page, '<link rel="first" href="', '"')
        if url:
            if self.comic == "porcelain":
                self._needle = 'id="porArchivetop_"'
            else:
                self._next = self._next_link
            return url

        pos = page.find('id="first_day1"')
        if pos >= 0:
            self._next = self._next_id
            return text.rextract(page, 'href="', '"', pos)[0]

        pos = page.find('>FIRST PAGE<')
        if pos >= 0:
            if self.comic == "lastblood":
                self._next = self._next_lastblood
                self._image = '<div id="comic">'
            else:
                self._next = self._next_id
            return text.rextract(page, 'href="', '"', pos)[0]

        pos = page.find('<div id="kscomicpart"')
        if pos >= 0:
            self._needle = '<a href="/archive.html'
            return text.extract(page, 'href="', '"', pos)[0]

        pos = page.find('>First Comic<')  # twokinds
        if pos >= 0:
            self._image = '</header>'
            self._needle = 'class="navarchive"'
            return text.rextract(page, 'href="', '"', pos)[0]

        pos = page.find('id="flip_FirstDay"')  # flipside
        if pos >= 0:
            self._image = 'class="flip_Pages ksc"'
            self._needle = 'id="flip_ArcButton"'
            return text.rextract(page, 'href="', '"', pos)[0]

        self.log.error("Unrecognized page layout")
        return None

    def _next_needle(self, page):
        pos = page.index(self._needle) + len(self._needle)
        return text.extract(page, 'href="', '"', pos)[0]

    @staticmethod
    def _next_link(page):
        return text.extr(page, '<link rel="next" href="', '"')

    @staticmethod
    def _next_id(page):
        pos = page.find('id="next_')
        return text.rextract(page, 'href="', '"', pos)[0] if pos >= 0 else None

    @staticmethod
    def _next_lastblood(page):
        pos = page.index("link rel='next'")
        return text.extract(page, "href='", "'", pos)[0]

    @staticmethod
    def _next_brawl(page):
        pos = page.index("comic-nav-next")
        url = text.rextract(page, 'href="', '"', pos)[0]
        return None if "?random" in url else url
