# -*- coding: utf-8 -*-

# Copyright 2025-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangataro.org/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
import hashlib
import time

BASE_PATTERN = r"(?:https?://)?mangataro\.org"


class MangataroBase():
    """Base class for mangataro extractors"""
    category = "mangataro"
    root = "https://mangataro.org"

    def _manga_info(self, slug):
        url = f"{self.root}/manga/{slug}"
        page = self.request(url).text
        manga = self._extract_jsonld(page)

        return {
            "manga"      : manga["name"].rpartition(
                " | ")[0].rpartition(" ")[0],
            "manga_id"   : text.extr(page, 'data-manga-id="', '"'),
            "manga_url"  : manga["url"],
            "cover"      : manga["image"],
            "author"     : manga["author"]["name"].split(", "),
            "genre"      : manga["genre"],
            "status"     : manga["status"],
            "description": text.unescape(text.extr(
                page, 'id="description-content-tab">', "</div></div>")),
            "tags"       : text.split_html(text.extr(
                page, ">Genres</h4>", "</div>")),
            "publisher"  : text.remove_html(text.extr(
                page, '>Serialization</h4>', "</div>")),
        }


class MangataroChapterExtractor(MangataroBase, ChapterExtractor):
    """Extractor for mangataro manga chapters"""
    pattern = BASE_PATTERN + r"(/read/([^/?#]+)/(?:[^/?#]*-)?(\d+))"
    example = "https://mangataro.org/read/MANGA/ch123-12345"

    def metadata(self, page):
        _, slug, chapter_id = self.groups
        comic = self._extract_jsonld(page)["@graph"][0]
        chapter = comic["position"]
        minor = chapter - int(chapter)
        desc = comic["description"].split(" - ", 3)

        return {
            **self.cache(self._manga_info, slug),
            "title"    : desc[1] if len(desc) > 3 else "",
            "chapter"  : int(chapter),
            "chapter_minor": str(round(minor, 5))[1:] if minor else "",
            "chapter_id"   : text.parse_int(chapter_id),
            "chapter_url"  : comic["url"],
            "date"         : self.parse_datetime_iso(comic["datePublished"]),
            "date_updated" : self.parse_datetime_iso(comic["dateModified"]),
        }

    def images(self, page):
        url = f"{self.root}/auth/chapter-content?chapter_id={self.groups[2]}"
        data = self.request_json(url)
        return [(url, None) for url in data["images"]]


class MangataroMangaExtractor(MangataroBase, MangaExtractor):
    """Extractor for mangataro manga"""
    chapterclass = MangataroChapterExtractor
    pattern = BASE_PATTERN + r"/manga/([^/?#]+)"
    example = "https://mangataro.org/manga/MANGA"

    def chapters(self, _):
        manga = self.cache(self._manga_info, self.groups[0])

        url = self.root + "/auth/manga-chapters"
        params = {
            "manga_id": manga["manga_id"],
            "offset"  : 0,
            "limit"   : 500,  # values higher than 500 have no effect
            "order"   : "DESC",
        }
        headers = {
            "Referer"       : manga["manga_url"],
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        results = []
        while True:
            self._update_params(params)
            data = self.request_json(url, params=params, headers=headers)

            for ch in data["chapters"]:
                chapter, sep, minor = ch["chapter"].partition(".")
                results.append((ch["url"], {
                    **manga,
                    "chapter_id"   : text.parse_int(ch.pop("id", None)),
                    **ch,
                    "chapter"      : text.parse_int(chapter),
                    "chapter_minor": "." + minor if sep else "",
                }))

            if not data.get("has_more"):
                break
            params["offset"] += (data.get("limit") or params["limit"])
        return results

    def _update_params(self, params):
        # adapted from dazedcat19/FMD2
        # https://github.com/dazedcat19/FMD2/blob/master/lua/modules/MangaTaro.lua
        if (ts := int(time.time())) == params.get("_ts"):
            return
        Y, m, d, H, _, _, _, _, _ = time.gmtime(ts)
        secret = f"{ts}mng_ch_{Y:>04}{m:>02}{d:>02}{H:>02}"
        params["_t"] = hashlib.md5(secret.encode()).hexdigest()[:16]
        params["_ts"] = ts
