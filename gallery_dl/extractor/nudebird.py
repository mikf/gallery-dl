# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nudebird.biz/"""

from .. import exception, text, dt
from .common import Extractor, Message

BASE_PATTERN = r"(?:https?://)?(?:www\.)?nudebird\.biz"


class NudebirdExtractor(Extractor):
    """Base class for nudebird extractors"""
    category = "nudebird"
    root = "https://nudebird.biz"

    def items(self):
        data = {"_extractor": NudebirdPostExtractor}
        data.update(self.metadata(None, self.url))
        for post in self.posts(self.url):
            yield Message.Queue, post, data

    def metadata(self, page, url):
        raise NotImplementedError()

    def posts(self, page):
        return self._pagination(self.groups[0])

    def _pagination(self, path, params=None, page_num=1):
        while True:
            url = f"{self.root}{path.rstrip('/')}/page/{page_num}/"

            try:
                response = self.request(url, params=params)
            except exception.HttpError:
                return

            if response.status_code >= 300:
                return

            page = response.text
            if "featured-thumbnail" not in page:
                return

            posts = text.re(
                r"<a"
                r"(?=[^>]*\bid=['\"]featured-thumbnail['\"])"
                r"(?=[^>]*\bhref=['\"]([^'\"]+))"
                r"[^>]*>"
            ).findall(page)
            if not posts:
                return

            page_num += 1
            yield from posts


class NudebirdPostExtractor(NudebirdExtractor):
    """Extractor for individual posts on nudebird.biz"""
    subcategory = "post"
    directory_fmt = ("{category}", "{title}")
    archive_fmt = "{gallery_id}_{filename}"
    pattern = (
        BASE_PATTERN + r"/(?!"
        r"(?:category|tag|page)/"
        r"|most-popular-(?:weekly|monthly|yearly)(?:$|/)"
        r"|wp-(?:content|admin|json)/"
        r"|\?s=)([^/?#]+)/?"
    )
    example = "https://nudebird.biz/cosplayer-name-character-picture-size/"

    def __init__(self, match):
        NudebirdExtractor.__init__(self, match)
        self.post_slug = match[1]

    def items(self):
        url = f"{self.root}/{self.post_slug}/"
        page = self.request(url).text
        data = self.metadata(page, url)
        posts = self.posts(page)
        data["count"] = len(posts)

        yield Message.Directory, "", data
        for post in posts:
            yield Message.Url, post["url"], {**post, **data}

    def metadata(self, page, url):
        return {
            "gallery_id": self.post_slug,
            "post_slug": self.post_slug,
            "post_url": url,
            "title": text.unescape(
                text.extr(page, "<title>", "</title>").rsplit(" - ", 1)[0]
            ),
            "post_category": text.unescape(
                text.extr(
                    page, '<span class="thecategory">', "</span>"
                ).strip()
            ),
            "date_published": dt.parse(text.unescape(
                text.extr(page, '<span itemprop="datePublished">', "</span>")
            ), "%B %d, %Y"),
            "tags": [
                text.unescape(tag)
                for tag in text.extract_iter(
                    text.extr(
                        page, '<div class="tags border-bottom">', "</div>"
                    ),
                    ">",
                    "</a>",
                )
            ],
        }

    def posts(self, page):
        return sorted([
            {**text.nameext_from_url(url), "url": url}
            for url in {
                text.unquote(text.unescape(url))
                for url in text.re(r"<img[^>]*data-lazy-src=[\"']([^\"']+)")
                .findall(text.extr(page, "<p>", "</p>"))}],
            key=lambda p: (
                (num := text.parse_int(p["filename"]
                                       .partition("-")[0], None)) is None,
                num if num is not None else p["filename"]))


class NudebirdCategoryExtractor(NudebirdExtractor):
    """Extractor for nudebird categories"""
    subcategory = "category"
    pattern = BASE_PATTERN + r"(/category/[^/?#]+)(?:/page/\d+)?/?$"
    example = "https://nudebird.biz/category/cosplay/"

    def metadata(self, page, url):
        return {"category_slug": self.groups[0].strip("/").split("/")[1]}


class NudebirdTagExtractor(NudebirdExtractor):
    """Extractor for nudebird tags"""
    subcategory = "tag"
    pattern = BASE_PATTERN + r"(/tag/[^/?#]+)(?:/page/\d+)?/?$"
    example = "https://nudebird.biz/tag/cosplay-character/"

    def metadata(self, page, url):
        return {"tag_slug": self.groups[0].strip("/").split("/")[1]}


class NudebirdPopularExtractor(NudebirdExtractor):
    """Extractor for nudebird most-popular pages"""
    subcategory = "popular"
    pattern = (
        BASE_PATTERN + r"(/most-popular-(weekly|monthly|yearly))"
        r"(?:/page/\d+)?/?$"
    )
    example = "https://nudebird.biz/most-popular-weekly/"

    def metadata(self, page, url):
        return {"popularity_period": self.groups[1]}


class NudebirdSearchExtractor(NudebirdExtractor):
    """Extractor for nudebird search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/(?:page/\d+/)?\?s=([^&#]+)"
    example = "https://nudebird.biz/?s=cosplay-series"

    def metadata(self, page, url):
        return {"search_query": text.unquote(self.groups[0])}

    def posts(self, page):
        params = {"s": self.groups[0]}
        return self._pagination("/", params)
