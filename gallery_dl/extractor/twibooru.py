# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://twibooru.org/"""

from .booru import BooruExtractor
from .. import text, exception
import operator

BASE_PATTERN = r"(?:https?://)?(?:www\.)?twibooru\.org"


class TwibooruExtractor(BooruExtractor):
    """Base class for twibooru extractors"""
    category = "twibooru"
    basecategory = "philomena"
    root = "https://twibooru.org"
    filename_fmt = "{id}_{filename}.{extension}"
    archive_fmt = "{id}"
    request_interval = (6.0, 6.1)
    page_start = 1
    per_page = 50

    def _init(self):
        self.api = TwibooruAPI(self)
        if not self.config("svg", True):
            self._file_url = operator.itemgetter("view_url")

    def _file_url(self, post):
        if post["format"] == "svg":
            return post["view_url"].rpartition(".")[0] + ".svg"
        return post["view_url"]

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
    request_interval = (0.5, 1.5)
    pattern = BASE_PATTERN + r"/(\d+)"
    example = "https://twibooru.org/12345"

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
    example = "https://twibooru.org/search?q=TAG"

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
    example = "https://twibooru.org/galleries/12345"

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

        params["page"] = extr.page_start
        params["per_page"] = per_page = extr.per_page

        while True:
            data = self._call(endpoint, params)
            yield from data["posts"]

            if len(data["posts"]) < per_page:
                return
            params["page"] += 1
