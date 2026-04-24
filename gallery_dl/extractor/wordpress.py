# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for WordPress sites via the WP REST API"""

from .common import Extractor, Message
from .generic import GenericExtractor
from .. import text


class WordpressExtractor(Extractor):
    """Base class for WordPress extractors"""
    category = "wordpress"
    directory_fmt = ("{category}", "{domain}", "{post_slug}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{post_id}_{filename}"
    page_start = 1
    per_page = 100

    def __init__(self, match):
        Extractor.__init__(self, match)

        url = match[0].partition(":")[2]
        url = text.ensure_http_scheme(url)
        self.root = text.root_from_url(url)
        self.domain = match.group(1)

    def _init(self):
        self.per_page = min(self.config("per-page", 100), 100)

    def _api_url(self, endpoint):
        if self.api_rest_route:
            return "{}?rest_route=/wp/v2/{}".format(self.root, endpoint)
        return "{}/wp-json/wp/v2/{}".format(self.root, endpoint)

    def _api_check(self):
        self.api_rest_route = False
        for url, rest_route in (
            (self.root + "/wp-json/", False),
            (self.root + "/?rest_route=/", True),
        ):
            response = self.request(url, fatal=False)
            try:
                data = response.json()
            except Exception:
                data = None
            if isinstance(data, dict) and "name" in data:
                self.api_rest_route = rest_route
                return data
        self.log.error(
            "WordPress REST API not available at '%s'", self.root)
        return None

    def _pagination(self, endpoint, params=None):
        if params is None:
            params = {}
        params["per_page"] = self.per_page
        params["page"] = self.page_start
        url = self._api_url(endpoint)

        while True:
            items = self.request_json(url, params=params)
            if not items or isinstance(items, dict):
                return
            yield from items
            if len(items) < self.per_page:
                return
            params["page"] += 1

    def _featured_media_url(self, media_id):
        if not media_id:
            return None
        media = self.request_json(
            self._api_url("media/{}".format(media_id)), fatal=False)
        if isinstance(media, dict):
            return media.get("source_url")
        return None

    def _images_from_html(self, html, post_url):
        self.url = post_url
        self.scheme = self.root.partition("://")[0] + "://"
        return [url for url, _ in GenericExtractor.images(self, html)]

    def skip_files(self, num):
        pages = num // self.per_page
        self.page_start += pages
        return pages * self.per_page


class WordpressPostsExtractor(WordpressExtractor):
    """Extractor for media from all posts of a WordPress site"""
    subcategory = "posts"
    pattern = r"(?:wp|wordpress):(?:https?://)?([^/?#]+)/?$"
    example = "wp:https://example.com"

    def items(self):
        site = self._api_check()
        if not site:
            return

        for post in self._pagination("posts", {
            "_fields": "id,date,slug,link,title,content,featured_media,author",
        }):
            post_url = post.get("link", self.root)
            html = post.get("content", {}).get("rendered", "")
            if not html:
                response = self.request(post_url, fatal=False)
                html = response.text if response else ""
            urls = self._images_from_html(html, post_url)

            featured_url = self._featured_media_url(post.get("featured_media"))
            if featured_url and featured_url not in urls:
                urls.insert(0, featured_url)

            if not urls:
                continue

            data = {
                "domain"      : self.domain,
                "site_name"   : site.get("name", ""),
                "post_id"     : post["id"],
                "post_title"  : text.remove_html(
                    post.get("title", {}).get("rendered", "")),
                "post_date"   : self.parse_datetime_iso(
                    post.get("date") or ""),
                "post_slug"   : post.get("slug", ""),
                "post_author" : post.get("author"),
                "post_url"    : post_url,
                "count"       : len(urls),
            }

            yield Message.Directory, "", data

            for data["num"], url in enumerate(urls, 1):
                text.nameext_from_url(url, data)
                yield Message.Url, url, data
