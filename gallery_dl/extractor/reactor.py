# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Generic extractors for *reactor sites"""

from .common import BaseExtractor, Message
from .. import text, util
import urllib.parse


class ReactorExtractor(BaseExtractor):
    """Base class for *reactor.cc extractors"""
    basecategory = "reactor"
    filename_fmt = "{post_id}_{num:>02}{title[:100]:?_//}.{extension}"
    archive_fmt = "{post_id}_{num}"
    request_interval = (3.0, 6.0)

    def __init__(self, match):
        BaseExtractor.__init__(self, match)

        url = text.ensure_http_scheme(match.group(0), "http://")
        pos = url.index("/", 10)
        self.root = url[:pos]
        self.path = url[pos:]

        if self.category == "reactor":
            # set category based on domain name
            netloc = urllib.parse.urlsplit(self.root).netloc
            self.category = netloc.rpartition(".")[0]

    def _init(self):
        self.gif = self.config("gif", False)

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
            data = util.json_loads(script)
        except ValueError:
            try:
                # remove control characters and escape backslashes
                mapping = dict.fromkeys(range(32))
                script = script.translate(mapping).replace("\\", "\\\\")
                data = util.json_loads(script)
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
            url = text.extr(image, ' src="', '"')
            if not url:
                continue
            if url.startswith("//"):
                url = "http:" + url
            width = text.extr(image, ' width="', '"')
            height = text.extr(image, ' height="', '"')
            image_id = url.rpartition("-")[2].partition(".")[0]
            num += 1

            if image.startswith("<iframe "):  # embed
                url = "ytdl:" + text.unescape(url)
            elif "/post/webm/" not in url and "/post/mp4/" not in url:
                url = url.replace("/post/", "/post/full/")

            if self.gif and ("/post/webm/" in url or "/post/mp4/" in url):
                gif_url = text.extr(image, '<a href="', '"')
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
    pattern = BASE_PATTERN + r"/tag/([^/?#]+)(?:/[^/?#]+)?"
    example = "http://reactor.cc/tag/TAG"

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
    example = "http://reactor.cc/search?q=QUERY"

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
    example = "http://reactor.cc/user/USER"

    def __init__(self, match):
        ReactorExtractor.__init__(self, match)
        self.user = match.group(match.lastindex)

    def metadata(self):
        return {"user": text.unescape(self.user).replace("+", " ")}


class ReactorPostExtractor(ReactorExtractor):
    """Extractor for single posts on *reactor.cc sites"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/post/(\d+)"
    example = "http://reactor.cc/post/12345"

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
