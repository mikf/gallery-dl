# -*- coding: utf-8 -*-

# Copyright 2018-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangadex.org/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache, memcache
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
        self.api = MangadexAPI(self)

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
            yield Message.Directory, "", data
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

        yield Message.Directory, "", data

        if self.config("data-saver", False):
            path = "data-saver"
            key = "dataSaver"
        else:
            path = key = "data"

        server = self.api.athome_server(self.uuid)
        chapter = server["chapter"]
        base = f"{server['baseUrl']}/{path}/{chapter['hash']}/"

        enum = util.enumerate_reversed if self.config(
            "page-reverse") else enumerate
        for data["page"], page in enum(chapter[key], 1):
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


class MangadexAPI():
    """Interface for the MangaDex API v5

    https://api.mangadex.org/docs/
    """

    def __init__(self, extr):
        self.extractor = extr
        self.headers = None
        self.headers_auth = {}

        self.username, self.password = extr._get_auth_info()
        if self.username:
            self.client_id = cid = extr.config("client-id")
            self.client_secret = extr.config("client-secret")
            if cid:
                self._authenticate_impl = self._authenticate_impl_client
            else:
                self._authenticate_impl = self._authenticate_impl_legacy
        else:
            self.authenticate = util.noop

        server = extr.config("api-server")
        self.root = ("https://api.mangadex.org" if server is None
                     else text.ensure_http_scheme(server).rstrip("/"))

    def athome_server(self, uuid):
        return self._call(f"/at-home/server/{uuid}")

    def author(self, uuid, manga=False):
        params = {"includes[]": ("manga",)} if manga else None
        return self._call(f"/author/{uuid}", params)["data"]

    def chapter(self, uuid):
        params = {"includes[]": ("scanlation_group",)}
        return self._call(f"/chapter/{uuid}", params)["data"]

    def covers_manga(self, uuid):
        params = {"manga[]": uuid}
        return self._pagination_covers("/cover", params)

    def list(self, uuid):
        return self._call(f"/list/{uuid}", None, True)["data"]

    def list_feed(self, uuid):
        return self._pagination_chapters(f"/list/{uuid}/feed", None, True)

    @memcache(keyarg=1)
    def manga(self, uuid):
        params = {"includes[]": ("artist", "author")}
        return self._call(f"/manga/{uuid}", params)["data"]

    def manga_author(self, uuid_author):
        params = {"authorOrArtist": uuid_author}
        return self._pagination_manga("/manga", params)

    def manga_feed(self, uuid):
        order = "desc" if self.extractor.config("chapter-reverse") else "asc"
        params = {
            "order[volume]" : order,
            "order[chapter]": order,
        }
        return self._pagination_chapters(f"/manga/{uuid}/feed", params)

    def user_follows_manga(self):
        params = {"contentRating": None}
        return self._pagination_manga(
            "/user/follows/manga", params, True)

    def user_follows_manga_feed(self):
        params = {"order[publishAt]": "desc"}
        return self._pagination_chapters(
            "/user/follows/manga/feed", params, True)

    def authenticate(self):
        self.headers_auth["Authorization"] = \
            self._authenticate_impl(self.username, self.password)

    @cache(maxage=900, keyarg=1)
    def _authenticate_impl_client(self, username, password):
        if refresh_token := _refresh_token_cache((username, "personal")):
            self.extractor.log.info("Refreshing access token")
            data = {
                "grant_type"   : "refresh_token",
                "refresh_token": refresh_token,
                "client_id"    : self.client_id,
                "client_secret": self.client_secret,
            }
        else:
            self.extractor.log.info("Logging in as %s", username)
            data = {
                "grant_type"   : "password",
                "username"     : self.username,
                "password"     : self.password,
                "client_id"    : self.client_id,
                "client_secret": self.client_secret,
            }

        self.extractor.log.debug("Using client-id '%s…'", self.client_id[:24])
        url = ("https://auth.mangadex.org/realms/mangadex"
               "/protocol/openid-connect/token")
        data = self.extractor.request_json(
            url, method="POST", data=data, fatal=None)

        try:
            access_token = data["access_token"]
        except Exception:
            raise exception.AuthenticationError(data.get("error_description"))

        if refresh_token != data.get("refresh_token"):
            _refresh_token_cache.update(
                (username, "personal"), data["refresh_token"])

        return f"Bearer {access_token}"

    @cache(maxage=900, keyarg=1)
    def _authenticate_impl_legacy(self, username, password):
        if refresh_token := _refresh_token_cache(username):
            self.extractor.log.info("Refreshing access token")
            url = f"{self.root}/auth/refresh"
            json = {"token": refresh_token}
        else:
            self.extractor.log.info("Logging in as %s", username)
            url = f"{self.root}/auth/login"
            json = {"username": username, "password": password}

        self.extractor.log.debug("Using legacy login method")
        data = self.extractor.request_json(
            url, method="POST", json=json, fatal=None)
        if data.get("result") != "ok":
            raise exception.AuthenticationError()

        if refresh_token != data["token"]["refresh"]:
            _refresh_token_cache.update(username, data["token"]["refresh"])
        return f"Bearer {data['token']['session']}"

    def _call(self, endpoint, params=None, auth=False):
        url = f"{self.root}{endpoint}"
        headers = self.headers_auth if auth else self.headers

        while True:
            if auth:
                self.authenticate()
            response = self.extractor.request(
                url, params=params, headers=headers, fatal=None)

            if response.status_code < 400:
                return response.json()
            if response.status_code == 429:
                until = response.headers.get("X-RateLimit-Retry-After")
                self.extractor.wait(until=until)
                continue

            msg = ", ".join(f'{error["title"]}: "{error["detail"]}"'
                            for error in response.json()["errors"])
            raise exception.AbortExtraction(
                f"{response.status_code} {response.reason} ({msg})")

    def _pagination_chapters(self, endpoint, params=None, auth=False):
        if params is None:
            params = {}

        lang = self.extractor.config("lang")
        if isinstance(lang, str) and "," in lang:
            lang = lang.split(",")
        params["translatedLanguage[]"] = lang
        params["includes[]"] = ("scanlation_group",)

        return self._pagination(endpoint, params, auth)

    def _pagination_manga(self, endpoint, params=None, auth=False):
        if params is None:
            params = {}

        return self._pagination(endpoint, params, auth)

    def _pagination_covers(self, endpoint, params=None, auth=False):
        if params is None:
            params = {}

        lang = self.extractor.config("lang")
        if isinstance(lang, str) and "," in lang:
            lang = lang.split(",")
        params["locales"] = lang
        params["contentRating"] = None
        params["order[volume]"] = \
            "desc" if self.extractor.config("chapter-reverse") else "asc"

        return self._pagination(endpoint, params, auth)

    def _pagination(self, endpoint, params, auth=False):
        config = self.extractor.config

        if "contentRating" not in params:
            ratings = config("ratings")
            if ratings is None:
                ratings = ("safe", "suggestive", "erotica", "pornographic")
            elif isinstance(ratings, str):
                ratings = ratings.split(",")
            params["contentRating[]"] = ratings
        params["offset"] = 0

        if api_params := config("api-parameters"):
            params.update(api_params)

        while True:
            data = self._call(endpoint, params, auth)
            yield from data["data"]

            params["offset"] = data["offset"] + data["limit"]
            if params["offset"] >= data["total"]:
                return


@cache(maxage=90*86400, keyarg=0)
def _refresh_token_cache(username):
    return None


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
