# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://weebdex.org/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
from ..cache import memcache

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
            **_manga_info(self, rel["manga"]["id"]),
            "title"   : data.get("title", ""),
            "version" : data["version"],
            "volume"  : text.parse_int(data["volume"]),
            "chapter" : text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_id"   : cid,
            "date"         : self.parse_datetime_iso(data["created_at"]),
            "date_updated" : self.parse_datetime_iso(data["updated_at"]),
            "lang"    : data["language"],
            "uploader": rel["uploader"]["name"] if "uploader" in rel else "",
            "group"   : [g["name"] for g in rel.get("groups") or ()],
        }

    def images(self, _):
        data = self.data
        base = f"{data['node']}/data/{data['id']}/"

        return [
            (base + page["name"], {
                "width" : page["dimensions"][0],
                "height": page["dimensions"][1],
            })
            for page in data["data"]
        ]


class WeebdexMangaExtractor(WeebdexBase, MangaExtractor):
    """Extractor for weebdex manga"""
    chapterclass = WeebdexChapterExtractor
    pattern = BASE_PATTERN + r"/title/(\w+)"
    example = "https://weebdex.org/title/ID/SLUG"

    def chapters(self, page):
        mid = self.groups[0]
        url = f"{self.root_api}/manga/{mid}/chapters"
        params = {
            "limit": 100,
            "order": "asc" if self.config("chapter-reverse") else "desc",
        }

        base = self.root + "/chapter/"
        manga = _manga_info(self, mid)
        results = []

        while True:
            data = self.request_json(
                url, params=params, headers=self.headers_api)

            for ch in data["data"]:
                chapter, sep, minor = ch["chapter"].partition(".")
                ch["volume"] = text.parse_int(ch["volume"])
                ch["chapter"] = text.parse_int(chapter)
                ch["chapter_minor"] = sep + minor
                ch.update(manga)
                results.append((base + ch["id"], ch))

            if data["total"] <= data["page"] * params["limit"]:
                break
            params["page"] = data["page"] + 1

        return results


@memcache(keyarg=1)
def _manga_info(self, mid):
    url = f"{self.root_api}/manga/{mid}"
    manga = self.request_json(url, headers=self.headers_api)
    rel = manga["relationships"]

    return {
        "manga"   : manga["title"],
        "manga_id": manga["id"],
        "manga_date": self.parse_datetime_iso(manga["created_at"]),
        "year"    : manga["year"],
        "status"  : manga["status"],
        "origin"  : manga["language"],
        "description": manga["description"],
        "demographic": manga["demographic"],
        "tags"    : [f"{t['group']}:{t['name']}" for t in rel["tags"]],
        "author"  : [a["name"] for a in rel["authors"]],
        "artist"  : [a["name"] for a in rel["artists"]],
    }
