# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Base classes for extractors for danbooru and co"""

from .common import SharedConfigExtractor, Message
from .. import text
import xml.etree.ElementTree as ET
import urllib.parse
import datetime
import operator


class BooruExtractor(SharedConfigExtractor):
    """Base class for all booru extractors"""
    basecategory = "booru"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    headers = {}
    pagestart = 1
    pagekey = "page"
    api_url = ""

    def __init__(self):
        SharedConfigExtractor.__init__(self)
        self.session.headers.update(self.headers)
        self.params = {"limit": 50}
        self.setup()

    def items(self):
        yield Message.Version, 1
        yield Message.Directory, self.get_job_metadata()
        for data in self.items_impl():
            try:
                url = self.get_file_url(data)
                data = self.get_file_metadata(data)
                yield Message.Url, url, data
            except KeyError:
                continue

    def skip(self, num):
        limit = self.params["limit"]
        pages = num // limit
        self.pagestart += pages
        return pages * limit

    def items_impl(self):
        pass

    def setup(self):
        pass

    def update_page(self, reset=False):
        """Update the value of the 'page' parameter"""
        # Override this method in derived classes if necessary.
        # It is usually enough to just adjust the 'page' attribute
        if reset is False:
            self.params[self.pagekey] += 1
        else:
            self.params[self.pagekey] = self.pagestart

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        # Override this method in derived classes
        return {}

    def get_file_metadata(self, data):
        """Collect metadata for a downloadable file"""
        return text.nameext_from_url(self.get_file_url(data), data)

    def get_file_url(self, data):
        """Extract download-url from 'data'"""
        url = data["file_url"]
        if url.startswith("/"):
            url = urllib.parse.urljoin(self.api_url, url)
        return url


class JSONBooruExtractor(BooruExtractor):
    """Base class for JSON based API responses"""
    sort = False

    def items_impl(self):
        self.update_page(reset=True)
        while True:
            images = self.request(self.api_url, params=self.params).json()
            if self.sort:
                images.sort(key=operator.itemgetter("score", "id"),
                            reverse=True)
            yield from images
            if len(images) < self.params["limit"]:
                return
            self.update_page()


class XMLBooruExtractor(BooruExtractor):
    """Base class for XML based API responses"""
    def items_impl(self):
        self.update_page(reset=True)
        while True:
            root = ET.fromstring(
                self.request(self.api_url, params=self.params).text
            )
            for item in root:
                yield item.attrib
            if len(root) < self.params["limit"]:
                return
            self.update_page()


class BooruTagExtractor(BooruExtractor):
    """Extractor for images based on search-tags"""
    subcategory = "tag"
    directory_fmt = ["{category}", "{tags}"]

    def __init__(self, match):
        BooruExtractor.__init__(self)
        self.tags = text.unquote(match.group(1).replace("+", " "))
        self.params["tags"] = self.tags

    def get_job_metadata(self):
        return {"tags": self.tags}


class BooruPoolExtractor(BooruExtractor):
    """Extractor for image-pools"""
    subcategory = "pool"
    directory_fmt = ["{category}", "pool", "{pool}"]

    def __init__(self, match):
        BooruExtractor.__init__(self)
        self.pool = match.group(1)
        self.params["tags"] = "pool:" + self.pool

    def get_job_metadata(self):
        return {"pool": self.pool}


class BooruPostExtractor(BooruExtractor):
    """Extractor for single images"""
    subcategory = "post"

    def __init__(self, match):
        BooruExtractor.__init__(self)
        self.post = match.group(1)
        self.params["tags"] = "id:" + self.post


class BooruPopularExtractor(BooruExtractor):
    """Extractor for popular images"""
    subcategory = "popular"
    directory_fmt = ["{category}", "popular", "{scale}", "{date}"]

    def __init__(self, match):
        BooruExtractor.__init__(self)
        self.sort = True
        self.scale = match.group(1)
        self.params.update(text.parse_query(match.group(2)))

    def get_job_metadata(self, fmt="%Y-%m-%d"):
        if "scale" in self.params:
            scale = self.params["scale"]
        elif self.scale:
            scale = self.scale
            if scale.startswith("by_"):
                scale = scale[3:]
        else:
            scale = "day"

        if "date" in self.params:
            date = self.params["date"][:10]
        elif "year" in self.params:
            date = "{:>04}-{:>02}-{:>02}".format(
                self.params["year"],
                self.params.get("month", "01"),
                self.params.get("day", "01"))
        else:
            date = datetime.datetime.utcnow().strftime(fmt)

        if scale == "week":
            dt = datetime.datetime.strptime(date, fmt)
            dt -= datetime.timedelta(days=dt.weekday())
            date = dt.strftime(fmt)
        elif scale == "month":
            date = date[:-3]

        return {"date": date, "scale": scale}
