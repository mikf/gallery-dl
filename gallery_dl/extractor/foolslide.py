# -*- coding: utf-8 -*-

# Copyright 2016-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for FoOlSlide based sites"""

from .common import (
    Extractor, ChapterExtractor, MangaExtractor, Message, SharedConfigMixin)
from .. import text, util, config
import base64
import json
import re


class FoolslideBase(SharedConfigMixin):
    """Base class for FoOlSlide extractors"""
    basecategory = "foolslide"

    def request(self, url):
        return Extractor.request(
            self, url, encoding="utf-8", method="POST", data={"adult": "true"})

    @staticmethod
    def parse_chapter_url(url, data):
        info = url.partition("/read/")[2].rstrip("/").split("/")
        lang = info[1].partition("-")[0]
        data["lang"] = lang
        data["language"] = util.code_to_language(lang)
        data["volume"] = text.parse_int(info[2])
        data["chapter"] = text.parse_int(info[3])
        data["chapter_minor"] = "." + info[4] if len(info) >= 5 else ""
        return data


class FoolslideChapterExtractor(FoolslideBase, ChapterExtractor):
    """Base class for chapter extractors for FoOlSlide based sites"""
    directory_fmt = (
        "{category}", "{manga}", "{chapter_string}")
    archive_fmt = "{id}"
    decode = "default"

    def items(self):
        page = self.request(self.chapter_url).text
        data = self.metadata(page)
        imgs = self.images(page)

        data["count"] = len(imgs)
        data["chapter_id"] = text.parse_int(imgs[0]["chapter_id"])

        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"], image in enumerate(imgs, 1):
            try:
                url = image["url"]
                del image["url"]
                del image["chapter_id"]
                del image["thumb_url"]
            except KeyError:
                pass
            for key in ("height", "id", "size", "width"):
                image[key] = text.parse_int(image[key])
            data.update(image)
            text.nameext_from_url(data["filename"], data)
            yield Message.Url, url, data

    def metadata(self, page):
        _      , pos = text.extract(page, '<h1 class="tbtitle dnone">', '')
        manga  , pos = text.extract(page, 'title="', '"', pos)
        chapter, pos = text.extract(page, 'title="', '"', pos)
        chapter = text.unescape(chapter)
        return self.parse_chapter_url(self.chapter_url, {
            "manga": text.unescape(manga).strip(),
            "title": chapter.partition(":")[2].strip(),
            "chapter_string": chapter,
        })

    def images(self, page):
        if self.decode == "base64":
            base64_data = text.extract(page, 'atob("', '"')[0].encode()
            data = base64.b64decode(base64_data).decode()
        elif self.decode == "double":
            pos = page.find("[{")
            data = text.extract(page, " = ", ";", pos)[0]
        else:
            data = text.extract(page, "var pages = ", ";")[0]
        return json.loads(data)


class FoolslideMangaExtractor(FoolslideBase, MangaExtractor):
    """Base class for manga extractors for FoOlSlide based sites"""

    def chapters(self, page):
        manga , pos = text.extract(page, '<h1 class="title">', '</h1>')
        author, pos = text.extract(page, '<b>Author</b>: ', '<br', pos)
        artist, pos = text.extract(page, '<b>Artist</b>: ', '<br', pos)
        manga = text.unescape(manga).strip()

        results = []
        while True:
            url, pos = text.extract(
                page, '<div class="title"><a href="', '"', pos)
            if not url:
                return results

            chapter, pos = text.extract(page, 'title="', '"', pos)
            group  , pos = text.extract(page, 'title="', '"', pos)

            results.append((url, self.parse_chapter_url(url, {
                "manga": manga, "author": author, "artist": artist,
                "group": group, "chapter_string": chapter,
                "title": chapter.partition(": ")[2] or "",
            })))


def generate_extractors():
    """Dynamically generate Extractor classes for FoOlSlide instances"""

    symtable = globals()
    extractors = config.get(("extractor", "foolslide"))

    if extractors:
        EXTRACTORS.update(extractors)

    for category, info in EXTRACTORS.items():

        if not isinstance(info, dict):
            continue

        root = info["root"]
        domain = root[root.index(":") + 3:]
        pattern = info.get("pattern") or re.escape(domain)
        name = (info.get("name") or category).capitalize()

        class ChExtr(FoolslideChapterExtractor):
            pass

        ChExtr.__name__ = ChExtr.__qualname__ = name + "ChapterExtractor"
        ChExtr.__doc__ = "Extractor for manga-chapters from " + domain
        ChExtr.category = category
        ChExtr.pattern = (r"(?:https?://)?" + pattern +
                          r"(/read/[^/?&#]+/[a-z-]+/\d+/\d+(?:/\d+)?)")
        ChExtr.test = info.get("test-chapter")
        ChExtr.root = root
        if "decode" in info:
            ChExtr.decode = info["decode"]
        symtable[ChExtr.__name__] = ChExtr

        class MaExtr(FoolslideMangaExtractor):
            pass

        MaExtr.__name__ = MaExtr.__qualname__ = name + "MangaExtractor"
        MaExtr.__doc__ = "Extractor for manga from " + domain
        MaExtr.category = category
        MaExtr.pattern = r"(?:https?://)?" + pattern + r"(/series/[^/?&#]+)"
        MaExtr.test = info.get("test-manga")
        MaExtr.root = root
        symtable[MaExtr.__name__] = MaExtr


