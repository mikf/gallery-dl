# -*- coding: utf-8 -*-

# Copyright 2014-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://e621.net/ and other e621 instances"""

from .common import Extractor, Message
from . import danbooru
from ..cache import memcache
from .. import text, util


class E621Extractor(danbooru.DanbooruExtractor):
    """Base class for e621 extractors"""
    basecategory = "E621"
    page_limit = 750
    page_start = None
    per_page = 320
    useragent = util.USERAGENT + " (by mikf)"
    request_interval_min = 1.0

    def items(self):
        if includes := self.config("metadata") or ():
            if isinstance(includes, str):
                includes = includes.split(",")
            elif not isinstance(includes, (list, tuple)):
                includes = ("notes", "pools")

        notes = ("notes" in includes)
        pools = ("pools" in includes)

        data = self.metadata()
        for post in self.posts():
            file = post["file"]

            if not file["url"]:
                md5 = file["md5"]
                file["url"] = (f"https://static1.{self.root[8:]}/data"
                               f"/{md5[0:2]}/{md5[2:4]}/{md5}.{file['ext']}")

            if notes and post.get("has_notes"):
                post["notes"] = self._get_notes(post["id"])

            if pools and post["pools"]:
                post["pools"] = self._get_pools(
                    ",".join(map(str, post["pools"])))

            post["filename"] = file["md5"]
            post["extension"] = file["ext"]
            post["date"] = self.parse_datetime_iso(post["created_at"])

            post.update(data)
            yield Message.Directory, post
            yield Message.Url, file["url"], post

    def items_artists(self):
        for artist in self.artists():
            artist["_extractor"] = E621TagExtractor
            url = f"{self.root}/posts?tags={text.quote(artist['name'])}"
            yield Message.Queue, url, artist

    def _get_notes(self, id):
        return self.request_json(
            f"{self.root}/notes.json?search[post_id]={id}")

    @memcache(keyarg=1)
    def _get_pools(self, ids):
        pools = self.request_json(
            f"{self.root}/pools.json?search[id]={ids}")
        for pool in pools:
            pool["name"] = pool["name"].replace("_", " ")
        return pools


BASE_PATTERN = E621Extractor.update({
    "e621": {
        "root": "https://e621.net",
        "pattern": r"e621\.(?:net|cc)",
    },
    "e926": {
        "root": "https://e926.net",
        "pattern": r"e926\.net",
    },
    "e6ai": {
        "root": "https://e6ai.net",
        "pattern": r"e6ai\.net",
    },
})


class E621TagExtractor(E621Extractor, danbooru.DanbooruTagExtractor):
    """Extractor for e621 posts from tag searches"""
    pattern = rf"{BASE_PATTERN}/posts?(?:\?[^#]*?tags=|/index/\d+/)([^&#]*)"
    example = "https://e621.net/posts?tags=TAG"


class E621PoolExtractor(E621Extractor, danbooru.DanbooruPoolExtractor):
    """Extractor for e621 pools"""
    pattern = rf"{BASE_PATTERN}/pool(?:s|/show)/(\d+)"
    example = "https://e621.net/pools/12345"

    def posts(self):
        self.log.info("Collecting posts of pool %s", self.pool_id)

        id_to_post = {
            post["id"]: post
            for post in self._pagination(
                "/posts.json", {"tags": "pool:" + self.pool_id})
        }

        posts = []
        for num, pid in enumerate(self.post_ids, 1):
            if pid in id_to_post:
                post = id_to_post[pid]
                post["num"] = num
                posts.append(post)
            else:
                self.log.warning("Post %s is unavailable", pid)
        return posts


class E621PostExtractor(E621Extractor, danbooru.DanbooruPostExtractor):
    """Extractor for single e621 posts"""
    pattern = rf"{BASE_PATTERN}/post(?:s|/show)/(\d+)"
    example = "https://e621.net/posts/12345"

    def posts(self):
        url = f"{self.root}/posts/{self.groups[-1]}.json"
        return (self.request_json(url)["post"],)


class E621PopularExtractor(E621Extractor, danbooru.DanbooruPopularExtractor):
    """Extractor for popular images from e621"""
    pattern = rf"{BASE_PATTERN}/explore/posts/popular(?:\?([^#]*))?"
    example = "https://e621.net/explore/posts/popular"

    def posts(self):
        return self._pagination("/popular.json", self.params)


class E621ArtistExtractor(E621Extractor, danbooru.DanbooruArtistExtractor):
    """Extractor for e621 artists"""
    subcategory = "artist"
    pattern = rf"{BASE_PATTERN}/artists/(\d+)"
    example = "https://e621.net/artists/12345"

    items = E621Extractor.items_artists


class E621ArtistSearchExtractor(E621Extractor,
                                danbooru.DanbooruArtistSearchExtractor):
    """Extractor for e621 artist searches"""
    subcategory = "artist-search"
    pattern = rf"{BASE_PATTERN}/artists/?\?([^#]+)"
    example = "https://e621.net/artists?QUERY"

    items = E621Extractor.items_artists


class E621FavoriteExtractor(E621Extractor):
    """Extractor for e621 favorites"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "Favorites", "{user_id}")
    archive_fmt = "f_{user_id}_{id}"
    pattern = rf"{BASE_PATTERN}/favorites(?:\?([^#]*))?"
    example = "https://e621.net/favorites"

    def metadata(self):
        self.query = text.parse_query(self.groups[-1])
        return {"user_id": self.query.get("user_id", "")}

    def posts(self):
        return self._pagination("/favorites.json", self.query)


class E621FrontendExtractor(Extractor):
    """Extractor for alternative e621 frontends"""
    basecategory = "E621"
    basesubcategory = ""
    category = "e621"
    subcategory = "frontend"
    pattern = r"(?:https?://)?e621\.(?:cc/\?tags|anthro\.fr/\?q)=([^&#]*)"
    example = "https://e621.cc/?tags=TAG"

    def initialize(self):
        pass

    def items(self):
        url = "https://e621.net/posts?tags=" + self.groups[0]
        data = {"_extractor": E621TagExtractor}
        yield Message.Queue, url, data
