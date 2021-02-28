# -*- coding: utf-8 -*-

# Copyright 2018-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangadex.org/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import memcache


class MangadexExtractor(Extractor):
    """Base class for mangadex extractors"""
    category = "mangadex"
    root = "https://mangadex.org"
    api_root = "https://api.mangadex.org"

    # mangadex-to-iso639-1 codes
    iso639_map = {
        "br": "pt",
        "ct": "ca",
        "gb": "en",
        "vn": "vi",
    }

    def __init__(self, match):
        Extractor.__init__(self, match)

        server = self.config("api-server")
        if server is not None:
            self.api_root = server.rstrip("/")

    def chapter_data(self, chapter_id):
        """Request API results for 'chapter_id'"""
        url = "{}/v2/chapter/{}".format(self.api_root, chapter_id)
        return self.request(url).json()["data"]

    @memcache(keyarg=1)
    def manga_data(self, manga_id):
        """Request API results for 'manga_id'"""
        url = "{}/v2/manga/{}".format(self.api_root, manga_id)
        return self.request(url).json()["data"]

    def manga_chapters(self, manga_id):
        """Request chapter list for 'manga_id'"""
        url = "{}/v2/manga/{}/chapters".format(self.api_root, manga_id)
        data = self.request(url).json()["data"]

        groups = {
            group["id"]: group["name"]
            for group in data["groups"]
        }

        for chapter in data["chapters"]:
            cgroups = chapter["groups"]
            for idx, group_id in enumerate(cgroups):
                cgroups[idx] = groups[group_id]
            yield chapter


class MangadexChapterExtractor(MangadexExtractor):
    """Extractor for manga-chapters from mangadex.org"""
    subcategory = "chapter"
    directory_fmt = (
        "{category}", "{manga}",
        "{volume:?v/ />02}c{chapter:>03}{chapter_minor}{title:?: //}")
    filename_fmt = (
        "{manga}_c{chapter:>03}{chapter_minor}_{page:>03}.{extension}")
    archive_fmt = "{chapter_id}_{page}"
    pattern = r"(?:https?://)?(?:www\.)?mangadex\.(?:org|cc)/chapter/(\d+)"
    test = (
        ("https://mangadex.org/chapter/122094", {
            "keyword": "89d1b24b4baa1fb737d32711d9f2ade6ea426987",
            #  "content": "50383a4c15124682057b197d40261641a98db514",
        }),
        # oneshot
        ("https://mangadex.cc/chapter/138086", {
            "count": 64,
            "keyword": "c53a0e4c12250578a4e630281085875e59532c03",
        }),
        # MANGA Plus (#1154)
        ("https://mangadex.org/chapter/1122815", {
            "exception": exception.HttpError,
        }),
    )

    def __init__(self, match):
        MangadexExtractor.__init__(self, match)
        self.chapter_id = match.group(1)

    def items(self):
        cdata = self.chapter_data(self.chapter_id)
        if "server" not in cdata:
            if cdata["status"] == "external":
                raise exception.StopExtraction(
                    "Chapter is not available on MangaDex and can be read on "
                    "the official publisher's website at %s.", cdata["pages"])
            raise exception.StopExtraction("No download server available.")
        mdata = self.manga_data(cdata["mangaId"])

        chapter, sep, minor = cdata["chapter"].partition(".")
        lang = self.iso639_map.get(cdata["language"], cdata["language"])

        base = cdata["server"] + cdata["hash"] + "/"
        if base[0] == "/":
            base = text.urljoin(self.root, base)

        if "serverFallback" in cdata:
            fallback = cdata["serverFallback"] + cdata["hash"] + "/"
        else:
            fallback = None

        data = {
            "manga"   : text.unescape(mdata["title"]),
            "manga_id": mdata["id"],
            "artist"  : mdata["artist"],
            "author"  : mdata["author"],
            "title"   : text.unescape(cdata["title"]),
            "volume"  : text.parse_int(cdata["volume"]),
            "chapter" : text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_id": cdata["id"],
            "group"   : [group["name"] for group in cdata["groups"]],
            "date"    : text.parse_timestamp(cdata["timestamp"]),
            "lang"    : lang,
            "language": util.code_to_language(lang),
            "count"   : len(cdata["pages"]),
        }

        yield Message.Directory, data
        for data["page"], page in enumerate(cdata["pages"], 1):
            if fallback:
                data["_fallback"] = (fallback + page,)
            yield Message.Url, base + page, text.nameext_from_url(page, data)


class MangadexMangaExtractor(MangadexExtractor):
    """Extractor for manga from mangadex.org"""
    subcategory = "manga"
    categorytransfer = True
    pattern = (r"(?:https?://)?(?:www\.)?mangadex\.(?:org|cc)"
               r"/(?:title|manga)/(\d+)")
    test = (
        ("https://mangadex.org/manga/2946/souten-no-koumori", {
            "pattern": r"https://mangadex.org/chapter/\d+",
            "keyword": {
                "manga"   : "Souten no Koumori",
                "manga_id": 2946,
                "title"   : "re:One[Ss]hot",
                "volume"  : 0,
                "chapter" : 0,
                "chapter_minor": "",
                "chapter_id": int,
                "group"   : list,
                "date"    : "type:datetime",
                "lang"    : str,
                "language": str,
            },
        }),
        ("https://mangadex.cc/manga/13318/dagashi-kashi/chapters/2/", {
            "count": ">= 100",
        }),
        ("https://mangadex.org/title/13004/yorumori-no-kuni-no-sora-ni", {
            "count": 0,
        }),
    )

    def __init__(self, match):
        MangadexExtractor.__init__(self, match)
        self.manga_id = match.group(1)

    def items(self):
        yield Message.Version, 1
        for data in self.chapters():
            url = "{}/chapter/{}".format(self.root, data["chapter_id"])
            yield Message.Queue, url, data

    def chapters(self):
        """Return a sorted list of chapter-metadata dicts"""
        manga = self.manga_data(int(self.manga_id))
        results = []

        for cdata in self.manga_chapters(self.manga_id):
            chapter, sep, minor = cdata["chapter"].partition(".")
            lang = self.iso639_map.get(cdata["language"], cdata["language"])
            results.append({
                "manga"   : text.unescape(manga["title"]),
                "manga_id": text.parse_int(self.manga_id),
                "artist"  : manga["artist"],
                "author"  : manga["author"],
                "title"   : text.unescape(cdata["title"]),
                "volume"  : text.parse_int(cdata["volume"]),
                "chapter" : text.parse_int(chapter),
                "chapter_minor": sep + minor,
                "chapter_id": text.parse_int(cdata["id"]),
                "group"   : cdata["groups"],
                "date"    : text.parse_timestamp(cdata["timestamp"]),
                "lang"    : lang,
                "language": util.code_to_language(lang),
                "_extractor": MangadexChapterExtractor,
            })

        results.sort(
            key=lambda x: (x["chapter"], x["chapter_minor"]),
            reverse=self.config("chapter-reverse", False),
        )
        return results
