# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from https://kissmanga.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, aes, exception
from ..cache import cache
import hashlib
import ast
import re


class KissmangaBase():
    """Base class for kissmanga extractors"""
    category = "kissmanga"
    archive_fmt = "{chapter_id}_{page}"
    root = "https://kissmanga.com"

    def request(self, url):
        response = super().request(url)
        if response.history and "/Message/AreYouHuman?" in response.url:
            self.log.error("Requesting too many pages caused a redirect to %s."
                           " Try visiting this URL in your browser and solve"
                           " the CAPTCHA to continue.", response.url)
            raise exception.StopExtraction()
        return response

    @staticmethod
    def parse_chapter_string(data):
        """Parse 'chapter_string' value contained in 'data'"""
        data["chapter_string"] = text.unescape(data["chapter_string"])

        match = re.match((
            r"(?:[Vv]ol\.0*(\d+) )?"
            r"(?:[Cc]h\.)?0*(\d+)"
            r"(?:[.:]0*(\d+))?"
            r"(?: *[:-]? *(.+))?"
        ), data["chapter_string"])

        if not match:
            match = re.match((
                r".+?(?: -)? ()"
                r"0*(\d+)(?:[Vv.]0*(\d+))?"
                r"(?: *[:-]? *(.+))?"
            ), data["chapter_string"])

        if match:
            volume, chapter, minor, title = match.groups()
        else:
            volume, chapter, minor, title = 0, 0, "", data["chapter_string"]

        data["volume"] = text.parse_int(volume)
        data["chapter"] = text.parse_int(chapter)
        data["chapter_minor"] = "." + minor if minor else ""
        data["title"] = title if title and title != "Read Online" else ""
        return data


class KissmangaChapterExtractor(KissmangaBase, ChapterExtractor):
    """Extractor for manga-chapters from kissmanga.com"""
    pattern = (r"(?i)(?:https?://)?(?:www\.)?kissmanga\.com"
               r"(/Manga/[^/?&#]+/[^/?&#]+\?id=(\d+))")
    test = (
        ("https://kissmanga.com/Manga/Dropout/Ch-000---Oneshot-?id=145847", {
            "url": "46e63fd63e9e16f19bc1e6c7a45dc060815642fd",
            "keyword": "1cd0b5214ac7ae4d53e2fd8fec40ceec84cd09bf",
        }),
        ("https://kissmanga.com/Manga/Urban-Tales/a?id=256717", {
            "url": "c26be8bf9c2abacee2076979d021634092cf38f1",
            "keyword": "e1d16780df8e04076ed2b5f0637c5b710ec2f2ea",
        }),
        ("https://kissmanga.com/Manga/Monster/Monster-79?id=7608", {
            "count": 23,
            "keyword": "f433a7a8fae840e17dace316a243fa27faab86de",
        }),
        ("https://kissmanga.com/Manga/Houseki-no-Kuni/Oneshot?id=404189", {
            "count": 49,
            "keyword": "d44d1b21d08e4dbf888b0c450a3f1bc919588b4f",
        }),
        ("https://kissmanga.com/mAnGa/mOnStEr/Monster-79?id=7608"),
    )

    def __init__(self, match):
        ChapterExtractor.__init__(self, match)
        self.chapter_id = match.group(2)
        self.session.headers["Referer"] = self.root

    def metadata(self, page):
        title = text.extract(page, "<title>", "</title>")[0].strip()
        manga, cinfo = title.split("\n")[1:3]
        data = {
            "manga": manga.strip(),
            "chapter_string": cinfo.strip(),
            "chapter_id": text.parse_int(self.chapter_id),
            "lang": "en",
            "language": "English",
        }
        return self.parse_chapter_string(data)

    def images(self, page):
        self.session.headers["Referer"] = None
        try:
            key = self.build_aes_key(page)
            iv = (0xa5, 0xe8, 0xe2, 0xe9, 0xc2, 0x72, 0x1b, 0xe0,
                  0xa8, 0x4a, 0xd6, 0x60, 0xc4, 0x72, 0xc1, 0xf3)
            return [
                (aes.aes_cbc_decrypt_text(data, key, iv), None)
                for data in text.extract_iter(
                    page, 'lstImages.push(wrapKA("', '"'
                )
            ]
        except UnicodeDecodeError:
            self.log.error("Failed to decrypt image URLs")
        except (ValueError, IndexError):
            self.log.error("Failed to get AES key")
        return []

    def build_aes_key(self, page):
        chko = self._chko_from_external_script()

        for script in self._scripts(page):
            for stmt in [s.strip() for s in script.split(";")]:

                if stmt.startswith("var _"):
                    name, _, value = stmt[4:].partition(" = ")
                    name += "[0]"
                    value = ast.literal_eval(value)[0]

                elif stmt.startswith("chko = "):
                    stmt = stmt[7:]
                    if stmt == name:
                        chko = value
                    elif stmt == "chko + " + name:
                        chko = chko + value
                    elif stmt == name + " + chko":
                        chko = value + chko
                    else:
                        self.log.warning("unrecognized expression: '%s'", stmt)

                elif stmt.startswith("key = "):
                    pass

                else:
                    self.log.warning("unrecognized statement: '%s'", stmt)

        return list(hashlib.sha256(chko.encode("ascii")).digest())

    @staticmethod
    def _scripts(page):
        end = 0
        while True:
            pos = page.find("key = ", end)
            if pos == -1:
                return
            beg = page.rindex('<script type="text/javascript">', 0, pos) + 31
            end = page.index('</script>', pos)
            yield page[beg:end]

    @cache(maxage=3600)
    def _chko_from_external_script(self):
        script = self.request(self.root + "/Scripts/lo.js").text

        pos = script.index("var chko")
        var = text.extract(script, "=", "[", pos)[0].lstrip()
        idx = text.extract(script, "[", "]", pos)[0]

        pos = script.index(var)
        lst = text.extract(script, "=", ";", pos)[0]
        return ast.literal_eval(lst.strip())[int(idx)]


class KissmangaMangaExtractor(KissmangaBase, MangaExtractor):
    """Extractor for manga from kissmanga.com"""
    chapterclass = KissmangaChapterExtractor
    pattern = (r"(?i)(?:https?://)?(?:www\.)?kissmanga\.com"
               r"(/Manga/[^/?&#]+/?)$")
    test = (
        ("https://kissmanga.com/Manga/Dropout", {
            "url": "9e3a6f715b229aa3fafa42a1d5da5d65614cb532",
            "keyword": "32b09711c28b481845acc32e3bb6054cfc90224d",
        }),
        ("https://kissmanga.com/manga/feng-shen-ji"),  # lowercase
    )

    def chapters(self, page):
        results = []
        manga, pos = text.extract(page, ' class="barTitle">', '\ninformation')
        page , pos = text.extract(page, ' class="listing">', '</table>', pos)
        manga = manga.strip()
        needle = '" title="Read ' + manga + ' '
        manga = text.unescape(manga)

        for item in text.extract_iter(page, '<a href="', ' online">'):
            url, _, chapter = item.partition(needle)
            data = {
                "manga": manga, "chapter_string": chapter,
                "chapter_id": text.parse_int(url.rpartition("=")[2]),
                "lang": "en", "language": "English",
            }
            self.parse_chapter_string(data)
            results.append((self.root + url, data))
        return results
