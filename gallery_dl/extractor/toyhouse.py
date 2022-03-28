# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://toyhou.se/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?toyhou\.se"


class ToyhouseExtractor(Extractor):
    """Base class for toyhouse extractors"""
    category = "toyhouse"
    root = "https://toyhou.se"
    directory_fmt = ("{category}", "{user|artists!S}")
    archive_fmt = "{id}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)
        self.offset = 0

    def items(self):
        metadata = self.metadata()

        for post in util.advance(self.posts(), self.offset):
            if metadata:
                post.update(metadata)
            text.nameext_from_url(post["url"], post)
            post["id"], _, post["hash"] = post["filename"].partition("_")
            yield Message.Directory, post
            yield Message.Url, post["url"], post

    def posts(self):
        return ()

    def metadata(self):
        return None

    def skip(self, num):
        self.offset += num
        return num

    def _parse_post(self, post, needle='<a href="'):
        extr = text.extract_from(post)
        return {
            "url": extr(needle, '"'),
            "date": text.parse_datetime(extr(
                'Credits\n</h2>\n<div class="mb-1">', '<'),
                "%d %b %Y, %I:%M:%S %p"),
            "artists": [
                text.remove_html(artist)
                for artist in extr(
                    '<div class="artist-credit">', '</div>\n</div>').split(
                    '<div class="artist-credit">')
            ],
            "characters": text.split_html(extr(
                '<div class="image-characters', '</div>\n</div>'))[2:],
        }

    def _pagination(self, path):
        url = self.root + path
        params = {"page": 1}

        while True:
            page = self.request(url, params=params).text

            cnt = 0
            for post in text.extract_iter(
                    page, '<li class="gallery-item">', '</li>'):
                cnt += 1
                yield self._parse_post(post)

            if cnt == 0 and params["page"] == 1:
                token, pos = text.extract(
                    page, '<input name="_token" type="hidden" value="', '"')
                if not token:
                    return
                data = {
                    "_token": token,
                    "user"  : text.extract(page, 'value="', '"', pos)[0],
                }
                self.request(self.root + "/~account/warnings/accept",
                             method="POST", data=data, allow_redirects=False)
                continue

            if cnt < 18:
                return
            params["page"] += 1


class ToyhouseArtExtractor(ToyhouseExtractor):
    """Extractor for artworks of a toyhouse user"""
    subcategory = "art"
    pattern = BASE_PATTERN + r"/([^/?#]+)/art"

    test = (
        ("https://www.toyhou.se/d-floe/art", {
            "range": "1-30",
            "count": 30,
            "pattern": r"https://f\d+\.toyhou\.se/file/f\d+-toyhou-se"
                       r"/images/\d+_\w+\.\w+$",
            "keyword": {
                "artists": list,
                "characters": list,
                "date": "type:datetime",
                "hash": r"re:\w+",
                "id": r"re:\d+",
                "url": str,
                "user": "d-floe",
            },
        }),
        # protected by Content Warning
        ("https://www.toyhou.se/kroksoc/art", {
            "count": ">= 19",
        }),
    )

    def posts(self):
        return self._pagination("/{}/art".format(self.user))

    def metadata(self):
        return {"user": self.user}


class ToyhouseImageExtractor(ToyhouseExtractor):
    """Extractor for individual toyhouse images"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:"
               r"(?:www\.)?toyhou\.se/~images|"
               r"f\d+\.toyhou\.se/file/[^/?#]+/(?:image|watermark)s"
               r")/(\d+)")
    test = (
        ("https://toyhou.se/~images/40587320", {
            "content": "058ec8427977ab432c4cc5be5a6dd39ce18713ef",
            "keyword": {
                "artists": ["d-floe"],
                "characters": ["Sumi"],
                "date": "dt:2021-10-08 01:32:47",
                "extension": "png",
                "filename": "40587320_TT1NaBUr3FLkS1p",
                "hash": "TT1NaBUr3FLkS1p",
                "id": "40587320",
                "url": "https://f2.toyhou.se/file/f2-toyhou-se/images"
                       "/40587320_TT1NaBUr3FLkS1p.png",
            },
        }),
        # direct link, multiple artists
        (("https://f2.toyhou.se/file/f2-toyhou-se"
          "/watermarks/36817425_bqhGcwcnU.png?1625561467"), {
            "keyword": {
                "artists": [
                    "http://aminoapps.com/p/92sf3z",
                    "kroksoc (Color)"],
                "characters": ["❀Reiichi❀"],
                "date": "dt:2021-07-03 20:02:02",
                "hash": "bqhGcwcnU",
                "id": "36817425",
            },
        }),
        ("https://f2.toyhou.se/file/f2-toyhou-se"
         "/images/40587320_TT1NaBUr3FLkS1p.png"),
    )

    def posts(self):
        url = "{}/~images/{}".format(self.root, self.user)
        return (self._parse_post(self.request(url).text, '<img src="'),)
