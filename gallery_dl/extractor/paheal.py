# -*- coding: utf-8 -*-

# Copyright 2018-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://rule34.paheal.net/"""

from .common import Extractor, Message
from .. import text, exception


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
            yield Message.Directory, "", post
            yield Message.Url, post["file_url"], post

    def get_metadata(self):
        """Return general metadata"""
        return {}

    def get_posts(self):
        """Return an iterable containing data of all relevant posts"""

    def _extract_post(self, post_id):
        url = f"{self.root}/post/view/{post_id}"
        extr = text.extract_from(self.request(url).text)

        post = {
            "id"      : post_id,
            "tags"    : extr(": ", "<"),
            "md5"     : extr("/_thumbs/", "/"),
            "file_url": (extr("id='main_image' src='", "'") or
                         extr("<source src='", "'")),
            "uploader": text.unquote(extr(
                "class='username' href='/user/", "'")),
            "date"    : self.parse_datetime_iso(extr("datetime='", "'")),
            "source"  : text.unescape(text.extr(
                extr(">Source Link<", "</td>"), "href='", "'")),
        }

        dimensions, size, ext = extr("Info</th><td>", "<").split(" // ")
        post["size"] = text.parse_bytes(size[:-1])
        post["width"], _, height = dimensions.partition("x")
        post["height"], _, duration = height.partition(", ")
        post["duration"] = text.parse_float(duration[:-1])
        post["filename"] = f"{post_id} - {post['tags']}"
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

    def _init(self):
        if self.config("metadata"):
            self._extract_data = self._extract_data_ex

    def skip(self, num):
        pages = num // self.per_page
        self.page_start += pages
        return pages * self.per_page

    def get_metadata(self):
        return {"search_tags": text.unquote(self.groups[0])}

    def get_posts(self):
        pnum = self.page_start
        base = f"{self.root}/post/list/{self.groups[0]}/"

        while True:
            try:
                page = self.request(f"{base}{pnum}").text
            except exception.HttpError as exc:
                if exc.status == 404:
                    return
                raise

            pos = page.find("id='image-list'")
            for post in text.extract_iter(
                    page, "<img id='thumb_", "Only</a>", pos):
                yield self._extract_data(post)

            if ">Next<" not in page:
                return
            pnum += 1

    def _extract_data(self, post):
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
            "date"     : self.parse_datetime(date, "%B %d, %Y; %H:%M"),
            "filename" : f"{pid} - {tags}",
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

    def get_posts(self):
        try:
            return (self._extract_post(self.groups[0]),)
        except exception.HttpError as exc:
            if exc.status == 404:
                return ()
            raise
