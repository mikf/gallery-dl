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
            yield Message.Queue, self.root + "/chapter/" + uuid, data

    def _items_manga(self):
        data = {"_extractor": MangadexMangaExtractor}
        for manga in self.manga():
            url = "{}/title/{}".format(self.root, manga["id"])
            yield Message.Queue, url, data

    def _transform(self, chapter):
        relationships = defaultdict(list)
        for item in chapter["relationships"]:
            relationships[item["type"]].append(item)
        manga = self.api.manga(relationships["manga"][0]["id"])
        for item in manga["relationships"]:
            relationships[item["type"]].append(item)

        cattributes = chapter["attributes"]
        mattributes = manga["attributes"]

        lang = cattributes.get("translatedLanguage")
        if lang:
            lang = lang.partition("-")[0]

        if cattributes["chapter"]:
            chnum, sep, minor = cattributes["chapter"].partition(".")
        else:
            chnum, sep, minor = 0, "", ""

        data = {
            "manga"   : (mattributes["title"].get("en") or
                         next(iter(mattributes["title"].values()))),
            "manga_id": manga["id"],
            "title"   : cattributes["title"],
            "volume"  : text.parse_int(cattributes["volume"]),
            "chapter" : text.parse_int(chnum),
            "chapter_minor": sep + minor,
            "chapter_id": chapter["id"],
            "date"    : text.parse_datetime(cattributes["publishAt"]),
            "lang"    : lang,
            "language": util.code_to_language(lang),
            "count"   : cattributes["pages"],
            "_external_url": cattributes.get("externalUrl"),
        }

        data["artist"] = [artist["attributes"]["name"]
                          for artist in relationships["artist"]]
        data["author"] = [author["attributes"]["name"]
                          for author in relationships["author"]]
        data["group"] = [group["attributes"]["name"]
                         for group in relationships["scanlation_group"]]

        data["status"] = mattributes["status"]
        data["tags"] = [tag["attributes"]["name"]["en"]
                        for tag in mattributes["tags"]]

        return data


class MangadexChapterExtractor(MangadexExtractor):
    """Extractor for manga-chapters from mangadex.org"""
    subcategory = "chapter"
    pattern = BASE_PATTERN + r"/chapter/([0-9a-f-]+)"
    example = ("https://mangadex.org/chapter"
               "/01234567-89ab-cdef-0123-456789abcdef")

    def items(self):
        try:
            data = self._cache.pop(self.uuid)
        except KeyError:
            chapter = self.api.chapter(self.uuid)
            data = self._transform(chapter)

        if data.get("_external_url") and not data["count"]:
            raise exception.StopExtraction(
                "Chapter %s%s is not available on MangaDex and can instead be "
                "read on the official publisher's website at %s.",
                data["chapter"], data["chapter_minor"], data["_external_url"])

        yield Message.Directory, data

        server = self.api.athome_server(self.uuid)
        chapter = server["chapter"]
        base = "{}/data/{}/".format(server["baseUrl"], chapter["hash"])

        enum = util.enumerate_reversed if self.config(
            "page-reverse") else enumerate
        for data["page"], page in enum(chapter["data"], 1):
            text.nameext_from_url(page, data)
            yield Message.Url, base + page, data


class MangadexMangaExtractor(MangadexExtractor):
    """Extractor for manga from mangadex.org"""
    subcategory = "manga"
    pattern = BASE_PATTERN + r"/(?:title|manga)/(?!follows|feed$)([0-9a-f-]+)"
    example = ("https://mangadex.org/title"
               "/01234567-89ab-cdef-0123-456789abcdef")

    def chapters(self):
        return self.api.manga_feed(self.uuid)


class MangadexFeedExtractor(MangadexExtractor):
    """Extractor for chapters from your Updates Feed"""
    subcategory = "feed"
    pattern = BASE_PATTERN + r"/titles?/feed$()"
    example = "https://mangadex.org/title/feed"

    def chapters(self):
        return self.api.user_follows_manga_feed()


