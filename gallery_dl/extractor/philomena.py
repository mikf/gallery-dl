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
        self.api = self.utilsb().PhilomenaAPI(self)
        self.svg = self.config("svg", True)

    def _file_url(self, post):
        try:
            url = post["representations"]["full"]
        except Exception:
            url = post["view_url"]

        if self.svg and post["format"] == "svg":
            return f"{url.rpartition('.')[0]}.svg"
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

    def posts(self):
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
            params = {"q": text.unquote(text.unquote(q))}
        else:
            params = text.parse_query(self.groups[-2])

        self.kwdict["search_tags"] = params.get("q", "")
        return self.api.search(params)


class PhilomenaGalleryExtractor(PhilomenaExtractor):
    """Extractor for Philomena galleries"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "galleries",
                     "{gallery[id]} {gallery[title]}")
    pattern = rf"{BASE_PATTERN}/galleries/(\d+)"
    example = "https://derpibooru.org/galleries/12345"

    def posts(self):
        gid = self.groups[-1]

        try:
            self.kwdict["gallery"] = self.api.gallery(gid)
        except IndexError:
            raise exception.NotFoundError("gallery")

        gallery_id = f"gallery_id:{gid}"
        params = {"sd": "desc", "sf": gallery_id, "q": gallery_id}
        return self.api.search(params)
