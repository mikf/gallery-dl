# -*- coding: utf-8 -*-

# Copyright 2021-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Philomena sites"""

from .booru import BooruExtractor
from .. import text, exception


class PhilomenaExtractor(BooruExtractor):
    """Base class for philomena extractors"""
    basecategory = "philomena"
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{id}"
    request_interval = (0.5, 1.5)
    page_start = 1
    per_page = 50

    def _init(self):
        self.api = PhilomenaAPI(self)
        self.svg = self.config("svg", True)

    def _file_url(self, post):
        try:
            url = post["representations"]["full"]
        except Exception:
            url = post["view_url"]

        if self.svg and post["format"] == "svg":
            return url.rpartition(".")[0] + ".svg"
        return url

    def _prepare(self, post):
        post["date"] = self.parse_datetime_iso(post["created_at"][:19])


BASE_PATTERN = PhilomenaExtractor.update({
    "derpibooru": {
        "root": "https://derpibooru.org",
        "pattern": r"(?:www\.)?derpibooru\.org",
        "filter_id": "56027",
    },
    "ponybooru": {
        "root": "https://ponybooru.org",
        "pattern": r"(?:www\.)?ponybooru\.org",
        "filter_id": "3",
    },
    "furbooru": {
        "root": "https://furbooru.org",
        "pattern": r"furbooru\.org",
        "filter_id": "2",
    },
})


class PhilomenaPostExtractor(PhilomenaExtractor):
    """Extractor for single posts on a Philomena booru"""
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/(?:images/)?(\d+)"
    example = "https://derpibooru.org/images/12345"

    def posts(self):
        return (self.api.image(self.groups[-1]),)


class PhilomenaSearchExtractor(PhilomenaExtractor):
    """Extractor for Philomena search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "{search_tags}")
    pattern = rf"{BASE_PATTERN}/(?:search/?\?([^#]+)|tags/([^/?#]+))"
    example = "https://derpibooru.org/search?q=QUERY"

    def __init__(self, match):
        PhilomenaExtractor.__init__(self, match)

        if q := self.groups[-1]:
            q = q.replace("+", " ")
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
            self.params = text.parse_query(self.groups[-2])

    def metadata(self):
        return {"search_tags": self.params.get("q", "")}

    def posts(self):
        return self.api.search(self.params)


class PhilomenaGalleryExtractor(PhilomenaExtractor):
    """Extractor for Philomena galleries"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "galleries",
                     "{gallery[id]} {gallery[title]}")
    pattern = rf"{BASE_PATTERN}/galleries/(\d+)"
    example = "https://derpibooru.org/galleries/12345"

    def metadata(self):
        try:
            return {"gallery": self.api.gallery(self.groups[-1])}
        except IndexError:
            raise exception.NotFoundError("gallery")

    def posts(self):
        gallery_id = f"gallery_id:{self.groups[-1]}"
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
            raise exception.HttpError("", response)

    def _pagination(self, endpoint, params):
        extr = self.extractor

        if api_key := extr.config("api-key"):
            params["key"] = api_key

        if filter_id := extr.config("filter"):
            params["filter_id"] = filter_id
        elif not api_key:
            params["filter_id"] = extr.config_instance("filter_id") or "2"

        params["page"] = extr.page_start
        params["per_page"] = extr.per_page

        while True:
            data = self._call(endpoint, params)
            yield from data["images"]

            if len(data["images"]) < extr.per_page:
                return
            params["page"] += 1
