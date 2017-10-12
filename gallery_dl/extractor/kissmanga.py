# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://kissmanga.com/"""

from .common import Extractor, MangaExtractor, Message
from .. import text, util, cloudflare, aes
from ..cache import cache
import re
import hashlib
import ast

IV = [
    0xa5, 0xe8, 0xe2, 0xe9, 0xc2, 0x72, 0x1b, 0xe0,
    0xa8, 0x4a, 0xd6, 0x60, 0xc4, 0x72, 0xc1, 0xf3
]


class KissmangaExtractor(Extractor):
    """Base class for kissmanga extractors"""
    category = "kissmanga"
    directory_fmt = [
        "{category}", "{manga}",
        "{volume:?v/ />02}c{chapter:>03}{chapter_minor}{title:?: //}"]
    filename_fmt = (
        "{manga}_c{chapter:>03}{chapter_minor}_{page:>03}.{extension}")
    root = "http://kissmanga.com"

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.group(0)
        self.session.headers["Referer"] = self.root

    request = cloudflare.request_func

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
            match = re.match(
                r"[\w ]+?(?: -)? 0*()(\d+)()(?: *[:-]? *(.+))?",
                data["chapter_string"])

        volume, chapter, minor, title = match.groups()
        data["volume"] = util.safe_int(volume)
        data["chapter"] = util.safe_int(chapter)
        data["chapter_minor"] = "." + minor if minor else ""
        data["title"] = title if title and title != "Read Online" else ""
        return data


class KissmangaMangaExtractor(KissmangaExtractor, MangaExtractor):
    """Extractor for manga from kissmanga.com"""
    pattern = [r"(?i)(?:https?://)?(?:www\.)?kissmanga\.com/"
               r"Manga/[^/?&#]+/?$"]
    test = [
        ("http://kissmanga.com/Manga/Dropout", {
            "url": "992befdd64e178fe5af67de53f8b510860d968ca",
            "keyword": "1d23ea07296e004b33bee17fe2f5cd5177c58680",
        }),
        ("http://kissmanga.com/manga/feng-shen-ji", None),
    ]

    def chapters(self, page):
        results = []
        manga, pos = text.extract(
            page, '<div class="barTitle">', '\ninformation')
        page, pos = text.extract(
            page, '<table class="listing">', '</table>', pos)
        manga = manga.strip()
        needle = '" title="Read ' + manga + ' '
        manga = text.unescape(manga)

        for item in text.extract_iter(page, '<a href="', ' online">'):
            url, _, chapter = item.partition(needle)
            data = {
                "manga": manga, "id": url.rpartition("=")[2],
                "chapter_string": chapter, "lang": "en", "language": "English",
            }
            self.parse_chapter_string(data)
            results.append((self.root + url, data))
        return results


class KissmangaChapterExtractor(KissmangaExtractor):
    """Extractor for manga-chapters from kissmanga.com"""
    subcategory = "chapter"
    pattern = [r"(?i)(?:https?://)?(?:www\.)?kissmanga\.com/"
               r"Manga/[^/?&#]+/[^/?&#]+\?id=\d+"]
    test = [
        ("http://kissmanga.com/Manga/Dropout/Ch-000---Oneshot-?id=145847", {
            "url": "4136bcd1c6cecbca8cc2bc965d54f33ef0a97cc0",
            "keyword": "68384c1167858fb4aa475c4596f0a685c45fff36",
        }),
        ("http://kissmanga.com/Manga/Urban-Tales/a?id=256717", {
            "url": "de074848f6c1245204bb9214c12bcc3ecfd65019",
            "keyword": "089158338b4cde43b2ff244814effeb13297de33",
        }),
        ("http://kissmanga.com/Manga/Monster/Monster-79?id=7608", {
            "url": "6abec8178f35fe7846586280ca9e38eacc32452c",
            "keyword": "558da596e86ca544eb72cf303f3694bbf0b1f2f5",
        }),
        ("http://kissmanga.com/mAnGa/mOnStEr/Monster-79?id=7608", None),
    ]

    def items(self):
        page = self.request(self.url).text
        data = self.get_job_metadata(page)
        imgs = self.get_image_urls(page)
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"], url in enumerate(imgs, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        title = text.extract(page, "<title>", "</title>")[0].strip()
        manga, cinfo = title.split("\n")[1:3]
        data = {
            "manga": manga.strip(),
            "chapter_string": cinfo.strip(),
            "lang": "en",
            "language": "English",
        }
        return self.parse_chapter_string(data)

    def get_image_urls(self, page):
        """Extract list of all image-urls for a manga chapter"""
        try:
            key = self.build_aes_key(page)
            return [
                aes.aes_cbc_decrypt_text(data, key, IV)
                for data in text.extract_iter(
                    page, 'lstImages.push(wrapKA("', '"'
                )
            ]
        except UnicodeDecodeError:
            self.log.error("Failed to decrypt image URls")
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
