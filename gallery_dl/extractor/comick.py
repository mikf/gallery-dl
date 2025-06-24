# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://comick.io/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
from ..cache import memcache

BASE_PATTERN = r"(?:https?://)?(?:www\.)?comick\.io"


class ComickBase():
    """Base class for comick.io extractors"""
    category = "comick"
    root = "https://comick.io"

    @memcache(keyarg=1)
    def _manga_info(self, slug):
        url = f"{self.root}/comic/{slug}"
        page = self.request(url).text
        data = self._extract_nextdata(page)
        props = data["props"]["pageProps"]
        comic = props["comic"]

        map_status = {
            0: "Unknown",
            1: "Ongoing",
            2: "Complete",
        }

        genre = []
        theme = []
        format = ""
        for item in comic["md_comic_md_genres"]:
            item = item["md_genres"]
            group = item["group"]
            if group == "Genre":
                genre.append(item["name"])
            elif group == "Theme":
                theme.append(item["name"])
            else:
                format = item["name"]

        if mu := comic["mu_comics"]:
            tags = [c["mu_categories"]["title"]
                    for c in mu["mu_comic_categories"]]
            publisher = [p["mu_publishers"]["title"]
                         for p in mu["mu_comic_publishers"]]
        else:
            tags = publisher = ()

        return {
            "manga": comic["title"],
            "manga_id": comic["id"],
            "manga_hid": comic["hid"],
            "manga_slug": slug,
            "manga_titles": [t["title"] for t in comic["md_titles"]],
            "artist": [a["name"] for a in props["artists"]],
            "author": [a["name"] for a in props["authors"]],
            "genre" : genre,
            "theme" : theme,
            "format": format,
            "tags"  : tags,
            "publisher": publisher,
            "published": text.parse_int(comic["year"]),
            "description": comic["desc"],
            "demographic": props["demographic"],
            "origin": comic["iso639_1"],
            "mature": props["matureContent"],
            "rating": comic["content_rating"],
            "rank"  : comic["follow_rank"],
            "score" : text.parse_float(comic["bayesian_rating"]),
            "status": map_status[comic["status"]],
            "links" : comic["links"],
            "_build_id": data["buildId"],
        }

    def _chapter_info(self, manga, chstr):
        slug = manga['manga_slug']
        url = (f"{self.root}/_next/data/{manga['_build_id']}"
               f"/comic/{slug}/{chstr}.json")
        params = {"slug": slug, "chapter": chstr}
        return self.request_json(url, params=params)["pageProps"]


class ComickChapterExtractor(ComickBase, ChapterExtractor):
    """Extractor for comick.io manga chapters"""
    pattern = BASE_PATTERN + r"/comic/([\w-]+)/(\w+-chapter-[^/?#]+)"
    example = "https://comick.io/comic/MANGA/ID-chapter-123-en"

    def __init__(self, match):
        ChapterExtractor.__init__(self, match, False)

    def metadata(self, page):
        slug, chstr = self.groups
        manga = self._manga_info(slug)
        props = self._chapter_info(manga, chstr)

        ch = props["chapter"]
        self._images = ch["md_images"]
        chapter, sep, minor = ch["chap"].partition(".")

        return {
            **manga,
            "title"   : props["chapTitle"],
            "volume"  : text.parse_int(ch["vol"]),
            "chapter" : text.parse_int(chapter),
            "chapter_minor" : sep + minor,
            "chapter_id"    : ch["id"],
            "chapter_hid"   : ch["hid"],
            "chapter_string": chstr,
            "group"   : ch["group_name"],
            "date"    : text.parse_datetime(
                ch["created_at"][:19], "%Y-%m-%dT%H:%M:%S"),
            "date_updated"  : text.parse_datetime(
                ch["updated_at"][:19], "%Y-%m-%dT%H:%M:%S"),
            "lang"    : ch["lang"],
        }

    def images(self, page):
        return [
            ("https://meo.comick.pictures/" + img["b2key"], img)
            for img in self._images
        ]


class ComickMangaExtractor(ComickBase, MangaExtractor):
    """Extractor for comick.io manga"""
    chapterclass = ComickChapterExtractor
    pattern = BASE_PATTERN + r"/comic/([\w-]+)/?(?:\?lang=(\w{2}))?"
    example = "https://comick.io/comic/MANGA"

    def __init__(self, match):
        MangaExtractor.__init__(self, match, False)

    def chapters(self, page):
        slug, lang = self.groups
        manga = self._manga_info(slug)

        url = f"https://api.comick.io/comic/{manga['manga_hid']}/chapters"
        params = {"lang": lang}
        data = self.request_json(url, params=params)

        if data["total"] > data["limit"]:
            # workaround for manga with more than 60 chapters
            ch = data["chapters"][0]
            chstr = f"{ch['hid']}-chapter-{ch['chap']}-{ch['lang']}"
            data = self._chapter_info(manga, chstr)

        results = []
        for ch in data["chapters"]:
            url = (f"{self.root}/comic/{slug}"
                   f"/{ch['hid']}-chapter-{ch['chap']}-{ch['lang']}")

            ch.update(manga)
            chapter, sep, minor = ch["chap"].partition(".")
            ch["chapter"] = text.parse_int(chapter)
            ch["chapter_minor"] = sep + minor

            results.append((url, ch))
        return results
