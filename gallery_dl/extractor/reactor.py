# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Generic extractors for *reactor sites"""

from .common import SharedConfigExtractor, Message
from .. import text
import urllib.parse
import random
import time
import json


BASE_PATTERN = r"(?:https?://)?([^/.]+\.reactor\.cc)"


class ReactorExtractor(SharedConfigExtractor):
    """Base class for *reactor.cc extractors"""
    basecategory = "reactor"
    directory_fmt = ["{category}"]
    filename_fmt = "{post_id}_{num:>02}{title[:100]:?_//}.{extension}"
    archive_fmt = "{post_id}_{num}"

    def __init__(self, match):
        SharedConfigExtractor.__init__(self)
        self.url = match.group(0)
        self.root = "http://" + match.group(1)
        self.session.headers["Referer"] = self.root

        self.wait_min = self.config("wait-min", 3)
        self.wait_max = self.config("wait-max", 6)
        if self.wait_max < self.wait_min:
            self.wait_max = self.wait_min

        if not self.category:
            # set category based on domain name
            netloc = urllib.parse.urlsplit(self.root).netloc
            self.category = netloc.rpartition(".")[0]

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
            time.sleep(random.uniform(self.wait_min, self.wait_max))
            page = self.request(url).text

            yield from text.extract_iter(
                page, '<div class="uhead">', '<div class="ufoot">')

            try:
                pos = page.index("class='next'")
                pos = page.rindex("class='current'", 0, pos)
                url = self.root + text.extract(page, "href='", "'", pos)[0]
            except (ValueError, TypeError):
                return

    def _parse_post(self, post):
        post, _, script = post.partition('<script type="application/ld+json">')
        images = text.extract_iter(post, '<div class="image">', '</div>')
        script = script[:script.index("</")].strip()

        try:
            data = json.loads(script)
        except ValueError:
            try:
                # remove control characters and escape backslashes
                mapping = dict.fromkeys(range(32))
                script = script.translate(mapping).replace("\\", "\\\\")
                data = json.loads(script)
            except ValueError as exc:
                self.log.warning("Unable to parse JSON data: %s", exc)
                return

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


class ReactorTagExtractor(ReactorExtractor):
    """Extractor for tag searches on *reactor.cc sites"""
    subcategory = "tag"
    directory_fmt = ["{category}", "{search_tags}"]
    archive_fmt = "{search_tags}_{post_id}_{num}"
    pattern = [BASE_PATTERN + r"/tag/([^/?&#]+)"]
    test = [("http://anime.reactor.cc/tag/Anime+Art", None)]

    def __init__(self, match):
        ReactorExtractor.__init__(self, match)
        self.tag = match.group(2)

    def metadata(self):
        return {"search_tags": text.unescape(self.tag).replace("+", " ")}


class ReactorSearchExtractor(ReactorTagExtractor):
    """Extractor for search results on *reactor.cc sites"""
    subcategory = "search"
    directory_fmt = ["{category}", "search", "{search_tags}"]
    archive_fmt = "s_{search_tags}_{post_id}_{num}"
    pattern = [BASE_PATTERN + r"/search(?:/|\?q=)([^/?&#]+)"]
    test = [("http://anime.reactor.cc/search?q=Art", None)]


class ReactorUserExtractor(ReactorExtractor):
    """Extractor for all posts of a user on *reactor.cc sites"""
    subcategory = "user"
    directory_fmt = ["{category}", "user", "{user}"]
    pattern = [BASE_PATTERN + r"/user/([^/?&#]+)"]
    test = [("http://anime.reactor.cc/user/Shuster", None)]

    def __init__(self, match):
        ReactorExtractor.__init__(self, match)
        self.user = match.group(2)

    def metadata(self):
        return {"user": text.unescape(self.user).replace("+", " ")}


class ReactorPostExtractor(ReactorExtractor):
    """Extractor for single posts on *reactor.cc sites"""
    subcategory = "post"
    pattern = [BASE_PATTERN + r"/post/(\d+)"]
    test = [("http://anime.reactor.cc/post/3576250", None)]

    def __init__(self, match):
        ReactorExtractor.__init__(self, match)
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


# --------------------------------------------------------------------
# JoyReactor

JR_BASE_PATTERN = r"(?:https?://)?(?:www\.)?(joyreactor\.c(?:c|om))"


