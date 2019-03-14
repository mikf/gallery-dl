# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://mangadex.org/"""

from .common import Extractor, Message
from .. import text, util
from ..cache import memcache


class MangadexExtractor(Extractor):
    """Base class for mangadex extractors"""
    category = "mangadex"
    root = "https://mangadex.org"

    # mangadex-to-iso639-1 codes
    iso639_map = {
        "br": "pt",
        "ct": "ca",
        "gb": "en",
        "vn": "vi",
    }

    def chapter_data(self, chapter_id):
        """Request API results for 'chapter_id'"""
        url = "{}/api/chapter/{}".format(self.root, chapter_id)
        return self.request(url).json()

    @memcache(keyarg=1)
    def manga_data(self, manga_id):
        """Request API results for 'manga_id'"""
        url = "{}/api/manga/{}".format(self.root, manga_id)
        return self.request(url).json()


class MangadexChapterExtractor(MangadexExtractor):
    """Extractor for manga-chapters from mangadex.org"""
    subcategory = "chapter"
    directory_fmt = (
        "{category}", "{manga}",
        "{volume:?v/ />02}c{chapter:>03}{chapter_minor}{title:?: //}")
    filename_fmt = (
        "{manga}_c{chapter:>03}{chapter_minor}_{page:>03}.{extension}")
    archive_fmt = "{chapter_id}_{page}"
    pattern = r"(?:https?://)?(?:www\.)?mangadex\.(?:org|com)/chapter/(\d+)"
    test = (
        ("https://mangadex.org/chapter/122094", {
            "keyword": "1c834dca33025f521e1874aee1f71c51e28ebf99",
            "content": "7ab3bef5caccb62b881f8e6e70359d3c7be8137f",
        }),
        # oneshot
        ("https://mangadex.org/chapter/138086", {
            "count": 64,
            "keyword": "178777bd0352fb19eb934cbee5630d16e3fb60ab",
        }),
    )

    def __init__(self, match):
        MangadexExtractor.__init__(self, match)
        self.chapter_id = match.group(1)
        self.data = None

    def items(self):
        data = self.metadata()
        imgs = self.images()
        data["count"] = len(imgs)

        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"], url in enumerate(imgs, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def metadata(self):
        """Return a dict with general metadata"""
        cdata = self.chapter_data(self.chapter_id)
        mdata = self.manga_data(cdata["manga_id"])
        self.data = cdata

        chapter, sep, minor = cdata["chapter"].partition(".")
        return {
            "manga": mdata["manga"]["title"],
            "manga_id": cdata["manga_id"],
            "artist": mdata["manga"]["artist"],
            "author": mdata["manga"]["author"],
            "title": text.unescape(cdata["title"]),
            "volume": text.parse_int(cdata["volume"]),
            "chapter": text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_id": cdata["id"],
            "group": mdata["chapter"][self.chapter_id]["group_name"],
            "date": cdata["timestamp"],
            "lang": util.language_to_code(cdata["lang_name"]),
            "language": cdata["lang_name"],
        }

    def images(self):
        """Return a list of all image URLs"""
        base = self.data["server"] + self.data["hash"] + "/"
        if base.startswith("/"):
            base = text.urljoin(self.root, base)
        return [base + page for page in self.data["page_array"]]


class MangadexMangaExtractor(MangadexExtractor):
    """Extractor for manga from mangadex.org"""
    subcategory = "manga"
    categorytransfer = True
    pattern = (r"(?:https?://)?(?:www\.)?mangadex\.(?:org|com)"
               r"/(?:title|manga)/(\d+)")
    test = (
        ("https://mangadex.org/manga/2946/souten-no-koumori", {
            "pattern": r"https://mangadex.org/chapter/\d+",
            "keywords": {
                "manga": "Souten no Koumori",
                "manga_id": 2946,
                "title": "Oneshot",
                "volume": 0,
                "chapter": 0,
                "chapter_minor": "",
                "chapter_id": int,
                "group": str,
                "date": int,
                "lang": str,
                "language": str,
            },
        }),
        ("https://mangadex.org/manga/13318/dagashi-kashi/chapters/2/", {
            "count": ">= 100",
        }),
        ("https://mangadex.org/title/13004/yorumori-no-kuni-no-sora-ni", {
            "count": 0,
        }),
        ("https://mangadex.org/title/2946/souten-no-koumori"),
    )

    def __init__(self, match):
        MangadexExtractor.__init__(self, match)
        self.manga_id = text.parse_int(match.group(1))

    def items(self):
        yield Message.Version, 1
        for data in self.chapters():
            url = "{}/chapter/{}".format(self.root, data["chapter_id"])
            yield Message.Queue, url, data

    def chapters(self):
        """Return a sorted list of chapter-metadata dicts"""
        data = self.manga_data(self.manga_id)
        if "chapter" not in data:
            return ()
        manga = data["manga"]

        results = []
        for chid, info in data["chapter"].items():
            chapter, sep, minor = info["chapter"].partition(".")
            lang = self.iso639_map.get(info["lang_code"], info["lang_code"])
            results.append({
                "manga": manga["title"],
                "manga_id": self.manga_id,
                "artist": manga["artist"],
                "author": manga["author"],
                "title": text.unescape(info["title"]),
                "volume": text.parse_int(info["volume"]),
                "chapter": text.parse_int(chapter),
                "chapter_minor": sep + minor,
                "chapter_id": text.parse_int(chid),
                "group": text.unescape(info["group_name"]),
                "date": info["timestamp"],
                "lang": lang,
                "language": util.code_to_language(lang),
                "_extractor": MangadexChapterExtractor,
            })

        results.sort(key=lambda x: (x["chapter"], x["chapter_minor"]))
        return results
