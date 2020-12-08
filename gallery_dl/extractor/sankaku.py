# -*- coding: utf-8 -*-

# Copyright 2014-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://chan.sankakucomplex.com/"""

from .booru import BooruExtractor
from .. import text, exception
import collections

BASE_PATTERN = r"(?:https?://)?(?:beta|chan)\.sankakucomplex\.com"


class SankakuExtractor(BooruExtractor):
    """Base class for sankaku channel extractors"""
    basecategory = "booru"
    category = "sankaku"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    request_interval_min = 1.0
    per_page = 100

    TAG_TYPES = {
        0: "general",
        1: "artist",
        2: "studio",
        3: "copyright",
        4: "character",
        5: "genre",
        6: "",
        7: "",
        8: "medium",
        9: "meta",
    }

    def _prepare_post(self, post, extended_tags=False):
        url = post["file_url"]
        if url[0] == "/":
            url = self.root + url
        if extended_tags:
            self._fetch_extended_tags(post)
        post["date"] = text.parse_timestamp(post["created_at"]["s"])
        post["tags"] = [tag["name"] for tag in post["tags"]]
        return url

    def _fetch_extended_tags(self, post):
        tags = collections.defaultdict(list)
        types = self.TAG_TYPES
        for tag in post["tags"]:
            tags[types[tag["type"]]].append(tag["name"])
        for key, value in tags.items():
            post["tags_" + key] = value

    def _api_request(self, endpoint, params=None):
        url = "https://capi-v2.sankakucomplex.com" + endpoint
        while True:
            response = self.request(url, params=params, fatal=False)
            if response.status_code == 429:
                self.wait(until=response.headers.get("X-RateLimit-Reset"))
                continue
            return response.json()

    def _pagination(self, params):
        params["lang"] = "en"
        params["limit"] = str(self.per_page)

        while True:
            data = self._api_request("/posts/keyset", params)
            if not data.get("success", True):
                raise exception.StopExtraction(data.get("code"))
            yield from data["data"]

            params["next"] = data["meta"]["next"]
            if not params["next"]:
                return
            if "page" in params:
                del params["page"]


class SankakuTagExtractor(SankakuExtractor):
    """Extractor for images from chan.sankakucomplex.com by search-tags"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/\?([^#]*)"
    test = (
        ("https://beta.sankakucomplex.com/?tags=bonocho", {
            "count": 5,
            "pattern": r"https://c?s\.sankakucomplex\.com/data/[^/]{2}/[^/]{2}"
                       r"/[^/]{32}\.\w+\?e=\d+&m=[^&#]+",
        }),
        # error on five or more tags
        ("https://chan.sankakucomplex.com/?tags=bonocho+a+b+c+d", {
            "options": (("username", None),),
            "exception": exception.StopExtraction,
        }),
        # match arbitrary query parameters
        ("https://chan.sankakucomplex.com"
         "/?tags=marie_rose&page=98&next=3874906&commit=Search"),
    )

    def __init__(self, match):
        SankakuExtractor.__init__(self, match)
        query = text.parse_query(match.group(1))
        self.tags = text.unquote(query.get("tags", "").replace("+", " "))

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        return self._pagination({"tags": self.tags})


class SankakuPoolExtractor(SankakuExtractor):
    """Extractor for image pools or books from chan.sankakucomplex.com"""
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool[id]} {pool[name_en]}")
    archive_fmt = "p_{pool}_{id}"
    pattern = BASE_PATTERN + r"/(?:books|pool/show)/(\d+)"
    test = (
        ("https://beta.sankakucomplex.com/books/90", {
            "count": 5,
        }),
        ("https://chan.sankakucomplex.com/pool/show/90"),
    )

    def __init__(self, match):
        SankakuExtractor.__init__(self, match)
        self.pool_id = match.group(1)

    def metadata(self):
        pool = self._api_request("/pools/" + self.pool_id)
        self._posts = pool.pop("posts")
        return {"pool": pool}

    def posts(self):
        return self._posts


class SankakuPostExtractor(SankakuExtractor):
    """Extractor for single images from chan.sankakucomplex.com"""
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/post/show/(\d+)"
    test = (
        ("https://beta.sankakucomplex.com/post/show/360451", {
            "content": "5e255713cbf0a8e0801dc423563c34d896bb9229",
            "options": (("tags", True),),
            "keyword": {
                "tags_artist": ["bonocho"],
                "tags_studio": ["dc_comics"],
                "tags_medium": ["sketch", "copyright_name"],
                "tags_copyright": list,
                "tags_character": list,
                "tags_general"  : list,
            },
        }),
        ("https://chan.sankakucomplex.com/post/show/360451"),
    )

    def __init__(self, match):
        SankakuExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def posts(self):
        return self._pagination({"tags": "id:" + self.post_id})
