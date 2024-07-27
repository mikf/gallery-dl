# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://agn.ph/"""

from . import booru
from .. import text

from xml.etree import ElementTree

BASE_PATTERN = r"(?:https?://)?agn\.ph"


class AgnphExtractor(booru.BooruExtractor):
    category = "agnph"
    root = "https://agn.ph"
    page_start = 1
    per_page = 45

    def _prepare(self, post):
        post["date"] = text.parse_timestamp(post["created_at"])
        post["status"] = post["status"].strip()
        post["has_children"] = ("true" in post["has_children"])

    def _xml_to_dict(self, xml):
        return {element.tag: element.text for element in xml}

    def _pagination(self, url, params):
        params["api"] = "xml"
        if "page" in params:
            params["page"] = \
                self.page_start + text.parse_int(params["page"]) - 1
        else:
            params["page"] = self.page_start

        while True:
            data = self.request(url, params=params).text
            root = ElementTree.fromstring(data)

            yield from map(self._xml_to_dict, root)

            attrib = root.attrib
            if int(attrib["offset"]) + len(root) >= int(attrib["count"]):
                return

            params["page"] += 1


class AgnphTagExtractor(AgnphExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/gallery/post/(?:\?([^#]+))?$"
    example = "https://agn.ph/gallery/post/?search=TAG"

    def __init__(self, match):
        AgnphExtractor.__init__(self, match)
        self.params = text.parse_query(self.groups[0])

    def metadata(self):
        return {"search_tags": self.params.get("search") or ""}

    def posts(self):
        url = self.root + "/gallery/post/"
        return self._pagination(url, self.params.copy())


class AgnphPostExtractor(AgnphExtractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/gallery/post/show/(\d+)"
    example = "https://agn.ph/gallery/post/show/12345/"

    def posts(self):
        url = "{}/gallery/post/show/{}/?api=xml".format(
            self.root, self.groups[0])
        post = ElementTree.fromstring(self.request(url).text)
        return (self._xml_to_dict(post),)
