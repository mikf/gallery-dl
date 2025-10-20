# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://sizebooru.com/"""

from .booru import BooruExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?sizebooru\.com"


class SizebooruExtractor(BooruExtractor):
    """Base class for sizebooru extractors"""
    category = "sizebooru"
    root = "https://sizebooru.com"
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"
    page_start = 1
    request_interval = (0.5, 1.5)

    def _init(self):
        if self.config("metadata", False):
            self._prepare = self._prepare_metadata

    def _file_url(self, post):
        post["file_url"] = url = f"{self.root}/Picture/{post['id']}"
        return url

    def _prepare(self, post):
        post_id = post["id"]
        post["id"] = text.parse_int(post_id)
        post["filename"] = post_id
        if not post["extension"]:
            post["extension"] = "jpg"

    def _prepare_metadata(self, post):
        post_id = post["id"]
        url = f"{self.root}/Details/{post_id}"
        extr = text.extract_from(self.request(url).text)

        post.update({
            "id"       : text.parse_int(post_id),
            "date"     : self.parse_datetime(
                extr("<b>Posted Date:</b> ", "<"), "%m/%d/%Y"),
            "date_approved": self.parse_datetime(
                extr("<b>Approved Date:</b> ", "<"), "%m/%d/%Y"),
            "approver" : text.remove_html(extr("<b>Approved By:</b>", "</")),
            "uploader" : text.remove_html(extr("<b>Posted By:</b>", "</")),
            "artist"   : None
                if (artist := extr("<b>Artist:</b> ", "</")) == "N/A" else  # noqa: E131 E501
                text.remove_html(artist),  # noqa: E131
            "views"    : text.parse_int(extr("<b>Views:</b>", "<")),
            "source"   : text.extr(extr(
                "<b>Source Link:</b>", "</"), ' href="', '"') or None,
            "tags"     : text.split_html(extr(
                "<h6>Related Tags</h6>", "</ul>")),
            "favorite" : text.split_html(extr(
                "<h6>Favorited By</h6>", "</ul>")),
        })

        post["filename"], _, ext = extr('" alt="', '"').rpartition(".")
        if not post["extension"]:
            post["extension"] = ext.lower()

        return post

    def _pagination(self, url, callback=None):
        params = {
            "pageNo"  : self.page_start,
            "pageSize": self.per_page,
        }

        page = self.request(url, params=params).text
        if callback is not None:
            callback(page)

        while True:
            thumb = None
            for thumb in text.extract_iter(
                    page, '<a href="/Details/', ';base64'):
                yield {
                    "id"       : thumb[:thumb.find('"')],
                    "extension": thumb[thumb.rfind("/")+1:],
                }

            if "disabled" in text.extr(page, 'area-label="Next"', ">") or \
                    thumb is None:
                return
            params["pageNo"] += 1
            page = self.request(url, params=params).text


class SizebooruPostExtractor(SizebooruExtractor):
    """Extractor for sizebooru posts"""
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/Details/(\d+)"
    example = "https://sizebooru.com/Details/12345"

    def posts(self):
        return ({"id": self.groups[0], "extension": None},)


class SizebooruTagExtractor(SizebooruExtractor):
    """Extractor for sizebooru tag searches"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    pattern = rf"{BASE_PATTERN}/Search/([^/?#]+)"
    example = "https://sizebooru.com/Search/TAG"

    def posts(self):
        tag = self.groups[0]
        self.kwdict["search_tags"] = text.unquote(tag)
        return self._pagination(f"{self.root}/Search/{tag}")


class SizebooruGalleryExtractor(SizebooruExtractor):
    """Extractor for sizebooru galleries"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{gallery_name} ({gallery_id})")
    pattern = rf"{BASE_PATTERN}/Galleries/List/(\d+)"
    example = "https://sizebooru.com/Galleries/List/123"

    def posts(self):
        gid = self.groups[0]
        self.kwdict["gallery_id"] = text.parse_int(gid)
        return self._pagination(
            f"{self.root}/Galleries/List/{gid}", self._extract_name)

    def _extract_name(self, page):
        self.kwdict["gallery_name"] = text.unescape(text.extr(
            page, "<title>Gallery: ", " - Size Booru<"))


class SizebooruUserExtractor(SizebooruExtractor):
    """Extractor for a sizebooru user's uploads"""
    subcategory = "user"
    directory_fmt = ("{category}", "Uploads {user}")
    pattern = rf"{BASE_PATTERN}/Profile/Uploads/([^/?#]+)"
    example = "https://sizebooru.com/Profile/Uploads/USER"

    def posts(self):
        user = self.groups[0]
        self.kwdict["user"] = text.unquote(user)
        return self._pagination(f"{self.root}/Profile/Uploads/{user}",)


class SizebooruFavoriteExtractor(SizebooruExtractor):
    """Extractor for a sizebooru user's favorites"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "Favorites {user}")
    pattern = rf"{BASE_PATTERN}/Profile/Favorites/([^/?#]+)"
    example = "https://sizebooru.com/Profile/Favorites/USER"

    def posts(self):
        user = self.groups[0]
        self.kwdict["user"] = text.unquote(user)
        return self._pagination(f"{self.root}/Profile/Favorites/{user}",)
