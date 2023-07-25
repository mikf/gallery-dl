# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Philomena sites"""

from .booru import BooruExtractor
from .. import text, exception
import operator


class PhilomenaExtractor(BooruExtractor):
    """Base class for philomena extractors"""
    basecategory = "philomena"
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{id}"
    request_interval = 1.0
    page_start = 1
    per_page = 50

    def _init(self):
        self.api = PhilomenaAPI(self)

    _file_url = operator.itemgetter("view_url")

    @staticmethod
    def _prepare(post):
        post["date"] = text.parse_datetime(post["created_at"])


INSTANCES = {
    "derpibooru": {
        "root": "https://derpibooru.org",
        "pattern": r"(?:www\.)?derpibooru\.org",
        "filter_id": "56027",
    },
    "ponybooru": {
        "root": "https://ponybooru.org",
        "pattern": r"(?:www\.)?ponybooru\.org",
        "filter_id": "2",
    },
    "furbooru": {
        "root": "https://furbooru.org",
        "pattern": r"furbooru\.org",
        "filter_id": "2",
    },
}

BASE_PATTERN = PhilomenaExtractor.update(INSTANCES)


class PhilomenaPostExtractor(PhilomenaExtractor):
    """Extractor for single posts on a Philomena booru"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/(?:images/)?(\d+)"
    test = (
        ("https://derpibooru.org/images/1", {
            "content": "88449eeb0c4fa5d3583d0b794f6bc1d70bf7f889",
            "count": 1,
            "keyword": {
                "animated": False,
                "aspect_ratio": 1.0,
                "comment_count": int,
                "created_at": "2012-01-02T03:12:33Z",
                "date": "dt:2012-01-02 03:12:33",
                "deletion_reason": None,
                "description": "",
                "downvotes": int,
                "duplicate_of": None,
                "duration": 0.04,
                "extension": "png",
                "faves": int,
                "first_seen_at": "2012-01-02T03:12:33Z",
                "format": "png",
                "height": 900,
                "hidden_from_users": False,
                "id": 1,
                "mime_type": "image/png",
                "name": "1__safe_fluttershy_solo_cloud_happy_flying_upvotes+ga"
                        "lore_artist-colon-speccysy_get_sunshine",
                "orig_sha512_hash": None,
                "processed": True,
                "representations": dict,
                "score": int,
                "sha512_hash": "f16c98e2848c2f1bfff3985e8f1a54375cc49f78125391"
                               "aeb80534ce011ead14e3e452a5c4bc98a66f56bdfcd07e"
                               "f7800663b994f3f343c572da5ecc22a9660f",
                "size": 860914,
                "source_url": "https://www.deviantart.com/speccysy/art"
                              "/Afternoon-Flight-215193985",
                "spoilered": False,
                "tag_count": int,
                "tag_ids": list,
                "tags": list,
                "thumbnails_generated": True,
                "updated_at": r"re:\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ",
                "uploader": "Clover the Clever",
                "uploader_id": 211188,
                "upvotes": int,
                "view_url": str,
                "width": 900,
                "wilson_score": float,
            },
        }),
        ("https://derpibooru.org/1"),
        ("https://www.derpibooru.org/1"),
        ("https://www.derpibooru.org/images/1"),

        ("https://ponybooru.org/images/1", {
            "content": "bca26f58fafd791fe07adcd2a28efd7751824605",
        }),
        ("https://www.ponybooru.org/images/1"),

        ("https://furbooru.org/images/1", {
            "content": "9eaa1e1b32fa0f16520912257dbefaff238d5fd2",
        }),
    )

    def __init__(self, match):
        PhilomenaExtractor.__init__(self, match)
        self.image_id = match.group(match.lastindex)

    def posts(self):
        return (self.api.image(self.image_id),)


class PhilomenaSearchExtractor(PhilomenaExtractor):
    """Extractor for Philomena search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "{search_tags}")
    pattern = BASE_PATTERN + r"/(?:search/?\?([^#]+)|tags/([^/?#]+))"
    test = (
        ("https://derpibooru.org/search?q=cute", {
            "range": "40-60",
            "count": 21,
        }),
        ("https://derpibooru.org/tags/cute", {
            "range": "40-60",
            "count": 21,
        }),
        (("https://derpibooru.org/tags/"
          "artist-colon--dash-_-fwslash--fwslash-%255Bkorroki%255D_aternak"), {
            "count": ">= 2",
        }),
        ("https://ponybooru.org/search?q=cute", {
            "range": "40-60",
            "count": 21,
        }),
        ("https://furbooru.org/search?q=cute", {
            "range": "40-60",
            "count": 21,
        }),
    )

    def __init__(self, match):
        PhilomenaExtractor.__init__(self, match)
        groups = match.groups()
        if groups[-1]:
            q = groups[-1].replace("+", " ")
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
            self.params = text.parse_query(groups[-2])

    def metadata(self):
        return {"search_tags": self.params.get("q", "")}

    def posts(self):
        return self.api.search(self.params)


class PhilomenaGalleryExtractor(PhilomenaExtractor):
    """Extractor for Philomena galleries"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "galleries",
                     "{gallery[id]} {gallery[title]}")
    pattern = BASE_PATTERN + r"/galleries/(\d+)"
    test = (
        ("https://derpibooru.org/galleries/1", {
            "pattern": r"https://derpicdn\.net/img/view/\d+/\d+/\d+/\d+[^/]+$",
            "keyword": {
                "gallery": {
                    "description": "Indexes start at 1 :P",
                    "id": 1,
                    "spoiler_warning": "",
                    "thumbnail_id": 1,
                    "title": "The Very First Gallery",
                    "user": "DeliciousBlackInk",
                    "user_id": 365446,
                },
            },
        }),
        ("https://ponybooru.org/galleries/27", {
            "count": ">= 24",
        }),
        ("https://furbooru.org/galleries/27", {
            "count": ">= 13",
        }),
    )

    def __init__(self, match):
        PhilomenaExtractor.__init__(self, match)
        self.gallery_id = match.group(match.lastindex)

    def metadata(self):
        try:
            return {"gallery": self.api.gallery(self.gallery_id)}
        except IndexError:
            raise exception.NotFoundError("gallery")

    def posts(self):
        gallery_id = "gallery_id:" + self.gallery_id
        params = {"sd": "desc", "sf": gallery_id, "q": gallery_id}
        return self.api.search(params)


class PhilomenaAPI():
    """Interface for the Philomena API

    https://www.derpibooru.org/pages/api
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = extractor.root + "/api"

    def gallery(self, gallery_id):
        endpoint = "/v1/json/search/galleries"
        params = {"q": "id:" + gallery_id}
        return self._call(endpoint, params)["galleries"][0]

    def image(self, image_id):
        endpoint = "/v1/json/images/" + image_id
        return self._call(endpoint)["image"]

    def search(self, params):
        endpoint = "/v1/json/search/images"
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params=None):
        url = self.root + endpoint

        while True:
            response = self.extractor.request(url, params=params, fatal=None)

            if response.status_code < 400:
                return response.json()

            if response.status_code == 429:
                self.extractor.wait(seconds=600)
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
            try:
                params["filter_id"] = INSTANCES[extr.category]["filter_id"]
            except (KeyError, TypeError):
                params["filter_id"] = "2"

        params["page"] = extr.page_start
        params["per_page"] = extr.per_page

        while True:
            data = self._call(endpoint, params)
            yield from data["images"]

            if len(data["images"]) < extr.per_page:
                return
            params["page"] += 1