EXTRACTORS = {
    "dokireader": {
        "root": "https://kobato.hologfx.com/reader",
        "test-chapter":
            (("https://kobato.hologfx.com/reader/read/"
              "hitoribocchi_no_oo_seikatsu/en/3/34"), {
                "keyword": "998d1d523da028284b8dd4b7b54ceae4af6cb65a",
            }),
        "test-manga":
            (("https://kobato.hologfx.com/reader/series/"
              "boku_ha_ohimesama_ni_narenai/"), {
                "url": "1c1f5a7258ce4f631f5fc32be548d78a6a57990d",
                "keyword": "614d89a6045b85c822cbd3e67578ea7577dfc995",
            }),
    },
    "jaiminisbox": {
        "root": "https://jaiminisbox.com/reader",
        "pattern": r"(?:www\.)?jaiminisbox\.com/reader",
        "decode": "base64",
        "test-chapter": (
            ("https://jaiminisbox.com/reader/read/uratarou/en/0/1/", {
                "keyword": "d8919bc8f0351b44e938862214e654401962b5a5",
            }),
            ("https://jaiminisbox.com/reader/read/dr-stone/en/0/16/", {
                "keyword": "9b658599651f1ae87cab3e0e29dd21e8337a362c",
            }),
        ),
        "test-manga":
            ("https://jaiminisbox.com/reader/series/sora_no_kian/", {
                "url": "66612be177dc3b3fa1d1f537ef02f4f701b163ea",
                "keyword": "0908a4145bb03acc4210f5d01169988969f5acd1",
            }),
    },
    "kireicake": {
        "root": "https://reader.kireicake.com",
        "test-chapter":
            ("https://reader.kireicake.com/read/wonderland/en/1/1/", {
                "url": "b2d36bc0bc67e4c461c3a4d6444a2fd339f5d07e",
                "keyword": "47e0cf69f95ab3b820bda05014aec38d3b824018",
            }),
        "test-manga":
            ("https://reader.kireicake.com/series/wonderland/", {
                "url": "d067b649af1cc88fa8c8b698fde04a10909fd169",
                "keyword": "99caa336a9d48e27e3b8e56a0a1e6faf9fc13a51",
            }),
    },
    "powermanga": {
        "root": "https://read.powermanga.org",
        "pattern": r"read(?:er)?\.powermanga\.org",
        "test-chapter":
            (("https://read.powermanga.org"
              "/read/one_piece_digital_colour_comics/en/0/75/"), {
                "url": "854c5817f8f767e1bccd05fa9d58ffb5a4b09384",
                "keyword": "9985bcb78491dff9c725958b06bba606be51b6d3",
            }),
        "test-manga":
            (("https://read.powermanga.org"
              "/series/one_piece_digital_colour_comics/"), {
                "count": ">= 1",
                "keyword": {
                    "chapter": int,
                    "chapter_minor": str,
                    "chapter_string": str,
                    "group": "PowerManga",
                    "lang": "en",
                    "language": "English",
                    "manga": "One Piece Digital Colour Comics",
                    "title": str,
                    "volume": int,
                },
            }),
    },
    "seaotterscans": {
        "root": "https://reader.seaotterscans.com",
        "test-chapter":
            ("https://reader.seaotterscans.com/read/100_days/en/0/5/", {
                "url": "63d46b8883cc652dfe8bd5be4492160dd31f06a8",
                "keyword": "5349c2fbaa88070e6af600de17a6c4e212243e8e",
            }),
        "test-manga":
            ("https://reader.seaotterscans.com/series/marry_me/", {
                "url": "fdbacabfa566a6baeb3f01bb46cbda0577bd4bbe",
                "keyword": "61d3388d73df12f64361892b47a9398df4a5947c",
            }),
    },
    "sensescans": {
        "root": "http://sensescans.com/reader",
        "pattern": r"(?:(?:www\.)?sensescans\.com/reader"
                   r"|reader\.sensescans\.com)",
        "test-chapter": (
            (("http://sensescans.com/reader/read/"
              "magi__labyrinth_of_magic/en/37/369/"), {
                  "url": "a399ef037cdfbc25b09d435cc2ea1e3e454a6812",
                  "keyword": "43ba75615d3e77d507808b0f3a8fd7fc72232a60",
            }),
            (("http://reader.sensescans.com/read/"
              "magi__labyrinth_of_magic/en/37/369/"), {
                  "url": "a399ef037cdfbc25b09d435cc2ea1e3e454a6812",
                  "keyword": "43ba75615d3e77d507808b0f3a8fd7fc72232a60",
            }),
        ),
        "test-manga":
            ("http://sensescans.com/reader/series/hakkenden/", {
                "url": "2360ccb0ead0ff2f5e27b7aef7eb17b9329de2f2",
                "keyword": "122cf92c32e6428c50f56ffaf29d06b96750ed71",
            }),
    },
    "worldthree": {
        "root": "http://www.slide.world-three.org",
        "pattern": r"(?:www\.)?slide\.world-three\.org",
        "test-chapter": (
            (("http://www.slide.world-three.org"
              "/read/black_bullet/en/2/7/page/1"), {
                "url": "be2f04f6e2d311b35188094cfd3e768583271584",
                "keyword": "28edfeccc92f7ea29546d5616e689dcfcbac59d9",
            }),
            (("http://www.slide.world-three.org"
              "/read/idolmster_cg_shuffle/en/0/4/2/"), {
                "url": "6028ea5ca282744f925dfad92eeb98509f9cc78c",
                "keyword": "d478e9f20847deb1844dba318acaa8b91c19468a",
            }),
        ),
        "test-manga":
            ("http://www.slide.world-three.org/series/black_bullet/", {
                "url": "5743b93512d26e6b540d90a7a5d69208b6d4a738",
                "keyword": "3a24f1088b4d7f3b798a96163f21ca251293a120",
            }),
    },
}


generate_extractors()
