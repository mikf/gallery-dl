# -*- coding: utf-8 -*-

# Copyright 2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentaihand.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util
import collections


class HentaihandGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries on hentaihand.com"""
    category = "hentaihand"
    root = "https://hentaihand.com"
    pattern = (r"(?i)(?:https?://)?(?:www\.)?hentaihand\.com"
               r"/(?:comi|view)c/(\d+)")
    test = (
        ("https://hentaihand.com/comic/272772/kouda-tomohiro-chiyomi-bl", {
            "pattern": r"https://i.hentaihand.com/.*/images/full/\d+.jpg$",
            "count": 19,
            "keyword": {
                "artists"   : ["kouda tomohiro"],
                "categories": ["manga"],
                "date"      : "Feb. 6, 2020, 3:19 p.m.",
                "gallery_id": 272772,
                "lang"      : "en",
                "language"  : "English",
                "relationships": ["family", "step family"],
                "tags"      : list,
                "title"     : r"re:\[Kouda Tomohiro\] Chiyomi Blizzard",
                "title_jp"  : r"re:\[幸田朋弘\] ちよみブリザード",
            },
        }),
        ("https://hentaihand.com/viewc/272772/kouda-tomohiro-chiyomi-bl"),
    )

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = "{}/comic/{}".format(self.root, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)

        title_en = text.unescape(extr("<h1>", "<"))
        title_jp = text.unescape(extr("<h2>", "<"))
        tags = extr('<section id="tags"', "</section>")

        data = {
            "gallery_id" : text.parse_int(self.gallery_id),
            "title"      : title_en or title_jp,
            "title_en"   : title_en,
            "title_jp"   : title_jp,

            # impossible to parse with strptime()
            "date"       : extr('datetime="', '"'),
        }

        tdict = collections.defaultdict(list)
        for path in text.extract_iter(tags, 'href="/', '"'):
            kind, _, name = path.partition("/")
            tdict[kind].append(name.replace("+", " "))
        data.update(tdict)

        if "languages" in data:
            data["language"] = data["languages"][-1].capitalize()
            data["lang"] = util.language_to_code(data["language"])
            del data["languages"]
        return data

    def images(self, _):
        url = "{}/viewc/{}/1".format(self.root, self.gallery_id)
        page = self.request(url).text
        images = text.extract(page, "var images", ";")[0]
        return [(img, None) for img in text.extract_iter(images, "'", "'")]


class HentaihandTagExtractor(Extractor):
    """Extractor for tag searches on hentaihand.com"""
    category = "hentaihand"
    subcategory = "tag"
    root = "https://hentaihand.com"
    pattern = (r"(?i)(?:https?://)?(?:www\.)?hentaihand\.com"
               r"(/(?:parody|characters|tags|artists|groups|languages"
               r"|categories|relationships)/[^#]+)")
    test = (
        ("https://hentaihand.com/artists/tony+taka", {
            "pattern": HentaihandGalleryExtractor.pattern,
            "count": ">= 50",
        }),
        ("https://hentaihand.com/artists/tony+taka/popular?page=2"),
        ("https://hentaihand.com/tags/full+color"),
        ("https://hentaihand.com/languages/japanese"),
        ("https://hentaihand.com/categories/manga"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path, _, query = match.group(1).partition("?")
        self.query = text.parse_query(query)
        self.query["page"] = text.parse_int(self.query.get("page"), 1)

    def items(self):
        yield Message.Version, 1
        url = self.root + self.path
        params = self.query.copy()
        data = {"_extractor": HentaihandGalleryExtractor}

        while True:
            page = self.request(url, params=params).text

            for path in text.extract_iter(page, '<a href="/comic/', '"'):
                yield Message.Queue, self.root + "/comic/" + path, data

            pos = page.find(">(current)<")
            if pos < 0 or page.find('class="page-link" href="', pos) < 0:
                break
            params["page"] += 1


class HentaihandSearchExtractor(HentaihandTagExtractor):
    """Extractor for search results on hentaihand.com"""
    subcategory = "search"
    pattern = r"(?i)(?:https?://)?(?:www\.)?hentaihand\.com(/search/?[^#]+)"
    test = ("https://hentaihand.com/search?q=color", {
        "pattern": HentaihandGalleryExtractor.pattern,
        "range": "1-50",
        "count": 50,
    })
