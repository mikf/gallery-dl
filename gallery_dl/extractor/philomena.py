# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
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
    per_page = 50

    _file_url = operator.itemgetter("view_url")

    @staticmethod
    def _prepare(post):
        post["date"] = text.parse_datetime(post["created_at"])

    @staticmethod
    def _extended_tags(post):
        pass

    def _pagination(self, url, params):
        params["page"] = 1
        params["per_page"] = self.per_page

        api_key = self.config("api-key")
        if api_key:
            params["key"] = api_key

        filter_id = self.config("filter")
        if filter_id:
            params["filter_id"] = filter_id
        elif not api_key:
            try:
                params["filter_id"] = INSTANCES[self.category]["filter_id"]
            except (KeyError, TypeError):
                pass

        while True:
            data = self.request(url, params=params).json()
            yield from data["images"]

            if len(data["images"]) < self.per_page:
                return
            params["page"] += 1


INSTANCES = {
    "derpibooru": {"root": "https://derpibooru.org",
                   "filter_id": "56027"},
    "ponybooru" : {"root": "https://ponybooru.org",
                   "filter_id": "2"},
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
                "tag_count": 36,
                "tag_ids": list,
                "tags": list,
                "thumbnails_generated": True,
                "updated_at": "2020-05-28T13:14:07Z",
                "uploader": "Clover the Clever",
                "uploader_id": 211188,
                "upvotes": int,
                "view_url": str,
                "width": 900,
                "wilson_score": float,
            },
        }),
        ("https://derpibooru.org/1"),
        ("https://ponybooru.org/images/1", {
            "content": "bca26f58fafd791fe07adcd2a28efd7751824605",
        }),
    )

    def __init__(self, match):
        PhilomenaExtractor.__init__(self, match)
        self.image_id = match.group(match.lastindex)

    def posts(self):
        url = self.root + "/api/v1/json/images/" + self.image_id
        return (self.request(url).json()["image"],)


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
        ("https://ponybooru.org/search?q=cute", {
            "range": "40-60",
            "count": 21,
        }),
    )

    def __init__(self, match):
        PhilomenaExtractor.__init__(self, match)
        groups = match.groups()
        if groups[-1]:
            self.params = {"q": groups[-1]}
        else:
            self.params = text.parse_query(groups[-2])

    def metadata(self):
        return {"search_tags": self.params.get("q", "")}

    def posts(self):
        url = self.root + "/api/v1/json/search/images"
        return self._pagination(url, self.params)


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
    )

    def __init__(self, match):
        PhilomenaExtractor.__init__(self, match)
        self.gallery_id = match.group(match.lastindex)

    def metadata(self):
        url = self.root + "/api/v1/json/search/galleries"
        params = {"q": "id:" + self.gallery_id}
        galleries = self.request(url, params=params).json()["galleries"]
        if not galleries:
            raise exception.NotFoundError("gallery")
        return {"gallery": galleries[0]}

    def posts(self):
        gallery_id = "gallery_id:" + self.gallery_id
        url = self.root + "/api/v1/json/search/images"
        params = {"sd": "desc", "sf": gallery_id, "q" : gallery_id}
        return self._pagination(url, params)
