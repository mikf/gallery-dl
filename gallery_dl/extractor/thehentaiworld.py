# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://thehentaiworld.com/"""

from .common import Extractor, Message
from .. import text, util
import collections

BASE_PATTERN = r"(?:https?://)?(?:www\.)?thehentaiworld\.com"


class ThehentaiworldExtractor(Extractor):
    """Base class for thehentaiworld extractors"""
    category = "thehentaiworld"
    root = "https://thehentaiworld.com"
    filename_fmt = "{title} ({id}{num:?-//}).{extension}"
    archive_fmt = "{id}_{num}"
    request_interval = (0.5, 1.5)

    def items(self):
        for url in self.posts():
            try:
                post = self._extract_post(url)
            except Exception as exc:
                self.status |= 1
                self.log.warning("Failed to extract post %s (%s: %s)",
                                 url, exc.__class__.__name__, exc)
                continue

            if "file_urls" in post:
                urls = post["file_urls"]
                post["count"] = len(urls)
                yield Message.Directory, "", post
                for post["num"], url in enumerate(urls, 1):
                    text.nameext_from_url(url, post)
                    yield Message.Url, url, post
            else:
                yield Message.Directory, "", post
                url = post["file_url"]
                text.nameext_from_url(url, post)
                yield Message.Url, url, post

    def _extract_post(self, url):
        extr = text.extract_from(self.request(url).text)

        post = {
            "num"     : 0,
            "count"   : 1,
            "title"   : text.unescape(extr("<title>", "<").strip()),
            "id"      : text.parse_int(extr(" postid-", " ")),
            "slug"    : extr(" post-", '"'),
            "tags"    : extr('id="tagsHead">', "</ul>"),
            "date"    : self.parse_datetime_iso(extr("<li>Posted: ", "<")),
        }

        if (c := url[27]) == "v":
            post["type"] = "video"
            post["width"] = post["height"] = 0
            post["votes"] = text.parse_int(extr("(<strong>", "</strong>"))
            post["score"] = text.parse_float(extr("<strong>", "<"))
            post["file_url"] = extr('<source src="', '"')
        else:
            post["type"] = ("animated" if c == "g" else
                            "3d cgi" if c == "3" else
                            "image")
            post["width"] = text.parse_int(extr("<li>Size: ", " "))
            post["height"] = text.parse_int(extr("x ", "<"))
            post["file_url"] = extr('a href="', '"')
            post["votes"] = text.parse_int(extr("(<strong>", "</strong>"))
            post["score"] = text.parse_float(extr("<strong>", "<"))

            if doujin := extr('<a id="prev-page"', "</div></div><"):
                repl = text.re(r"-220x\d+\.").sub
                post["file_urls"] = [
                    repl(".", url)
                    for url in text.extract_iter(
                        doujin, 'class="border" src="', '"')
                ]

        tags = collections.defaultdict(list)
        pattern = text.re(r'<li><a class="([^"]*)" href="[^"]*">([^<]+)')
        for tag_type, tag_name in pattern.findall(post["tags"]):
            tags[tag_type].append(tag_name)
        post["tags"] = tags_list = []
        for key, value in tags.items():
            tags_list.extend(value)
            post[f"tags_{key}" if key else "tags_general"] = value

        return post

    def _pagination(self, endpoint):
        base = f"{self.root}{endpoint}"
        pnum = self.page_start

        while True:
            url = base if pnum < 2 else f"{base}page/{pnum}/"
            page = self.request(url).text

            yield from text.extract_iter(text.extr(
                page, 'id="thumbContainer"', "<script"), ' href="', '"')

            if 'class="next"' not in page:
                return
            pnum += 1


class ThehentaiworldTagExtractor(ThehentaiworldExtractor):
    subcategory = "tag"
    per_page = 24
    page_start = 1
    post_start = 0
    directory_fmt = ("{category}", "{search_tags}")
    pattern = rf"{BASE_PATTERN}/tag/([^/?#]+)"
    example = "https://thehentaiworld.com/tag/TAG/"

    def posts(self):
        self.kwdict["search_tags"] = tag = self.groups[0]
        return util.advance(self._pagination(f"/tag/{tag}/"), self.post_start)

    def skip(self, num):
        pages, posts = divmod(num, self.per_page)
        self.page_start += pages
        self.post_start += posts
        return num


class ThehentaiworldPostExtractor(ThehentaiworldExtractor):
    subcategory = "post"
    pattern = (rf"{BASE_PATTERN}("
               rf"/(?:video|(?:[\w-]+-)?hentai-image)s/([^/?#]+))")
    example = "https://thehentaiworld.com/hentai-images/SLUG/"

    def posts(self):
        return (f"{self.root}{self.groups[0]}/",)
