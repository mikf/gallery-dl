# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://kissmanga.com/"""

from .common import Extractor, MangaExtractor, Message
from .. import text, cloudflare, aes
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
    directory_fmt = ["{category}", "{manga}",
                     "c{chapter:>03}{chapter-minor} - {title}"]
    filename_fmt = ("{manga}_c{chapter:>03}{chapter-minor}_"
                    "{page:>03}.{extension}")
    root = "http://kissmanga.com"

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.group(0)
        self.session.headers["Referer"] = self.root

    request = cloudflare.request_func


class KissmangaMangaExtractor(KissmangaExtractor, MangaExtractor):
    """Extractor for manga from kissmanga.com"""
    pattern = [r"(?:https?://)?(?:www\.)?kissmanga\.com/Manga/[^/]+/?$"]
    test = [("http://kissmanga.com/Manga/Dropout", {
        "url": "992befdd64e178fe5af67de53f8b510860d968ca",
    })]

    def chapter_paths(self, page):
        return text.extract_iter(page, '<td>\n<a href="', '"')


class KissmangaChapterExtractor(KissmangaExtractor):
    """Extractor for manga-chapters from kissmanga.com"""
    subcategory = "chapter"
    pattern = [r"(?:https?://)?(?:www\.)?kissmanga\.com/Manga/.+/.+\?id=\d+"]
    test = [
        ("http://kissmanga.com/Manga/Dropout/Ch-000---Oneshot-?id=145847", {
            "url": "4136bcd1c6cecbca8cc2bc965d54f33ef0a97cc0",
            "keyword": "ab332093a4f2e473a468235bfd624cbe3b19fd7f",
        }),
        ("http://kissmanga.com/Manga/Urban-Tales/a?id=256717", {
            "url": "de074848f6c1245204bb9214c12bcc3ecfd65019",
            "keyword": "013aad80e578c6ccd2e1fe47cdc27c12a64f6db2",
        }),
        ("http://kissmanga.com/Manga/Monster/Monster-79?id=7608", {
            "url": "6abec8178f35fe7846586280ca9e38eacc32452c",
            "keyword": "ca7a07ecfd9525c0f825dc747f520306611d6af9",
        }),
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
        manga, pos = text.extract(page, "Read manga\n", "\n")
        cinfo, pos = text.extract(page, "", "\n", pos)
        match = re.match((
            r"(?:[Vv]ol.0*(\d+) )?(?:[Cc]h.)?0*(\d+)(?:\.0*(\d+))?(?:: (.+))?|"
            r"[\w ]+?(?: -)? 0*(\d+)(?: (.+))?"), cinfo)
        chminor = match.group(3) or match.group(6)
        return {
            "manga": manga,
            "volume": match.group(1) or "",
            "chapter": match.group(2) or match.group(5),
            "chapter-minor": "."+chminor if chminor else "",
            "title": match.group(4) or "",
            "lang": "en",
            "language": "English",
        }

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
        except (ValueError, IndexError) as e:
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
