# -*- coding: utf-8 -*-

# Copyright 2018-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://rule34.paheal.net/"""

from .common import Extractor, Message
from .. import text


class PahealExtractor(Extractor):
    """Base class for paheal extractors"""
    basecategory = "shimmie2"
    category = "paheal"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    archive_fmt = "{id}"
    root = "https://rule34.paheal.net"

    def items(self):
        self.cookies.set(
            "ui-tnc-agreed", "true", domain="rule34.paheal.net")
        data = self.get_metadata()

        for post in self.get_posts():
            post["id"] = text.parse_int(post["id"])
            post["tags"] = text.unquote(post["tags"])
            post["width"] = text.parse_int(post["width"])
            post["height"] = text.parse_int(post["height"])
            post.update(data)
            yield Message.Directory, post
            yield Message.Url, post["file_url"], post

    def get_metadata(self):
        """Return general metadata"""
        return {}

    def get_posts(self):
        """Return an iterable containing data of all relevant posts"""

    def _extract_post(self, post_id):
        url = "{}/post/view/{}".format(self.root, post_id)
        extr = text.extract_from(self.request(url).text)

        post = {
            "id"      : post_id,
            "tags"    : extr(": ", "<"),
            "md5"     : extr("/_thumbs/", "/"),
            "file_url": (extr("id='main_image' src='", "'") or
                         extr("<source src='", "'")),
            "uploader": text.unquote(extr(
                "class='username' href='/user/", "'")),
            "date"    : text.parse_datetime(
                extr("datetime='", "'"), "%Y-%m-%dT%H:%M:%S%z"),
            "source"  : text.unescape(text.extr(
                extr(">Source Link<", "</td>"), "href='", "'")),
        }

        dimensions, size, ext = extr("Info</th><td>", "<").split(" // ")
        post["size"] = text.parse_bytes(size[:-1])
        post["width"], _, height = dimensions.partition("x")
        post["height"], _, duration = height.partition(", ")
        post["duration"] = text.parse_float(duration[:-1])
        post["filename"] = "{} - {}".format(post_id, post["tags"])
        post["extension"] = ext

        return post


class PahealTagExtractor(PahealExtractor):
    """Extractor for images from rule34.paheal.net by search-tags"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    pattern = (r"(?:https?://)?(?:rule34|rule63|cosplay)\.paheal\.net"
               r"/post/list/([^/?#]+)")
    example = "https://rule34.paheal.net/post/list/TAG/1"
    page_start = 1
    per_page = 70

    def __init__(self, match):
        PahealExtractor.__init__(self, match)
        self.tags = text.unquote(match.group(1))

    def _init(self):
        if self.config("metadata"):
            self._extract_data = self._extract_data_ex

    def skip(self, num):
        pages = num // self.per_page
        self.page_start += pages
        return pages * self.per_page

    def get_metadata(self):
        return {"search_tags": self.tags}

    def get_posts(self):
        pnum = self.page_start
        while True:
            url = "{}/post/list/{}/{}".format(self.root, self.tags, pnum)
            page = self.request(url).text

            pos = page.find("id='image-list'")
            for post in text.extract_iter(
                    page, "<img id='thumb_", "Only</a>", pos):
                yield self._extract_data(post)

            if ">Next<" not in page:
                return
            pnum += 1

    @staticmethod
    def _extract_data(post):
        pid , pos = text.extract(post, "", "'")
        data, pos = text.extract(post, "title='", "'", pos)
        md5 , pos = text.extract(post, "/_thumbs/", "/", pos)
        url , pos = text.extract(post, "<a href='", "'", pos)

        tags, data, date = data.split("\n")
        dimensions, size, ext = data.split(" // ")
        width, _, height = dimensions.partition("x")
        height, _, duration = height.partition(", ")

        return {
            "id"       : pid,
            "md5"      : md5,
            "file_url" : url,
            "width"    : width,
            "height"   : height,
            "duration" : text.parse_float(duration[:-1]),
            "tags"     : text.unescape(tags),
            "size"     : text.parse_bytes(size[:-1]),
            "date"     : text.parse_datetime(date, "%B %d, %Y; %H:%M"),
            "filename" : "{} - {}".format(pid, tags),
            "extension": ext,
        }

    def _extract_data_ex(self, post):
        pid = post[:post.index("'")]
        return self._extract_post(pid)


class PahealPostExtractor(PahealExtractor):
    """Extractor for single images from rule34.paheal.net"""
    subcategory = "post"
    pattern = (r"(?:https?://)?(?:rule34|rule63|cosplay)\.paheal\.net"
               r"/post/view/(\d+)")
    example = "https://rule34.paheal.net/post/view/12345"

    def __init__(self, match):
        PahealExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def get_posts(self):
        return (self._extract_post(self.post_id),)
