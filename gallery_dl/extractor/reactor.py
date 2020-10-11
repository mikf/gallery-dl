# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Generic extractors for *reactor sites"""

from .common import Extractor, Message, SharedConfigMixin
from .. import text
import urllib.parse
import random
import time
import json


BASE_PATTERN = r"(?:https?://)?((?:[^/.]+\.)?reactor\.cc)"


class ReactorExtractor(SharedConfigMixin, Extractor):
    """Base class for *reactor.cc extractors"""
    basecategory = "reactor"
    filename_fmt = "{post_id}_{num:>02}{title[:100]:?_//}.{extension}"
    archive_fmt = "{post_id}_{num}"

    def __init__(self, match):
        Extractor.__init__(self, match)
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
                url = image["url"]
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

            response = self.request(url)
            if response.history:
                # sometimes there is a redirect from
                # the last page of a listing (.../tag/<tag>/1)
                # to the first page (.../tag/<tag>)
                # which could cause an endless loop
                cnt_old = response.history[0].url.count("/")
                cnt_new = response.url.count("/")
                if cnt_old == 5 and cnt_new == 4:
                    return
            page = response.text

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
        date = text.parse_datetime(data["datePublished"])
        user = data["author"]["name"]
        description = text.unescape(data["description"])
        title, _, tags = text.unescape(data["headline"]).partition(" / ")
        post_id = text.parse_int(
            data["mainEntityOfPage"]["@id"].rpartition("/")[2])

        if not tags:
            title, tags = tags, title
        tags = tags.split(" :: ")
        tags.sort()

        for image in images:
            url = text.extract(image, ' src="', '"')[0]
            if not url:
                continue
            if url.startswith("//"):
                url = "http:" + url
            width = text.extract(image, ' width="', '"')[0]
            height = text.extract(image, ' height="', '"')[0]
            image_id = url.rpartition("-")[2].partition(".")[0]
            num += 1

            if image.startswith("<iframe "):  # embed
                url = "ytdl:" + text.unescape(url)
            elif "/post/webm/" not in url and "/post/mp4/" not in url:
                url = url.replace("/post/", "/post/full/")

            yield {
                "url": url,
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
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "{search_tags}_{post_id}_{num}"
    pattern = BASE_PATTERN + r"/tag/([^/?&#]+)"
    test = ("http://anime.reactor.cc/tag/Anime+Art",)

    def __init__(self, match):
        ReactorExtractor.__init__(self, match)
        self.tag = match.group(2)

    def metadata(self):
        return {"search_tags": text.unescape(self.tag).replace("+", " ")}


class ReactorSearchExtractor(ReactorTagExtractor):
    """Extractor for search results on *reactor.cc sites"""
    subcategory = "search"
    directory_fmt = ("{category}", "search", "{search_tags}")
    archive_fmt = "s_{search_tags}_{post_id}_{num}"
    pattern = BASE_PATTERN + r"/search(?:/|\?q=)([^/?&#]+)"
    test = ("http://anime.reactor.cc/search?q=Art",)


class ReactorUserExtractor(ReactorExtractor):
    """Extractor for all posts of a user on *reactor.cc sites"""
    subcategory = "user"
    directory_fmt = ("{category}", "user", "{user}")
    pattern = BASE_PATTERN + r"/user/([^/?&#]+)"
    test = ("http://anime.reactor.cc/user/Shuster",)

    def __init__(self, match):
        ReactorExtractor.__init__(self, match)
        self.user = match.group(2)

    def metadata(self):
        return {"user": text.unescape(self.user).replace("+", " ")}


class ReactorPostExtractor(ReactorExtractor):
    """Extractor for single posts on *reactor.cc sites"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/post/(\d+)"
    test = ("http://anime.reactor.cc/post/3576250",)

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
            url = image["url"]
            yield Message.Url, url, text.nameext_from_url(url, image)


# --------------------------------------------------------------------
# JoyReactor

JR_BASE_PATTERN = r"(?:https?://)?(?:www\.)?(joyreactor\.c(?:c|om))"


class JoyreactorTagExtractor(ReactorTagExtractor):
    """Extractor for tag searches on joyreactor.cc"""
    category = "joyreactor"
    pattern = JR_BASE_PATTERN + r"/tag/([^/?&#]+)"
    test = (
        ("http://joyreactor.cc/tag/Advent+Cirno", {
            "count": ">= 17",
        }),
        ("http://joyreactor.com/tag/Cirno", {
            "url": "de1e60c15bfb07a0e9603b00dc3d05f60edc7914",
        }),
    )


class JoyreactorSearchExtractor(ReactorSearchExtractor):
    """Extractor for search results on joyreactor.cc"""
    category = "joyreactor"
    pattern = JR_BASE_PATTERN + r"/search(?:/|\?q=)([^/?&#]+)"
    test = (
        ("http://joyreactor.cc/search/Cirno+Gifs", {
            "range": "1-25",
            "count": ">= 20",
        }),
        ("http://joyreactor.com/search?q=Cirno+Gifs", {
            "count": 0,  # no search results on joyreactor.com
        }),
    )


class JoyreactorUserExtractor(ReactorUserExtractor):
    """Extractor for all posts of a user on joyreactor.cc"""
    category = "joyreactor"
    pattern = JR_BASE_PATTERN + r"/user/([^/?&#]+)"
    test = (
        ("http://joyreactor.cc/user/hemantic"),
        ("http://joyreactor.com/user/Tacoman123", {
            "url": "452cd0fa23e2ad0e122c296ba75aa7f0b29329f6",
        }),
    )


class JoyreactorPostExtractor(ReactorPostExtractor):
    """Extractor for single posts on joyreactor.cc"""
    category = "joyreactor"
    pattern = JR_BASE_PATTERN + r"/post/(\d+)"
    test = (
        ("http://joyreactor.com/post/3721876", {  # single image
            "url": "6ce09f239d8b7fdf6dd1664c2afc39618cc87663",
            "keyword": "147ed5b9799ba43cbd16168450afcfae5ddedbf3",
        }),
        ("http://joyreactor.com/post/3713804", {  # 4 images
            "url": "f08ac8493ca0619a3e3c6bedb8d8374af3eec304",
            "keyword": "f12c6f3c2f298fed9b12bd3e70fb823870aa9b93",
        }),
        ("http://joyreactor.com/post/3726210", {  # gif / video
            "url": "33a48e1eca6cb2d298fbbb6536b3283799d6515b",
            "keyword": "d173cc6e88f02a63904e475eacd7050304eb1967",
        }),
        ("http://joyreactor.com/post/3668724", {  # youtube embed
            "url": "bf1666eddcff10c9b58f6be63fa94e4e13074214",
            "keyword": "e18b1ffbd79d76f9a0e90b6d474cc2499e343f0b",
        }),
        ("http://joyreactor.cc/post/1299", {  # "malformed" JSON
            "url": "ac900743ed7cf1baf3db3b531c3bc414bf1ffcde",
        }),
    )


# --------------------------------------------------------------------
# PornReactor

PR_BASE_PATTERN = r"(?:https?://)?(?:www\.)?(pornreactor\.cc|fapreactor.com)"


class PornreactorTagExtractor(ReactorTagExtractor):
    """Extractor for tag searches on pornreactor.cc"""
    category = "pornreactor"
    pattern = PR_BASE_PATTERN + r"/tag/([^/?&#]+)"
    test = (
        ("http://pornreactor.cc/tag/RiceGnat", {
            "range": "1-25",
            "count": ">= 25",
        }),
        ("http://fapreactor.com/tag/RiceGnat"),
    )


class PornreactorSearchExtractor(ReactorSearchExtractor):
    """Extractor for search results on pornreactor.cc"""
    category = "pornreactor"
    pattern = PR_BASE_PATTERN + r"/search(?:/|\?q=)([^/?&#]+)"
    test = (
        ("http://pornreactor.cc/search?q=ecchi+hentai", {
            "range": "1-25",
            "count": ">= 25",
        }),
        ("http://fapreactor.com/search/ecchi+hentai"),
    )


class PornreactorUserExtractor(ReactorUserExtractor):
    """Extractor for all posts of a user on pornreactor.cc"""
    category = "pornreactor"
    pattern = PR_BASE_PATTERN + r"/user/([^/?&#]+)"
    test = (
        ("http://pornreactor.cc/user/Disillusion", {
            "range": "1-25",
            "count": ">= 25",
        }),
        ("http://fapreactor.com/user/Disillusion"),
    )


class PornreactorPostExtractor(ReactorPostExtractor):
    """Extractor for single posts on pornreactor.cc"""
    category = "pornreactor"
    subcategory = "post"
    pattern = PR_BASE_PATTERN + r"/post/(\d+)"
    test = (
        ("http://pornreactor.cc/post/863166", {
            "url": "680db1e33ca92ff70b2c0e1708c471cbe2201324",
            "content": "ec6b0568bfb1803648744077da082d14de844340",
        }),
        ("http://fapreactor.com/post/863166", {
            "url": "864ecd5785e4898301aa8d054dd653b1165be158",
        }),
    )
