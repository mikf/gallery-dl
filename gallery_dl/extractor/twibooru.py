# -*- coding: utf-8 -*-

# Copyright 2022-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://twibooru.org/"""

from .booru import BooruExtractor
from .. import text, exception

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
        self.api = self.utils().TwibooruAPI(self)
        if not self.config("svg", True):
            import operator
            self._file_url = operator.itemgetter("view_url")

    def _file_url(self, post):
        if post["format"] == "svg":
            return f"{post['view_url'].rpartition('.')[0]}.svg"
        return post["view_url"]

    def _prepare(self, post):
        post["date"] = self.parse_datetime_iso(post["created_at"])

        if "name" in post:
            name, sep, rest = post["name"].rpartition(".")
            post["filename"] = name if sep else rest


class TwibooruPostExtractor(TwibooruExtractor):
    """Extractor for single twibooru posts"""
    subcategory = "post"
    request_interval = (0.5, 1.5)
    pattern = rf"{BASE_PATTERN}/(\d+)"
    example = "https://twibooru.org/12345"

    def posts(self):
        return (self.api.post(self.groups[0]),)


class TwibooruSearchExtractor(TwibooruExtractor):
    """Extractor for twibooru search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "{search_tags}")
    pattern = rf"{BASE_PATTERN}/(?:search/?\?([^#]+)|tags/([^/?#]+))"
    example = "https://twibooru.org/search?q=TAG"

    def posts(self):
        query, tag = self.groups
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
            params = {"q": text.unquote(text.unquote(q))}
        else:
            params = text.parse_query(query)

        self.kwdict["search_tags"] = params.get("q", "")
        return self.api.search(params)


class TwibooruGalleryExtractor(TwibooruExtractor):
    """Extractor for twibooru galleries"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "galleries",
                     "{gallery[id]} {gallery[title]}")
    pattern = rf"{BASE_PATTERN}/galleries/(\d+)"
    example = "https://twibooru.org/galleries/12345"

    def posts(self):
        gid = self.groups[0]

        try:
            self.kwdict["gallery"] = self.api.gallery(gid)
        except IndexError:
            raise exception.NotFoundError("gallery")

        gallery_id = f"gallery_id:{gid}"
        params = {"sd": "desc", "sf": gallery_id, "q": gallery_id}
        return self.api.search(params)
