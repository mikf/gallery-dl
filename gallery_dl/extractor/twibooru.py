# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://twibooru.org/"""

from .booru import BooruExtractor
from .. import text, exception
import operator

BASE_PATTERN = r"(?:https?://)?twibooru\.org"


class TwibooruExtractor(BooruExtractor):
    """Base class for twibooru extractors"""
    category = "twibooru"
    basecategory = "philomena"
    filename_fmt = "{id}_{filename}.{extension}"
    archive_fmt = "{id}"
    request_interval = 6.05
    per_page = 50
    root = "https://twibooru.org"

    def __init__(self, match):
        BooruExtractor.__init__(self, match)
        self.api = TwibooruAPI(self)

    _file_url = operator.itemgetter("view_url")

    @staticmethod
    def _prepare(post):
        post["date"] = text.parse_datetime(
            post["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")

        if "name" in post:
            name, sep, rest = post["name"].rpartition(".")
            post["filename"] = name if sep else rest


class TwibooruPostExtractor(TwibooruExtractor):
    """Extractor for single twibooru posts"""
    subcategory = "post"
    request_interval = 1.0
    pattern = BASE_PATTERN + r"/(\d+)"
    test = ("https://twibooru.org/1", {
        "pattern": r"https://cdn.twibooru.org/img/2020/7/8/1/full.png",
        "content": "aac4d1dba611883ac701aaa8f0b2b322590517ae",
        "keyword": {
            "animated": False,
            "aspect_ratio": 1.0,
            "comment_count": int,
            "created_at": "2020-07-08T22:26:55.743Z",
            "date": "dt:2020-07-08 22:26:55",
            "description": "Why have I done this?",
            "downvotes": 0,
            "duration": 0.0,
            "faves": int,
            "first_seen_at": "2020-07-08T22:26:55.743Z",
            "format": "png",
            "height": 576,
            "hidden_from_users": False,
            "id": 1,
            "intensities": dict,
            "locations": [],
            "media_type": "image",
            "mime_type": "image/png",
            "name": "1676547__safe_artist-colon-scraggleman_oc_oc-colon-"
                    "floor+bored_oc+only_bags+under+eyes_bust_earth+pony_"
                    "female_goggles_helmet_mare_meme_neet_neet+home+g.png",
            "orig_sha512_hash": "re:8b4c00d2[0-9a-f]{120}",
            "processed": True,
            "representations": dict,
            "score": int,
            "sha512_hash": "8b4c00d2eff52d51ad9647e14738944ab306fd1d8e1bf6"
                           "34fbb181b32f44070aa588938e26c4eb072b1eb61489aa"
                           "f3062fb644a76c79f936b97723a2c3e0e5d3",
            "size": 70910,
            "source_url": "",
            "tag_ids": list,
            "tags": list,
            "thumbnails_generated": True,
            "updated_at": "2022-05-13T00:43:19.791Z",
            "upvotes": int,
            "view_url": "https://cdn.twibooru.org/img/2020/7/8/1/full.png",
            "width": 576,
            "wilson_score": float,
        },
    })

    def __init__(self, match):
        TwibooruExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def posts(self):
        return (self.api.post(self.post_id),)


class TwibooruSearchExtractor(TwibooruExtractor):
    """Extractor for twibooru search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "{search_tags}")
    pattern = BASE_PATTERN + r"/(?:search/?\?([^#]+)|tags/([^/?#]+))"
    test = (
        ("https://twibooru.org/search?q=cute", {
            "range": "40-60",
            "count": 21,
        }),
        ("https://twibooru.org/tags/cute", {
            "range": "1-20",
            "count": 20,
        }),
    )

    def __init__(self, match):
        TwibooruExtractor.__init__(self, match)
        query, tag = match.groups()
        if tag:
            q = tag.replace("+", " ")
            for old, new in (
                ("-colon-"  , ":"),
                ("-dash-"   , "-"),
                ("-dot-"    , "."),
                ("-plus-"   , "+"),
                ("-fwslash-", "/"),
                ("-bwslash-", "\\"),
            ):
                if old in q:
                    q = q.replace(old, new)
            self.params = {"q": text.unquote(text.unquote(q))}
        else:
            self.params = text.parse_query(query)

    def metadata(self):
        return {"search_tags": self.params.get("q", "")}

    def posts(self):
        return self.api.search(self.params)


class TwibooruGalleryExtractor(TwibooruExtractor):
    """Extractor for twibooru galleries"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "galleries",
                     "{gallery[id]} {gallery[title]}")
    pattern = BASE_PATTERN + r"/galleries/(\d+)"
    test = ("https://twibooru.org/galleries/1", {
        "range": "1-20",
        "keyword": {
            "gallery": {
                "description": "Best nation pone and "
                               "russian related pics.",
                "id": 1,
                "spoiler_warning": "Russia",
                "thumbnail_id": 694923,
                "title": "Marussiaverse",
            },
        },
    })

    def __init__(self, match):
        TwibooruExtractor.__init__(self, match)
        self.gallery_id = match.group(1)

    def metadata(self):
        return {"gallery": self.api.gallery(self.gallery_id)}

    def posts(self):
        gallery_id = "gallery_id:" + self.gallery_id
        params = {"sd": "desc", "sf": gallery_id, "q" : gallery_id}
        return self.api.search(params)


class TwibooruAPI():
    """Interface for the Twibooru API

    https://twibooru.org/pages/api
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = "https://twibooru.org/api"

    def gallery(self, gallery_id):
        endpoint = "/v3/galleries/" + gallery_id
        return self._call(endpoint)["gallery"]

    def post(self, post_id):
        endpoint = "/v3/posts/" + post_id
        return self._call(endpoint)["post"]

    def search(self, params):
        endpoint = "/v3/search/posts"
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params=None):
        url = self.root + endpoint

        while True:
            response = self.extractor.request(url, params=params, fatal=None)

            if response.status_code < 400:
                return response.json()

            if response.status_code == 429:
                until = text.parse_datetime(
                    response.headers["X-RL-Reset"], "%Y-%m-%d %H:%M:%S %Z")
                # wait an extra minute, just to be safe
                self.extractor.wait(until=until, adjust=60.0)
                continue

            # error
            self.extractor.log.debug(response.content)
            raise exception.StopExtraction(
                "%s %s", response.status_code, response.reason)

    def _pagination(self, endpoint, params):
        extr = self.extractor

        api_key = extr.config("api-key")
        if api_key:
            params["key"] = api_key

        filter_id = extr.config("filter")
        if filter_id:
            params["filter_id"] = filter_id
        elif not api_key:
            params["filter_id"] = "2"

        params["page"] = 1
        params["per_page"] = per_page = extr.per_page

        while True:
            data = self._call(endpoint, params)
            yield from data["posts"]

            if len(data["posts"]) < per_page:
                return
            params["page"] += 1
