# -*- coding: utf-8 -*-

# Copyright 2025-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://weebdex.org/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?weebdex\.org"


class WeebdexBase():
    """Base class for weebdex extractors"""
    category = "weebdex"
    root = "https://weebdex.org"
    root_api = "https://api.weebdex.org"
    request_interval = 0.2  # 5 requests per second

    def _init(self):
        self.headers_api = {
            "Referer": self.root + "/",
            "Origin" : self.root,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }

    def _manga_info(self, mid):
        url = f"{self.root_api}/manga/{mid}"
        manga = self.request_json(url, headers=self.headers_api)
        rel = manga["relationships"]

        return {
            "manga"   : manga.get("title"),
            "manga_id": manga.get("id"),
            "manga_date": self.parse_datetime_iso(manga.get("created_at")),
            "year"    : manga.get("year"),
            "status"  : manga.get("status"),
            "origin"  : manga.get("language"),
            "description": manga.get("description"),
            "demographic": manga.get("demographic"),
            "tags"    : [f"{t['group']}:{t['name']}"
                         for t in rel.get("tags") or ()],
            "author"  : [a["name"] for a in rel.get("authors") or ()],
            "artist"  : [a["name"] for a in rel.get("artists") or ()],
        }


class WeebdexChapterExtractor(WeebdexBase, ChapterExtractor):
    """Extractor for weebdex manga chapters"""
    archive_fmt = "{chapter_id}_{version}_{page}"
    pattern = BASE_PATTERN + r"/chapter/(\w+)"
    example = "https://weebdex.org/chapter/ID/PAGE"

    def metadata(self, _):
        cid = self.groups[0]
        url = f"{self.root_api}/chapter/{cid}"
        self.data = data = self.request_json(url, headers=self.headers_api)

        rel = data.pop("relationships")
        chapter, sep, minor = data["chapter"].partition(".")

        return {
            **self.cache(self._manga_info, rel["manga"]["id"]),
            "title"   : data.get("title", ""),
            "version" : data.get("version", 0),
            "volume"  : text.parse_int(data.get("volume")),
            "chapter" : text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_id"   : cid,
            "date"         : self.parse_datetime_iso(data.get("created_at")),
            "date_updated" : self.parse_datetime_iso(data.get("updated_at")),
            "lang"    : data.get("language"),
            "uploader": rel["uploader"]["name"] if "uploader" in rel else "",
            "group"   : [g["name"] for g in rel.get("groups") or ()],
        }

    def images(self, _):
        data = self.data
        base = f"{data['node']}/data/{data['id']}/"

        if self.config("data-saver", False):
            pages = data["data_optimized"]
            original = False
        else:
            pages = data["data"]
            original = True

        return [
            (base + page["name"], {
                "width" : page["dimensions"][0],
                "height": page["dimensions"][1],
                "original": original,
            })
            for page in pages
        ]


class WeebdexMangaExtractor(WeebdexBase, MangaExtractor):
    """Extractor for weebdex manga"""
    chapterclass = WeebdexChapterExtractor
    reverse = False
    pattern = BASE_PATTERN + r"/title/(\w+)(?:/[^/?#]+/?\?([^#]+))?"
    example = "https://weebdex.org/title/ID/SLUG"

    def chapters(self, page):
        mid, qs = self.groups

        params = text.parse_query(qs)
        params.setdefault("limit", 100)
        params.setdefault("order", "asc")
        if "tlang" not in params:
            params["tlang"] = self.config("lang", "en")

        url = f"{self.root_api}/manga/{mid}/chapters"
        base = self.root + "/chapter/"
        manga = self.cache(self._manga_info, mid)
        results = []

        while True:
            data = self.request_json(
                url, params=params, headers=self.headers_api)

            for ch in data["data"]:
                chapter, sep, minor = ch["chapter"].partition(".")
                ch["volume"] = text.parse_int(ch.get("volume"))
                ch["chapter"] = text.parse_int(chapter)
                ch["chapter_minor"] = sep + minor
                ch.update(manga)
                results.append((base + ch["id"], ch))

            if data["total"] <= data["page"] * params["limit"]:
                break
            params["page"] = data["page"] + 1

        return results
