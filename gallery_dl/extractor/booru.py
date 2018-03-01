# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Base classes for extractors for danbooru and co"""

from .common import SharedConfigExtractor, Message
from .. import text
from urllib.parse import urljoin
from xml.etree import ElementTree
import datetime
import operator


class BooruExtractor(SharedConfigExtractor):
    """Base class for all booru extractors"""
    basecategory = "booru"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    api_url = ""
    per_page = 50
    page_start = 1
    page_limit = None
    sort = False

    def __init__(self, match):
        super().__init__()
        self.params = {}

    def skip(self, num):
        pages = num // self.per_page
        if self.page_limit and pages + self.page_start > self.page_limit:
            pages = self.page_limit - self.page_start
        self.page_start += pages
        return pages * self.per_page

    def items(self):
        data = self.get_metadata()

        yield Message.Version, 1
        yield Message.Directory, data

        self.reset_page()
        while True:
            images = self.parse_response(
                self.request(self.api_url, params=self.params))

            for image in images:
                try:
                    url = image["file_url"]
                    if url.startswith("/"):
                        url = urljoin(self.api_url, url)
                    image.update(data)
                    yield Message.Url, url, text.nameext_from_url(url, image)
                except KeyError:
                    continue

            if len(images) < self.per_page:
                return
            self.update_page(data)

    def reset_page(self):
        """Initialize params to point to the first page"""
        self.params["page"] = self.page_start

    def update_page(self, data):
        """Update params to point to the next page"""

    def parse_response(self, response):
        """Parse JSON API response"""
        images = response.json()
        if self.sort:
            images.sort(key=operator.itemgetter("score", "id"),
                        reverse=True)
        return images

    def get_metadata(self):
        """Collect metadata for extractor-job"""
        return {}


class XmlParserMixin():
    """Mixin for XML based API responses"""
    def parse_response(self, response):
        root = ElementTree.fromstring(response.text)
        return [post.attrib for post in root]


class DanbooruPageMixin():
    """Pagination for Danbooru v2"""
    def update_page(self, data):
        self.params["page"] = "b{}".format(data["id"])


class MoebooruPageMixin():
    """Pagination for Moebooru and Danbooru v1"""
    def update_page(self, data):
        if self.page_limit:
            self.params["page"] = None
            self.params["before_id"] = data["id"]
        else:
            self.params["page"] += 1


class GelbooruPageMixin():
    """Pagination for Gelbooru-like sites"""
    def reset_page(self):
        self.params["pid"] = self.page_start - 1

    def update_page(self, data):
        self.params["pid"] += 1


class TagMixin():
    """Extraction of images based on search-tags"""
    subcategory = "tag"
    directory_fmt = ["{category}", "{search_tags}"]
    archive_fmt = "t_{search_tags}_{id}"

    def __init__(self, match):
        super().__init__(match)
        self.tags = text.unquote(match.group("tags").replace("+", " "))
        self.params["tags"] = self.tags
        self.params["limit"] = self.per_page

    def get_metadata(self):
        return {"search_tags": self.tags}


class PoolMixin():
    """Extraction of image-pools"""
    subcategory = "pool"
    directory_fmt = ["{category}", "pool", "{pool}"]
    archive_fmt = "p_{pool}_{id}"

    def __init__(self, match):
        super().__init__(match)
        self.pool = match.group("pool")
        self.params["tags"] = "pool:" + self.pool
        self.params["limit"] = self.per_page

    def get_metadata(self):
        return {"pool": self.pool}


class PostMixin():
    """Extraction of a single image-post"""
    subcategory = "post"
    archive_fmt = "{id}"

    def __init__(self, match):
        super().__init__(match)
        self.post = match.group("post")
        self.params["tags"] = "id:" + self.post


class PopularMixin():
    """Extraction and metadata handling for Danbooru v2"""
    subcategory = "popular"
    directory_fmt = ["{category}", "popular", "{scale}", "{date}"]
    archive_fmt = "P_{scale[0]}_{date}_{id}"
    page_start = None
    sort = True

    def __init__(self, match):
        super().__init__(match)
        self.params.update(text.parse_query(match.group("query")))

    def get_metadata(self, fmt="%Y-%m-%d"):
        date = self.get_date() or datetime.datetime.utcnow().strftime(fmt)
        scale = self.get_scale() or "day"

        if scale == "week":
            dt = datetime.datetime.strptime(date, fmt)
            dt -= datetime.timedelta(days=dt.weekday())
            date = dt.strftime(fmt)
        elif scale == "month":
            date = date[:-3]

        return {"date": date, "scale": scale}

    def get_scale(self):
        if "scale" in self.params:
            return self.params["scale"]
        return None

    def get_date(self):
        if "date" in self.params:
            return self.params["date"][:10]
        return None


class MoebooruPopularMixin(PopularMixin):
    """Extraction and metadata handling for Moebooru and Danbooru v1"""
    def __init__(self, match):
        super().__init__(match)
        self.scale = match.group("scale")

    def get_date(self):
        if "year" in self.params:
            return "{:>04}-{:>02}-{:>02}".format(
                self.params["year"],
                self.params.get("month", "01"),
                self.params.get("day", "01"))
        return None

    def get_scale(self):
        if self.scale and self.scale.startswith("by_"):
            return self.scale[3:]
        return self.scale
