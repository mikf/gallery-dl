# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://comick.io/"""

from .common import ChapterExtractor, MangaExtractor, Message
from .. import text
from ..cache import memcache

BASE_PATTERN = r"(?:https?://)?(?:www\.)?comick\.io"


class ComickBase():
    """Base class for comick.io extractors"""
    category = "comick"
    root = "https://comick.io"


class ComickChapterExtractor(ComickBase, ChapterExtractor):
    """Extractor for comick.io manga chapters"""
    archive_fmt = "{chapter_hid}_{page}"
    pattern = (BASE_PATTERN + r"/comic/([\w-]+)"
               r"/(\w+(?:-(?:chapter|volume)-[^/?#]+)?)")
    example = "https://comick.io/comic/MANGA/ID-chapter-123-en"

    def metadata(self, page):
        slug, chstr = self.groups
        manga = _manga_info(self, slug)
        props = _chapter_info(self, manga, chstr)

        ch = props["chapter"]
        self._images = ch["md_images"]

        if chapter := ch["chap"]:
            chapter, sep, minor = chapter.partition(".")
        else:
            chapter = 0
            sep = minor = ""

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
            ("https://meo.comick.pictures/" + img["b2key"], {
                "width"    : img["w"],
                "height"   : img["h"],
                "size"     : img["s"],
                "optimized": img["optimized"],
            })
            for img in self._images
        ]


class ComickMangaExtractor(ComickBase, MangaExtractor):
    """Extractor for comick.io manga"""
    pattern = BASE_PATTERN + r"/comic/([\w-]+)/?(?:\?([^#]+))?"
    example = "https://comick.io/comic/MANGA"

    def items(self):
        manga = _manga_info(self, self.groups[0])
        slug = manga["manga_slug"]
        _manga_info.update(slug, manga)

        for ch in self.chapters(manga):
            ch.update(manga)
            ch["_extractor"] = ComickChapterExtractor

            if chapter := ch["chap"]:
                url = (f"{self.root}/comic/{slug}"
                       f"/{ch['hid']}-chapter-{chapter}-{ch['lang']}")
                chapter, sep, minor = chapter.partition(".")
                ch["volume"] = text.parse_int(ch["vol"])
                ch["chapter"] = text.parse_int(chapter)
                ch["chapter_minor"] = sep + minor
            elif volume := ch["vol"]:
                url = (f"{self.root}/comic/{slug}"
                       f"/{ch['hid']}-volume-{volume}-{ch['lang']}")
                ch["volume"] = text.parse_int(volume)
                ch["chapter"] = 0
                ch["chapter_minor"] = ""
            else:
                url = f"{self.root}/comic/{slug}/{ch['hid']}"
                ch["volume"] = ch["chapter"] = 0
                ch["chapter_minor"] = ""

            yield Message.Queue, url, ch

    def chapters(self, manga):
        info = True
        slug, query = self.groups

        url = f"https://api.comick.io/comic/{manga['manga_hid']}/chapters"
        headers = {
            "Origin": "https://comick.io",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }

        query = text.parse_query_list(query, ("lang",))

        if (lang := query.get("lang")) or (lang := self.config("lang")):
            if not isinstance(lang, str):
                lang = ",".join(lang)
        else:
            lang = None

        params = {"lang": lang}
        params["page"] = page = text.parse_int(query.get("page"), 1)

        if date_order := query.get("date-order"):
            params["date-order"] = date_order
        elif chap_order := query.get("chap-order"):
            params["chap-order"] = chap_order
        else:
            params["chap-order"] = \
                "0" if self.config("chapter-reverse", False) else "1"

        group = query.get("group")
        if group == "0":
            group = None

        while True:
            data = self.request_json(url, params=params, headers=headers)
            limit = data["limit"]

            if info:
                info = False
                total = data["total"] - limit * page
                if total > limit:
                    self.log.info("Collecting %s chapters", total)

            if group is None:
                yield from data["chapters"]
            else:
                for ch in data["chapters"]:
                    if (groups := ch["group_name"]) and group in groups:
                        yield ch

            if data["total"] <= limit * page:
                return
            params["page"] = page = page + 1


@memcache(keyarg=1)
def _manga_info(self, slug):
    url = f"{self.root}/comic/{slug}"
    page = self.request(url).text
    data = self._extract_nextdata(page)
    props = data["props"]["pageProps"]
    comic = props["comic"]

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
        "manga_slug": comic["slug"],
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
        "status": "Complete" if comic["status"] == 2 else "Ongoing",
        "links" : comic["links"],
        "_build_id": data["buildId"],
    }


def _chapter_info(self, manga, chstr):
    slug = manga['manga_slug']
    url = (f"{self.root}/_next/data/{manga['_build_id']}"
           f"/comic/{slug}/{chstr}.json")
    params = {"slug": slug, "chapter": chstr}
    return self.request_json(url, params=params)["pageProps"]
