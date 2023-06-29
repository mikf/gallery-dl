# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangapark.net/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, util
import re

BASE_PATTERN = r"(?:https?://)?(?:www\.)?mangapark\.(?:net|com|org|io|me)"


class MangaparkBase():
    """Base class for mangapark extractors"""
    category = "mangapark"

    @staticmethod
    def parse_chapter_path(path, data):
        """Get volume/chapter information from url-path of a chapter"""
        data["volume"], data["chapter_minor"] = 0, ""
        for part in path.split("/")[1:]:
            key, value = part[0], part[1:]
            if key == "c":
                chapter, dot, minor = value.partition(".")
                data["chapter"] = text.parse_int(chapter)
                data["chapter_minor"] = dot + minor
            elif key == "i":
                data["chapter_id"] = text.parse_int(value)
            elif key == "v":
                data["volume"] = text.parse_int(value)
            elif key == "s":
                data["stream"] = text.parse_int(value)
            elif key == "e":
                data["chapter_minor"] = "v" + value

    @staticmethod
    def parse_chapter_title(title, data):
        match = re.search(r"(?i)(?:vol(?:ume)?[ .]*(\d+) )?"
                          r"ch(?:apter)?[ .]*(\d+)(\.\w+)?", title)
        if match:
            vol, ch, data["chapter_minor"] = match.groups()
            data["volume"] = text.parse_int(vol)
            data["chapter"] = text.parse_int(ch)


class MangaparkChapterExtractor(MangaparkBase, ChapterExtractor):
    """Extractor for manga-chapters from mangapark.net"""
    pattern = BASE_PATTERN + r"/title/[^/?#]+/(\d+)"
    test = (
        ("https://mangapark.net/title/114972-aria/6710214-en-ch.60.2", {
            "count": 70,
            "pattern": r"https://[\w-]+\.mpcdn\.org/comic/2002/e67"
                       r"/61e29278a583b9227964076e/\d+_\d+_\d+_\d+\.jpeg"
                       r"\?acc=[^&#]+&exp=\d+",
            "keyword": {
                "artist": [],
                "author": ["Amano Kozue"],
                "chapter": 60,
                "chapter_id": 6710214,
                "chapter_minor": ".2",
                "count": 70,
                "date": "dt:2022-01-15 09:25:03",
                "extension": "jpeg",
                "filename": str,
                "genre": ["adventure", "comedy", "drama", "sci_fi",
                          "shounen", "slice_of_life"],
                "lang": "en",
                "language": "English",
                "manga": "Aria",
                "manga_id": 114972,
                "page": int,
                "source": "Koala",
                "title": "Special Navigation - Aquaria Ii",
                "volume": 12,
            },
        }),
        ("https://mangapark.com/title/114972-aria/6710214-en-ch.60.2"),
        ("https://mangapark.org/title/114972-aria/6710214-en-ch.60.2"),
        ("https://mangapark.io/title/114972-aria/6710214-en-ch.60.2"),
        ("https://mangapark.me/title/114972-aria/6710214-en-ch.60.2"),
    )

    def __init__(self, match):
        self.root = text.root_from_url(match.group(0))
        url = "{}/title/_/{}".format(self.root, match.group(1))
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        data = util.json_loads(text.extr(
            page, 'id="__NEXT_DATA__" type="application/json">', '<'))
        chapter = (data["props"]["pageProps"]["dehydratedState"]
                   ["queries"][0]["state"]["data"]["data"])
        manga = chapter["comicNode"]["data"]
        source = chapter["sourceNode"]["data"]

        self._urls = chapter["imageSet"]["httpLis"]
        self._params = chapter["imageSet"]["wordLis"]

        match = re.match(
            r"(?i)"
            r"(?:vol(?:\.|ume)?\s*(\d+)\s*)?"
            r"ch(?:\.|apter)?\s*(\d+)([^\s:]*)"
            r"(?:\s*:\s*(.*))?", chapter["dname"])
        vol, ch, minor, title = match.groups() if match else (0, 0, "", "")

        return {
            "manga"     : manga["name"],
            "manga_id"  : manga["id"],
            "artist"    : source["artists"],
            "author"    : source["authors"],
            "genre"     : source["genres"],
            "volume"    : text.parse_int(vol),
            "chapter"   : text.parse_int(ch),
            "chapter_minor": minor,
            "chapter_id": chapter["id"],
            "title"     : chapter["title"] or title or "",
            "lang"      : chapter["lang"],
            "language"  : util.code_to_language(chapter["lang"]),
            "source"    : chapter["srcTitle"],
            "date"      : text.parse_timestamp(chapter["dateCreate"] // 1000),
        }

    def images(self, page):
        return [
            (url + "?" + params, None)
            for url, params in zip(self._urls, self._params)
        ]


class MangaparkMangaExtractor(MangaparkBase, MangaExtractor):
    """Extractor for manga from mangapark.net"""
    chapterclass = MangaparkChapterExtractor
    pattern = (r"(?:https?://)?(?:www\.|v2\.)?mangapark\.(me|net|com)"
               r"(/manga/[^/?#]+)/?$")
    test = (
        ("https://mangapark.net/manga/aria", {
            "url": "51c6d82aed5c3c78e0d3f980b09a998e6a2a83ee",
            "keyword": "cabc60cf2efa82749d27ac92c495945961e4b73c",
        }),
        ("https://mangapark.me/manga/aria"),
        ("https://mangapark.com/manga/aria"),
    )

    def __init__(self, match):
        self.root = self.root_fmt.format(match.group(1))
        MangaExtractor.__init__(self, match, self.root + match.group(2))

    def chapters(self, page):
        results = []
        data = {"lang": "en", "language": "English"}
        data["manga"] = text.unescape(
            text.extr(page, '<title>', ' Manga - '))

        for stream in page.split('<div id="stream_')[1:]:
            data["stream"] = text.parse_int(text.extr(stream, '', '"'))

            for chapter in text.extract_iter(stream, '<li ', '</li>'):
                path  , pos = text.extract(chapter, 'href="', '"')
                title1, pos = text.extract(chapter, '>', '<', pos)
                title2, pos = text.extract(chapter, '>: </span>', '<', pos)
                count , pos = text.extract(chapter, '  of ', ' ', pos)

                self.parse_chapter_path(path[8:], data)
                if "chapter" not in data:
                    self.parse_chapter_title(title1, data)

                if title2:
                    data["title"] = title2.strip()
                else:
                    data["title"] = title1.partition(":")[2].strip()

                data["count"] = text.parse_int(count)
                results.append((self.root + path, data.copy()))
                data.pop("chapter", None)

        return results
