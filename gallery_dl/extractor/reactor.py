# -*- coding: utf-8 -*-

# Copyright 2019-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Generic extractors for *reactor sites"""

from .common import BaseExtractor, Message
from .. import text
import urllib.parse
import json


class ReactorExtractor(BaseExtractor):
    """Base class for *reactor.cc extractors"""
    basecategory = "reactor"
    filename_fmt = "{post_id}_{num:>02}{title[:100]:?_//}.{extension}"
    archive_fmt = "{post_id}_{num}"
    request_interval = 5.0

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        url = text.ensure_http_scheme(match.group(0), "http://")
        pos = url.index("/", 10)

        self.root, self.path = url[:pos], url[pos:]
        self.session.headers["Referer"] = self.root
        self.gif = self.config("gif", False)

        if self.category == "reactor":
            # set category based on domain name
            netloc = urllib.parse.urlsplit(self.root).netloc
            self.category = netloc.rpartition(".")[0]

    def items(self):
        data = self.metadata()
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
        return self._pagination(self.root + self.path)

    def _pagination(self, url):
        while True:
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
        if not script:
            return
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

            if self.gif and ("/post/webm/" in url or "/post/mp4/" in url):
                gif_url = text.extract(image, '<a href="', '"')[0]
                if not gif_url:
                    continue
                url = gif_url

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


BASE_PATTERN = ReactorExtractor.update({
    "reactor"    : {
        "root": "http://reactor.cc",
        "pattern": r"(?:[^/.]+\.)?reactor\.cc",
    },
    "joyreactor" : {
        "root": "http://joyreactor.cc",
        "pattern": r"(?:www\.)?joyreactor\.c(?:c|om)",
    },
    "pornreactor": {
        "root": "http://pornreactor.cc",
        "pattern": r"(?:www\.)?(?:pornreactor\.cc|fapreactor.com)",
    },
    "thatpervert": {
        "root": "http://thatpervert.com",
        "pattern": r"thatpervert\.com",
    },
})


class ReactorTagExtractor(ReactorExtractor):
    """Extractor for tag searches on *reactor.cc sites"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "{search_tags}_{post_id}_{num}"
    pattern = BASE_PATTERN + r"/tag/([^/?#]+)"
    test = (
        ("http://reactor.cc/tag/gif"),
        ("http://anime.reactor.cc/tag/Anime+Art"),
        ("http://joyreactor.cc/tag/Advent+Cirno", {
            "count": ">= 15",
        }),
        ("http://joyreactor.com/tag/Cirno", {
            "url": "aa59090590b26f4654881301fe8fe748a51625a8",
        }),
        ("http://pornreactor.cc/tag/RiceGnat", {
            "range": "1-25",
            "count": ">= 25",
        }),
        ("http://fapreactor.com/tag/RiceGnat"),
    )

    def __init__(self, match):
        ReactorExtractor.__init__(self, match)
        self.tag = match.group(match.lastindex)

    def metadata(self):
        return {"search_tags": text.unescape(self.tag).replace("+", " ")}


class ReactorSearchExtractor(ReactorExtractor):
    """Extractor for search results on *reactor.cc sites"""
    subcategory = "search"
    directory_fmt = ("{category}", "search", "{search_tags}")
    archive_fmt = "s_{search_tags}_{post_id}_{num}"
    pattern = BASE_PATTERN + r"/search(?:/|\?q=)([^/?#]+)"
    test = (
        ("http://reactor.cc/search?q=Art"),
        ("http://joyreactor.cc/search/Nature", {
            "range": "1-25",
            "count": ">= 20",
        }),
        ("http://joyreactor.com/search?q=Nature", {
            "range": "1-25",
            "count": ">= 20",
        }),
        ("http://pornreactor.cc/search?q=ecchi+hentai"),
        ("http://fapreactor.com/search/ecchi+hentai"),
    )

    def __init__(self, match):
        ReactorExtractor.__init__(self, match)
        self.tag = match.group(match.lastindex)

    def metadata(self):
        return {"search_tags": text.unescape(self.tag).replace("+", " ")}


class ReactorUserExtractor(ReactorExtractor):
    """Extractor for all posts of a user on *reactor.cc sites"""
    subcategory = "user"
    directory_fmt = ("{category}", "user", "{user}")
    pattern = BASE_PATTERN + r"/user/([^/?#]+)"
    test = (
        ("http://reactor.cc/user/Dioklet"),
        ("http://anime.reactor.cc/user/Shuster"),
        ("http://joyreactor.cc/user/hemantic"),
        ("http://joyreactor.com/user/Tacoman123", {
            "url": "60ce9a3e3db791a0899f7fb7643b5b87d09ae3b5",
        }),
        ("http://pornreactor.cc/user/Disillusion", {
            "range": "1-25",
            "count": ">= 20",
        }),
        ("http://fapreactor.com/user/Disillusion"),
    )

    def __init__(self, match):
        ReactorExtractor.__init__(self, match)
        self.user = match.group(match.lastindex)

    def metadata(self):
        return {"user": text.unescape(self.user).replace("+", " ")}


class ReactorPostExtractor(ReactorExtractor):
    """Extractor for single posts on *reactor.cc sites"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/post/(\d+)"
    test = (
        ("http://reactor.cc/post/4999736", {
            "url": "dfc74d150d7267384d8c229c4b82aa210755daa0",
        }),
        ("http://anime.reactor.cc/post/3576250"),
        ("http://joyreactor.com/post/3721876", {  # single image
            "pattern": r"http://img\d\.joyreactor\.com/pics/post/full"
                       r"/cartoon-painting-monster-lake-4841316.jpeg",
            "count": 1,
            "keyword": "2207a7dfed55def2042b6c2554894c8d7fda386e",
        }),
        ("http://joyreactor.com/post/3713804", {  # 4 images
            "pattern": r"http://img\d\.joyreactor\.com/pics/post/full"
                       r"/movie-tv-godzilla-monsters-\d+\.jpeg",
            "count": 4,
            "keyword": "d7da9ba7809004c809eedcf6f1c06ad0fbb3df21",
        }),
        ("http://joyreactor.com/post/3726210", {  # gif / video
            "url": "60f3b9a0a3918b269bea9b4f8f1a5ab3c2c550f8",
            "keyword": "8949d9d5fc469dab264752432efbaa499561664a",
        }),
        ("http://joyreactor.com/post/3668724", {  # youtube embed
            "url": "bf1666eddcff10c9b58f6be63fa94e4e13074214",
            "keyword": "e18b1ffbd79d76f9a0e90b6d474cc2499e343f0b",
        }),
        ("http://joyreactor.cc/post/1299", {  # "malformed" JSON
            "url": "ab02c6eb7b4035ad961b29ee0770ee41be2fcc39",
        }),
        ("http://pornreactor.cc/post/863166", {
            "url": "a09fb0577489e1f9564c25d0ad576f81b19c2ef3",
            "content": "ec6b0568bfb1803648744077da082d14de844340",
        }),
        ("http://fapreactor.com/post/863166", {
            "url": "2a956ce0c90e8bc47b4392db4fa25ad1342f3e54",
        }),
    )

    def __init__(self, match):
        ReactorExtractor.__init__(self, match)
        self.post_id = match.group(match.lastindex)

    def items(self):
        post = self.request(self.root + self.path).text
        pos = post.find('class="uhead">')
        for image in self._parse_post(post[pos:]):
            if image["num"] == 1:
                yield Message.Directory, image
            url = image["url"]
            yield Message.Url, url, text.nameext_from_url(url, image)