class JoyreactorTagExtractor(ReactorTagExtractor):
    """Extractor for tag searches on joyreactor.cc"""
    category = "joyreactor"
    pattern = [JR_BASE_PATTERN + r"/tag/([^/?&#]+)"]
    test = [
        ("http://joyreactor.com/tag/Cirno", {
            "url": "a81382a3146da50b647c475f87427a6ca1d737df",
            "keyword": "dcd3b101cae0a93fbb91281235de1410faf88455",
        }),
        ("http://joyreactor.cc/tag/Advent+Cirno", {
            "count": ">= 17",
        }),
    ]


class JoyreactorSearchExtractor(ReactorSearchExtractor):
    """Extractor for search results on joyreactor.cc"""
    category = "joyreactor"
    pattern = [JR_BASE_PATTERN + r"/search(?:/|\?q=)([^/?&#]+)"]
    test = [
        ("http://joyreactor.com/search?q=Cirno+Gifs", {
            "count": 0,  # no search results on joyreactor.com
        }),
        ("http://joyreactor.cc/search/Cirno+Gifs", {
            "range": "1-25",
            "count": ">= 20",
        }),
    ]


class JoyreactorUserExtractor(ReactorUserExtractor):
    """Extractor for all posts of a user on joyreactor.cc"""
    category = "joyreactor"
    pattern = [JR_BASE_PATTERN + r"/user/([^/?&#]+)"]
    test = [
        ("http://joyreactor.com/user/Tacoman123", {
            "url": "0444158f17c22f08515ad4e7abf69ad2f3a63b35",
            "keyword": "1571a81fa5b8bab81528c93065d2460a72e77102",
        }),
        ("http://joyreactor.cc/user/hemantic", None),
    ]


class JoyreactorPostExtractor(ReactorPostExtractor):
    """Extractor for single posts on joyreactor.cc"""
    category = "joyreactor"
    pattern = [JR_BASE_PATTERN + r"/post/(\d+)"]
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


# --------------------------------------------------------------------
# PornReactor

PR_BASE_PATTERN = r"(?:https?://)?(?:www\.)?(pornreactor\.cc|fapreactor.com)"


class PornreactorTagExtractor(ReactorTagExtractor):
    """Extractor for tag searches on pornreactor.cc"""
    category = "pornreactor"
    pattern = [PR_BASE_PATTERN + r"/tag/([^/?&#]+)"]
    test = [
        ("http://pornreactor.cc/tag/RiceGnat", {
            "count": ">= 120",
        }),
        ("http://fapreactor.com/tag/RiceGnat", None),
    ]


class PornreactorSearchExtractor(ReactorSearchExtractor):
    """Extractor for search results on pornreactor.cc"""
    category = "pornreactor"
    pattern = [PR_BASE_PATTERN + r"/search(?:/|\?q=)([^/?&#]+)"]
    test = [
        ("http://pornreactor.cc/search?q=ecchi+hentai", {
            "range": "1-25",
            "count": ">= 20",
        }),
        ("http://fapreactor.com/search/ecchi+hentai", None),
    ]


class PornreactorUserExtractor(ReactorUserExtractor):
    """Extractor for all posts of a user on pornreactor.cc"""
    category = "pornreactor"
    pattern = [PR_BASE_PATTERN + r"/user/([^/?&#]+)"]
    test = [
        ("http://pornreactor.cc/user/Disillusion", {
            "url": "7e06f87f8dcce3fc7851b6d13aa55712ab45fb04",
            "keyword": "edfefb54ea4863e3731c508ae6caeb4140be0d31",
        }),
        ("http://fapreactor.com/user/Disillusion", None),
    ]


class PornreactorPostExtractor(ReactorPostExtractor):
    """Extractor for single posts on pornreactor.cc"""
    category = "pornreactor"
    subcategory = "post"
    pattern = [PR_BASE_PATTERN + r"/post/(\d+)"]
    test = [
        ("http://pornreactor.cc/post/863166", {
            "url": "9e5f7b374605cbbd413f4f4babb9d1af6f95b843",
            "keyword": "6e9e4bd4e2d4f3f2c7936340ec71f8693129f809",
            "content": "3e2a09f8b5e5ed7722f51c5f423ff4c9260fb23e",
        }),
        ("http://fapreactor.com/post/863166", {
            "url": "83ff7c87741c05bcf1de6825e2b4739afeb87ed5",
            "keyword": "cf8159224fde59c1dab86677514b4aedeb533d66",
        }),
    ]
