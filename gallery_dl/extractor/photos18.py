# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://photos18.com"""

from .common import Extractor, Message
from .. import text


BASE_PATTERN = r"(?:https?://)(?:www\.)?photos18\.com"
SORTING_METHODS = "(created|hits|views|score|likes)"


class Photos18Extractor(Extractor):
    """Base class for Photos18 extractors"""
    category = "photos18"
    directory_fmt = ("{category}", "{category_name}")
    filename_fmt = "{category}_{title}_{num:>02}.{extension}"
    archive_fmt = "{filename}"
    root = "https://www.photos18.com"


class Photos18AlbumExtractor(Photos18Extractor):
    """Extractor for a single album URL"""
    subcategory = "album"
    pattern = BASE_PATTERN + r"/v/(\w+)"
    example = "https://www.photos18.com/v/ID"

    def __init__(self, match):
        Photos18Extractor.__init__(self, match)
        self.post_id = match.group(1)

    def items(self):
        url = self.root + "/v/" + self.post_id
        page = self.request(url).text
        extr = text.extract_from(page)

        category_id = int(extr(
            '<li class="breadcrumb-item"><a href="/cat/', '"'))
        category_name = text.unescape(extr('>', '<'))
        date = text.parse_datetime(extr('"datePublished":"', '"'))
        title = text.unescape(extr(
            '<h1 class="title py-1">', '</h1>')).strip()

        urls = []
        while True:
            url = text.unescape(extr(
                '<div class="my-2 imgHolder"><a href="', '"'))
            if not url:
                break

            urls.append(url)

        data = {
            "post_id": self.post_id,
            "title": title,
            "category_id": category_id,
            "category_name": category_name,
            "date": date,
            "count": len(urls),
            "_http_headers": {"Referer": self.root},
        }
        yield Message.Directory, data
        for data["num"], url in enumerate(urls, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)


class Photos18ListExtractor(Photos18Extractor):
    """Extractor for a list of posts"""
    subcategory = "list"
    pattern = (BASE_PATTERN + r"(?:/|/cat/(\d+)(?:/" + SORTING_METHODS +
               r")?|/sort/" + SORTING_METHODS + r"|/q/([^/?#]+))?"
               r"(?:\?([^#]*))?(?:#.*)?$")
    example = "https://www.photos18.com/cat/1"

    def __init__(self, match):
        Photos18Extractor.__init__(self, match)
        query = text.parse_query(match.group(5))
        self.q = text.unquote(match.group(4) or "") or query.get("q")
        self.category_id = match.group(1) or query.get("category_id")
        self.sort = match.group(2) or match.group(3) or query.get("sort")
        self.page = int(query.get("page") or 1)

    def items(self):
        query = {}
        if self.q:
            query["q"] = self.q
        if self.category_id:
            query["category_id"] = self.category_id
        if self.sort:
            query["sort"] = self.sort
        if self.page:
            query["page"] = self.page

        while True:
            has_post = False
            page = self.request(self.root, params=query).text

            for i in text.extract_iter(
                    page, '<a class="visited" href="/v/', '"'):
                has_post = True
                url = self.root + "/v/" + i
                data = {"_extractor": Photos18AlbumExtractor}
                yield Message.Queue, url, data

            if not has_post or '<li class="page-item next">' not in page:
                break
            query["page"] += 1
