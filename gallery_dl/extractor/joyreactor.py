# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for http://joyreactor.cc/"""

from .common import Extractor, Message
from .. import text
import json


BASE_PATTERN = r"(?:https?://)?(?:www\.)?(joyreactor\.c(?:c|om))"


class JoyreactorExtractor(Extractor):
    """Base class for joyreactor extractors"""
    category = "joyreactor"
    directory_fmt = ["{category}"]
    filename_fmt = "{post_id}_{num:>02}{title[:100]:?_//}.{extension}"
    archive_fmt = "{post_id}_{num}"

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.group(0)
        self.root = "http://" + match.group(1)
        self.session.headers["Referer"] = self.root

    def items(self):
        data = self.metadata()
        yield Message.Version, 1
        yield Message.Directory, data
        for post in self.posts():
            for image in self._parse_post(post):
                url = image["file_url"]
                image.update(data)
                yield Message.Url, url, text.nameext_from_url(url, image)

    def metadata(self):
        """Collect metadata for extractor-job"""
        return {}

    def posts(self):
        """Return all relevant post-objects"""
        return self._pagination(self.url)

    def _pagination(self, url):
        while True:
            page = self.request(url).text

            yield from text.extract_iter(
                page, '<div class="uhead">', '<div class="ufoot">')

            pos = page.find("<span class='current'>")
            if pos == -1 or page[pos+21:pos+24] == ">1<":
                return
            path = text.extract(page, "href='", "'", pos)[0]
            if not path:
                return
            url = self.root + path

    @staticmethod
    def _parse_post(post):
        post, _, script = post.partition('<script type="application/ld+json">')
        images = text.extract_iter(post, '<div class="image">', '</div>')
        script = script[:script.index("</")].strip()

        try:
            data = json.loads(script)
        except ValueError:
            data = json.loads(script
                              .replace("\\", "\\\\")
                              .replace("\n", "")
                              .replace("\r", ""))

        num = 0
        date = data["datePublished"]
        user = data["author"]["name"]
        description = text.unescape(data["description"])
        title, _, tags = text.unescape(data["headline"]).partition(" / ")
        post_id = text.parse_int(
            data["mainEntityOfPage"]["@id"].rpartition("/")[2])

        if not tags:
            title, tags = tags, title

        for image in images:
            url = text.extract(image, ' src="', '"')[0]
            if not url:
                continue
            width = text.extract(image, ' width="', '"')[0]
            height = text.extract(image, ' height="', '"')[0]
            image_id = url.rpartition("-")[2].partition(".")[0]
            num += 1

            if image.startswith("<iframe "):  # embed
                url = "ytdl:" + text.unescape(url)

            yield {
                "file_url": url,
                "post_id": post_id,
                "image_id": text.parse_int(image_id),
                "width": text.parse_int(width),
                "height": text.parse_int(height),
                "title": title,
                "description": description,
                "tags": tags,
                "date": date,
                "user": user,
                "num": num,
            }


class JoyreactorTagExtractor(JoyreactorExtractor):
    """Extractor for tag searches on joyreactor.cc"""
    subcategory = "tag"
    directory_fmt = ["{category}", "{search_tags}"]
    archive_fmt = "{search_tags}_{post_id}_{num}"
    pattern = [BASE_PATTERN + r"/tag/([^/?&#]+)"]
    test = [
        ("http://joyreactor.com/tag/Cirno", {
            "url": "a81382a3146da50b647c475f87427a6ca1d737df",
            "keyword": "dcd3b101cae0a93fbb91281235de1410faf88455",
        }),
        ("http://joyreactor.cc/tag/Advent+Cirno", {
            "count": ">= 17",
        }),
    ]

    def __init__(self, match):
        JoyreactorExtractor.__init__(self, match)
        self.tag = match.group(2)

    def metadata(self):
        return {"search_tags": text.unescape(self.tag).replace("+", " ")}


class JoyreactorUserExtractor(JoyreactorExtractor):
    """Extractor for all posts of a user on joyreactor.cc"""
    subcategory = "user"
    directory_fmt = ["{category}", "user", "{user}"]
    pattern = [BASE_PATTERN + r"/user/([^/?&#]+)"]
    test = [
        ("http://joyreactor.com/user/Tacoman123", {
            "url": "0444158f17c22f08515ad4e7abf69ad2f3a63b35",
            "keyword": "1571a81fa5b8bab81528c93065d2460a72e77102",
        }),
        ("http://joyreactor.cc/user/hemantic", None),
    ]

    def __init__(self, match):
        JoyreactorExtractor.__init__(self, match)
        self.user = match.group(2)

    def metadata(self):
        return {"user": text.unescape(self.user).replace("+", " ")}


class JoyreactorPostExtractor(JoyreactorExtractor):
    """Extractor for single posts on joyreactor.cc"""
    subcategory = "post"
    pattern = [BASE_PATTERN + r"/post/(\d+)"]
    test = [
        ("http://joyreactor.com/post/3721876", {  # single image
            "url": "904779f6571436f3d5adbce30c2c272f6401e14a",
            "keyword": "0d231f6ae36c5dca1f7eb71443bab3b2659fcacc",
        }),
        ("http://joyreactor.com/post/3713804", {  # 4 images
            "url": "99c614416b959f22001f7da3f68df03b1551abdf",
            "keyword": "1f0bf40f5030c803de6f8969099689e36fe885e6",
        }),
        ("http://joyreactor.com/post/3726210", {  # gif / video
            "url": "33a48e1eca6cb2d298fbbb6536b3283799d6515b",
            "keyword": "b2514c20f59b9c521545e96ca1a9ad504d6fa7e5",
        }),
        ("http://joyreactor.com/post/3668724", {  # youtube embed
            "url": "be2589e2e8f3ffcaf41b34bc28bfad850ccea34a",
            "keyword": "97e2cdef751fba13e43d789ddfb806683a903fae",
        }),
        ("http://joyreactor.cc/post/1299", {  # "malformed" JSON
            "url": "d45337fec926159afe11c59e32d259d793dd00b3",
            "keyword": "d28e2f44c2d107d549d91c443e489d2454a64181",
        }),
    ]

    def __init__(self, match):
        JoyreactorExtractor.__init__(self, match)
        self.post_id = match.group(2)

    def items(self):
        yield Message.Version, 1
        post = self.request(self.url).text
        pos = post.find('class="uhead">')
        for image in self._parse_post(post[pos:]):
            if image["num"] == 1:
                yield Message.Directory, image
            url = image["file_url"]
            yield Message.Url, url, text.nameext_from_url(url, image)
