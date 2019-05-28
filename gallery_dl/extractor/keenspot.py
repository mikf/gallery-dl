# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
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
    pattern = r"(?:https?://)?(?!www\.|forums\.)([^.]+)\.keenspot\.com"
    test = (
        ("http://marksmen.keenspot.com/", {  # link
            "range": "1-3",
            "url": "83bcf029103bf8bc865a1988afa4aaeb23709ba6",
        }),
        ("http://barkercomic.keenspot.com/", {  # id
            "range": "1-3",
            "url": "c4080926db18d00bac641fdd708393b7d61379e6",
        }),
        ("http://crowscare.keenspot.com/", {  # id v2
            "range": "1-3",
            "url": "a00e66a133dd39005777317da90cef921466fcaa"
        }),
        ("http://supernovas.keenspot.com/", {  # ks
            "range": "1-3",
            "url": "de21b12887ef31ff82edccbc09d112e3885c3aab"
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self._next = None
        self.comic = match.group(1)
        self.root = "http://" + self.comic + ".keenspot.com"

    def items(self):
        data = {"comic": self.comic}
        yield Message.Version, 1
        yield Message.Directory, data

        url = self._first(self.request(self.root + "/").text)
        while url:
            if url[0] == "/":
                url = self.root + url
            page = self.request(url).text

            for img in text.extract_iter(page, 'class="ksc"', '>'):
                img = text.extract(img, 'src="', '"')[0]
                if img[0] == "/":
                    img = self.root + img
                yield Message.Url, img, text.nameext_from_url(img, data)

            url = self._next(page)

    def _first(self, page):
        url = text.extract(page, '<link rel="first" href="', '"')[0]
        if url and not url.startswith("index"):
            self._next = self._next_link
            return url

        pos = page.find('id="first_day1"')
        if pos >= 0:
            self._next = self._next_id
            return text.rextract(page, '<a href="', '"', pos)[0]

        pos = page.find('>FIRST PAGE<')
        if pos >= 0:
            self._next = self._next_id
            return text.rextract(page, '<a href="', '"', pos)[0]

        pos = page.find('<div id="kscomicpart"')
        if pos >= 0:
            self._next = self._next_ks
            return text.extract(page, 'href="', '"', pos)[0]

        self.log.error("Unrecognized page layout")
        return None

    @staticmethod
    def _next_link(page):
        return text.extract(page, '<link rel="next" href="', '"')[0]

    @staticmethod
    def _next_id(page):
        pos = page.find('id="next_')
        return text.rextract(page, 'href="', '"', pos)[0] if pos >= 0 else None

    @staticmethod
    def _next_ks(page):
        pos = page.index('<a href="/archive.html') + 22
        return text.extract(page, 'href="', '"', pos)[0]
