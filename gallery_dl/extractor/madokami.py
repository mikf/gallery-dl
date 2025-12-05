# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://manga.madokami.al/"""

from .common import Extractor, Message
from .. import text, util, exception

BASE_PATTERN = r"(?:https?://)?manga\.madokami\.al"


class MadokamiExtractor(Extractor):
    """Base class for madokami extractors"""
    category = "madokami"
    root = "https://manga.madokami.al"


class MadokamiMangaExtractor(MadokamiExtractor):
    """Extractor for madokami manga"""
    subcategory = "manga"
    directory_fmt = ("{category}", "{manga}")
    archive_fmt = "{chapter_id}"
    pattern = rf"{BASE_PATTERN}/Manga/(\w/\w{{2}}/\w{{4}}/.+)"
    example = "https://manga.madokami.al/Manga/A/AB/ABCD/ABCDE_TITLE"

    def items(self):
        username, password = self._get_auth_info()
        if not username:
            raise exception.AuthRequired("username & password")
        self.session.auth = util.HTTPBasicAuth(username, password)

        url = f"{self.root}/Manga/{self.groups[0]}"
        page = self.request(url).text
        extr = text.extract_from(page)

        chapters = []
        while True:
            if not (cid := extr('<tr data-record="', '"')):
                break
            chapters.append({
                "chapter_id": text.parse_int(cid),
                "path": text.unescape(extr('href="', '"')),
                "chapter_string": text.unescape(extr(">", "<")),
                "size": text.parse_bytes(extr("<td>", "</td>")),
                "date": self.parse_datetime_iso(extr("<td>", "</td>").strip()),
            })

        if self.config("chapter-reverse"):
            chapters.reverse()

        self.kwdict.update({
            "manga" : text.unescape(extr('itemprop="name">', "<")),
            "year"  : text.parse_int(extr(
                'itemprop="datePublished" content="', "-")),
            "author": text.split_html(extr('<p class="staff', "</p>"))[1::2],
            "genre" : text.split_html(extr("<h3>Genres</h3>", "</div>")),
            "tags"  : text.split_html(extr("<h3>Tags</h3>", "</div>")),
            "complete": extr('span class="scanstatus">', "<").lower() == "yes",
        })

        search_chstr = text.re(
            r"(?i)((?:v(?:ol)?\.?\s*(\d+))"
            r"(?:\s+ch?\.?\s*(\d+)(?:-(\d+))?)?)").search
        search_chstr_min = text.re(
            r"(?i)(ch?\.?\s*(\d+)(?:-(\d+))?)").search

        for ch in chapters:

            chstr = ch["chapter_string"]
            if match := search_chstr(chstr):
                ch["chapter_string"], volume, chapter, end = match.groups()
                ch["volume"] = text.parse_int(volume)
                ch["chapter"] = text.parse_int(chapter)
                ch["chapter_end"] = text.parse_int(end)
            elif match := search_chstr_min(chstr):
                ch["chapter_string"], chapter, end = match.groups()
                ch["volume"] = 0
                ch["chapter"] = text.parse_int(chapter)
                ch["chapter_end"] = text.parse_int(end)
            else:
                ch["volume"] = ch["chapter"] = ch["chapter_end"] = 0

            url = f"{self.root}{ch['path']}"
            text.nameext_from_url(url, ch)

            yield Message.Directory, "", ch
            yield Message.Url, url, ch
