# -*- coding: utf-8 -*-

# Copyright 2018-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangadex.org/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import memcache
from collections import defaultdict

BASE_PATTERN = r"(?:https?://)?(?:www\.)?mangadex\.(?:org|cc)"


class MangadexExtractor(Extractor):
    """Base class for mangadex extractors"""
    category = "mangadex"
    directory_fmt = (
        "{category}", "{manga}",
        "{volume:?v/ />02}c{chapter:>03}{chapter_minor}{title:?: //}")
    filename_fmt = (
        "{manga}_c{chapter:>03}{chapter_minor}_{page:>03}.{extension}")
    archive_fmt = "{chapter_id}_{page}"
    root = "https://mangadex.org"
    useragent = util.USERAGENT
    _cache = {}

    def _init(self):
        self.uuid = self.groups[0]
        self.api = self.utils().MangadexAPI(self)

    def items(self):
        for chapter in self.chapters():
            uuid = chapter["id"]
            data = self._transform(chapter)
            data["_extractor"] = MangadexChapterExtractor
            self._cache[uuid] = data
            yield Message.Queue, f"{self.root}/chapter/{uuid}", data

    def _items_manga(self):
        data = {"_extractor": MangadexMangaExtractor}
        for manga in self.manga():
            url = f"{self.root}/title/{manga['id']}"
            yield Message.Queue, url, data

    def _transform(self, chapter):
        relationships = defaultdict(list)
        for item in chapter["relationships"]:
            relationships[item["type"]].append(item)

        cattributes = chapter["attributes"]
        if lang := cattributes.get("translatedLanguage"):
            lang = lang.partition("-")[0]

        if cattributes["chapter"]:
            chnum, sep, minor = cattributes["chapter"].partition(".")
        else:
            chnum, sep, minor = 0, "", ""

        return {
            **_manga_info(self, relationships["manga"][0]["id"]),
            "title"   : cattributes["title"],
            "volume"  : text.parse_int(cattributes["volume"]),
            "chapter" : text.parse_int(chnum),
            "chapter_minor": f"{sep}{minor}",
            "chapter_id": chapter["id"],
            "date"    : self.parse_datetime_iso(cattributes["publishAt"]),
            "group"   : [group["attributes"]["name"]
                         for group in relationships["scanlation_group"]],
            "lang"    : lang,
            "count"   : cattributes["pages"],
            "_external_url": cattributes.get("externalUrl"),
        }


class MangadexCoversExtractor(MangadexExtractor):
    """Extractor for mangadex manga covers"""
    subcategory = "covers"
    directory_fmt = ("{category}", "{manga}", "Covers")
    filename_fmt = "{volume:>02}_{lang}.{extension}"
    archive_fmt = "c_{cover_id}"
    pattern = (rf"{BASE_PATTERN}/(?:title|manga)/(?!follows|feed$)([0-9a-f-]+)"
               rf"(?:/[^/?#]+)?\?tab=art")
    example = ("https://mangadex.org/title"
               "/01234567-89ab-cdef-0123-456789abcdef?tab=art")

    def items(self):
        base = f"{self.root}/covers/{self.uuid}/"
        for cover in self.api.covers_manga(self.uuid):
            data = self._transform_cover(cover)
            name = data["cover"]
            text.nameext_from_url(name, data)
            data["cover_id"] = data["filename"]
            yield Message.Directory, data
            yield Message.Url, f"{base}{name}", data

    def _transform_cover(self, cover):
        relationships = defaultdict(list)
        for item in cover["relationships"]:
            relationships[item["type"]].append(item)
        cattributes = cover["attributes"]

        return {
            **_manga_info(self, relationships["manga"][0]["id"]),
            "cover"   : cattributes["fileName"],
            "lang"    : cattributes.get("locale"),
            "volume"  : text.parse_int(cattributes["volume"]),
            "date"    : self.parse_datetime_iso(cattributes["createdAt"]),
            "date_updated": self.parse_datetime_iso(cattributes["updatedAt"]),
        }


