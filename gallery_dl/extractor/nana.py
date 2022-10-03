# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nana.my.id/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, exception
import json


class NanaGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from nana.my.id"""
    category = "nana"
    directory_fmt = ("{category}", "{title}")
    pattern = r"(?:https?://)?nana\.my\.id/reader/([^/?#]+)"
    test = (
        (("https://nana.my.id/reader/"
          "059f7de55a4297413bfbd432ce7d6e724dd42bae"), {
            "pattern": r"https://nana\.my\.id/reader/"
                       r"\w+/image/page\?path=.*\.\w+",
            "title"  : "Everybody Loves Shion",
            "artist" : "fuzui",
            "tags"   : list,
            "count"  : 29,
        }),
        (("https://nana.my.id/reader/"
          "77c8712b67013e427923573379f5bafcc0c72e46"), {
            "pattern": r"https://nana\.my\.id/reader/"
                       r"\w+/image/page\?path=.*\.\w+",
            "title"  : "Lovey-Dovey With an Otaku-Friendly Gyaru",
            "artist" : "Sueyuu",
            "tags"   : ["Sueyuu"],
            "count"  : 58,
        }),
    )

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = "https://nana.my.id/reader/" + self.gallery_id
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        title = text.unescape(
            text.extract(page, '</a>&nbsp; ', '</div>')[0])
        artist = text.unescape(text.extract(
            page, '<title>', '</title>')[0])[len(title):-10]
        tags = text.extract(page, 'Reader.tags = "', '"')[0]

        return {
            "gallery_id": self.gallery_id,
            "title"     : title,
            "artist"    : artist[4:] if artist.startswith(" by ") else "",
            "tags"      : tags.split(", ") if tags else (),
            "lang"      : "en",
            "language"  : "English",
        }

    def images(self, page):
        data = json.loads(text.extract(page, "Reader.pages = ", ".pages")[0])
        return [
            ("https://nana.my.id" + image, None)
            for image in data["pages"]
        ]


class NanaSearchExtractor(Extractor):
    """Extractor for nana search results"""
    category = "nana"
    subcategory = "search"
    pattern = r"(?:https?://)?nana\.my\.id(?:/?\?([^#]+))"
    test = (
        ('https://nana.my.id/?q=+"elf"&sort=desc', {
            "pattern": NanaGalleryExtractor.pattern,
            "range": "1-100",
            "count": 100,
        }),
        ("https://nana.my.id/?q=favorites%3A", {
            "pattern": NanaGalleryExtractor.pattern,
            "count": ">= 2",
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.params = text.parse_query(match.group(1))
        self.params["p"] = text.parse_int(self.params.get("p"), 1)
        self.params["q"] = self.params.get("q") or ""

    def items(self):
        if "favorites:" in self.params["q"]:
            favkey = self.config("favkey")
            if not favkey:
                raise exception.AuthenticationError(
                    "'Favorite key' not provided. "
                    "Please see 'https://nana.my.id/tutorial'")
            self.session.cookies.set("favkey", favkey, domain="nana.my.id")

        data = {"_extractor": NanaGalleryExtractor}
        while True:
            try:
                page = self.request(
                    "https://nana.my.id", params=self.params).text
            except exception.HttpError:
                return

            for gallery in text.extract_iter(
                    page, '<div class="id3">', '</div>'):
                url = "https://nana.my.id" + text.extract(
                    gallery, '<a href="', '"')[0]
                yield Message.Queue, url, data

            self.params["p"] += 1