class MangadexFollowingExtractor(MangadexExtractor):
    """Extractor for followed manga from your Library"""
    subcategory = "following"
    pattern = BASE_PATTERN + r"/titles?/follows(?:\?([^#]+))?$"
    example = "https://mangadex.org/title/follows"

    items = MangadexExtractor._items_manga

    def manga(self):
        return self.api.user_follows_manga()


class MangadexListExtractor(MangadexExtractor):
    """Extractor for mangadex MDLists"""
    subcategory = "list"
    pattern = (BASE_PATTERN +
               r"/list/([0-9a-f-]+)(?:/[^/?#]*)?(?:\?tab=(\w+))?")
    example = ("https://mangadex.org/list"
               "/01234567-89ab-cdef-0123-456789abcdef/NAME")

    def __init__(self, match):
        if match.group(2) == "feed":
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
    pattern = BASE_PATTERN + r"/author/([0-9a-f-]+)"
    example = ("https://mangadex.org/author"
               "/01234567-89ab-cdef-0123-456789abcdef/NAME")

    def items(self):
        for manga in self.api.manga_author(self.uuid):
            manga["_extractor"] = MangadexMangaExtractor
            url = "{}/title/{}".format(self.root, manga["id"])
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
        return self._call("/at-home/server/" + uuid)

    def author(self, uuid, manga=False):
        params = {"includes[]": ("manga",)} if manga else None
        return self._call("/author/" + uuid, params)["data"]

    def chapter(self, uuid):
        params = {"includes[]": ("scanlation_group",)}
        return self._call("/chapter/" + uuid, params)["data"]

    def list(self, uuid):
        return self._call("/list/" + uuid, None, True)["data"]

    def list_feed(self, uuid):
        return self._pagination_chapters("/list/" + uuid + "/feed", None, True)

    @memcache(keyarg=1)
    def manga(self, uuid):
        params = {"includes[]": ("artist", "author")}
        return self._call("/manga/" + uuid, params)["data"]

    def manga_author(self, uuid_author):
        params = {"authorOrArtist": uuid_author}
        return self._pagination_manga("/manga", params)

    def manga_feed(self, uuid):
        order = "desc" if self.extractor.config("chapter-reverse") else "asc"
        params = {
            "order[volume]" : order,
            "order[chapter]": order,
        }
        return self._pagination_chapters("/manga/" + uuid + "/feed", params)

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
        refresh_token = _refresh_token_cache((username, "personal"))
        if refresh_token:
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
        data = self.extractor.request(
            url, method="POST", data=data, fatal=None).json()

        try:
            access_token = data["access_token"]
        except Exception:
            raise exception.AuthenticationError(data.get("error_description"))

        if refresh_token != data.get("refresh_token"):
            _refresh_token_cache.update(
                (username, "personal"), data["refresh_token"])

        return "Bearer " + access_token

    @cache(maxage=900, keyarg=1)
    def _authenticate_impl_legacy(self, username, password):
        refresh_token = _refresh_token_cache(username)
        if refresh_token:
            self.extractor.log.info("Refreshing access token")
            url = self.root + "/auth/refresh"
            json = {"token": refresh_token}
        else:
            self.extractor.log.info("Logging in as %s", username)
            url = self.root + "/auth/login"
            json = {"username": username, "password": password}

        self.extractor.log.debug("Using legacy login method")
        data = self.extractor.request(
            url, method="POST", json=json, fatal=None).json()
        if data.get("result") != "ok":
            raise exception.AuthenticationError()

        if refresh_token != data["token"]["refresh"]:
            _refresh_token_cache.update(username, data["token"]["refresh"])
        return "Bearer " + data["token"]["session"]

    def _call(self, endpoint, params=None, auth=False):
        url = self.root + endpoint
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

            msg = ", ".join('{title}: "{detail}"'.format_map(error)
                            for error in response.json()["errors"])
            raise exception.StopExtraction(
                "%s %s (%s)", response.status_code, response.reason, msg)

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

    def _pagination(self, endpoint, params, auth=False):
        config = self.extractor.config

        if "contentRating" not in params:
            ratings = config("ratings")
            if ratings is None:
                ratings = ("safe", "suggestive", "erotica", "pornographic")
            params["contentRating[]"] = ratings
        params["offset"] = 0

        api_params = config("api-parameters")
        if api_params:
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