class MangadexChapterExtractor(MangadexExtractor):
    """Extractor for manga-chapters from mangadex.org"""
    subcategory = "chapter"
    pattern = rf"{BASE_PATTERN}/chapter/([0-9a-f-]+)"
    example = ("https://mangadex.org/chapter"
               "/01234567-89ab-cdef-0123-456789abcdef")

    def items(self):
        try:
            data = self._cache.pop(self.uuid)
        except KeyError:
            chapter = self.api.chapter(self.uuid)
            data = self._transform(chapter)

        if data.get("_external_url") and not data["count"]:
            raise exception.AbortExtraction(
                f"Chapter {data['chapter']}{data['chapter_minor']} is not "
                f"available on MangaDex and can instead be read on the "
                f"official publisher's website at {data['_external_url']}.")

        yield Message.Directory, data

        server = self.api.athome_server(self.uuid)
        chapter = server["chapter"]
        base = f"{server['baseUrl']}/data/{chapter['hash']}/"

        enum = util.enumerate_reversed if self.config(
            "page-reverse") else enumerate
        for data["page"], page in enum(chapter["data"], 1):
            text.nameext_from_url(page, data)
            yield Message.Url, f"{base}{page}", data


class MangadexMangaExtractor(MangadexExtractor):
    """Extractor for manga from mangadex.org"""
    subcategory = "manga"
    pattern = rf"{BASE_PATTERN}/(?:title|manga)/(?!follows|feed$)([0-9a-f-]+)"
    example = ("https://mangadex.org/title"
               "/01234567-89ab-cdef-0123-456789abcdef")

    def chapters(self):
        return self.api.manga_feed(self.uuid)


class MangadexFeedExtractor(MangadexExtractor):
    """Extractor for chapters from your Updates Feed"""
    subcategory = "feed"
    pattern = rf"{BASE_PATTERN}/titles?/feed$()"
    example = "https://mangadex.org/title/feed"

    def chapters(self):
        return self.api.user_follows_manga_feed()


class MangadexFollowingExtractor(MangadexExtractor):
    """Extractor for followed manga from your Library"""
    subcategory = "following"
    pattern = rf"{BASE_PATTERN}/titles?/follows(?:\?([^#]+))?$"
    example = "https://mangadex.org/title/follows"

    items = MangadexExtractor._items_manga

    def manga(self):
        return self.api.user_follows_manga()


class MangadexListExtractor(MangadexExtractor):
    """Extractor for mangadex MDLists"""
    subcategory = "list"
    pattern = (rf"{BASE_PATTERN}"
               rf"/list/([0-9a-f-]+)(?:/[^/?#]*)?(?:\?tab=(\w+))?")
    example = ("https://mangadex.org/list"
               "/01234567-89ab-cdef-0123-456789abcdef/NAME")

    def __init__(self, match):
        if match[2] == "feed":
            self.subcategory = "list-feed"
        else:
            self.items = self._items_manga
        MangadexExtractor.__init__(self, match)

    def chapters(self):
        return self.api.list_feed(self.uuid)

    def manga(self):
        return [
            item
            for item in self.api.list(self.uuid)["relationships"]
            if item["type"] == "manga"
        ]


class MangadexAuthorExtractor(MangadexExtractor):
    """Extractor for mangadex authors"""
    subcategory = "author"
    pattern = rf"{BASE_PATTERN}/author/([0-9a-f-]+)"
    example = ("https://mangadex.org/author"
               "/01234567-89ab-cdef-0123-456789abcdef/NAME")

    def items(self):
        for manga in self.api.manga_author(self.uuid):
            manga["_extractor"] = MangadexMangaExtractor
            url = f"{self.root}/title/{manga['id']}"
            yield Message.Queue, url, manga


@memcache(keyarg=1)
def _manga_info(self, uuid):
    manga = self.api.manga(uuid)

    rel = defaultdict(list)
    for item in manga["relationships"]:
        rel[item["type"]].append(item)
    mattr = manga["attributes"]

    return {
        "manga" : (mattr["title"].get("en") or
                   next(iter(mattr["title"].values()), "")),
        "manga_id": manga["id"],
        "manga_titles": [t.popitem()[1]
                         for t in mattr.get("altTitles") or ()],
        "manga_date"  : self.parse_datetime_iso(mattr.get("createdAt")),
        "description" : (mattr["description"].get("en") or
                         next(iter(mattr["description"].values()), "")),
        "demographic": mattr.get("publicationDemographic"),
        "origin": mattr.get("originalLanguage"),
        "status": mattr.get("status"),
        "year"  : mattr.get("year"),
        "rating": mattr.get("contentRating"),
        "links" : mattr.get("links"),
        "tags"  : [tag["attributes"]["name"]["en"] for tag in mattr["tags"]],
        "artist": [artist["attributes"]["name"] for artist in rel["artist"]],
        "author": [author["attributes"]["name"] for author in rel["author"]],
    }
