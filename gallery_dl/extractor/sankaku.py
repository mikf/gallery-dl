# -*- coding: utf-8 -*-

# Copyright 2014-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://sankaku.app/"""

from .booru import BooruExtractor
from .common import Message
from .. import text
import collections

BASE_PATTERN = r"(?:https?://)?" \
    r"(?:(?:chan|www|beta|black|white)\.sankakucomplex\.com|sankaku\.app)" \
    r"(?:/[a-z]{2})?"


class SankakuExtractor(BooruExtractor):
    """Base class for sankaku channel extractors"""
    basecategory = "booru"
    category = "sankaku"
    root = "https://sankaku.app"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    _warning = True

    def skip(self, num):
        return 0

    def _init(self):
        self.api = self.utils().SankakuAPI(self)
        if self.config("tags") == "extended":
            self._tags = self._tags_extended
            self._tags_findall = text.re(
                r"tag-type-([^\"' ]+).*?\?tags=([^\"'&]+)").findall

    def _file_url(self, post):
        url = post["file_url"]
        if not url:
            if post["status"] != "active":
                self.log.warning(
                    "Unable to download post %s (%s)",
                    post["id"], post["status"])
            elif self._warning:
                self.log.warning(
                    "Login required to download 'contentious_content' posts")
                SankakuExtractor._warning = False
        elif url[8] == "v":
            url = f"https://s.sankakucomplex.com{url[url.index('/', 8):]}"
        return url

    def _prepare(self, post):
        post["created_at"] = post["created_at"]["s"]
        post["date"] = self.parse_timestamp(post["created_at"])
        post["tags"] = post.pop("tag_names", ())
        post["tag_string"] = " ".join(post["tags"])
        post["_http_validate"] = self._check_expired

    def _check_expired(self, response):
        return not response.history or '.com/expired.png' not in response.url

    def _tags(self, post, page):
        tags = collections.defaultdict(list)
        for tag in self.api.tags(post["id"]):
            if name := tag["name"]:
                tags[tag["type"]].append(name.lower().replace(" ", "_"))
        types = self.utils().TAG_TYPES
        for type, values in tags.items():
            name = types[type]
            post[f"tags_{name}"] = values
            post[f"tag_string_{name}"] = " ".join(values)

    def _tags_extended(self, post, page):
        try:
            url = f"https://chan.sankakucomplex.com/posts/{post['id']}"
            headers = {"Referer": url}
            page = self.request(url, headers=headers).text
        except Exception as exc:
            return self.log.warning(
                "%s: Failed to extract extended tag categories (%s: %s)",
                post["id"], exc.__class__.__name__, exc)

        tags = collections.defaultdict(list)
        tag_sidebar = text.extr(page, '<ul id="tag-sidebar"', "</ul>")
        for tag_type, tag_name in self._tags_findall(tag_sidebar):
            tags[tag_type].append(text.unescape(text.unquote(tag_name)))
        for type, values in tags.items():
            post[f"tags_{type}"] = values
            post[f"tag_string_{type}"] = " ".join(values)

    def _notes(self, post, page):
        if post.get("has_notes"):
            post["notes"] = self.api.notes(post["id"])
            for note in post["notes"]:
                note["created_at"] = note["created_at"]["s"]
                note["updated_at"] = note["updated_at"]["s"]
        else:
            post["notes"] = ()


class SankakuTagExtractor(SankakuExtractor):
    """Extractor for images from sankaku.app by search-tags"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = rf"{BASE_PATTERN}(?:/posts)?/?\?([^#]*)"
    example = "https://sankaku.app/?tags=TAG"

    def posts(self):
        query = text.parse_query(self.groups[0])
        tags = text.unquote(query.get(
            "tags", "").replace("+", " "))

        if "date:" in tags:
            # rewrite 'date:' tags (#1790)
            tags = text.re(
                r"date:(\d\d)[.-](\d\d)[.-](\d\d\d\d)(?!T)").sub(
                r"date:\3-\2-\1T00:00", tags)
            tags = text.re(
                r"date:(\d\d\d\d)[.-](\d\d)[.-](\d\d)(?!T)").sub(
                r"date:\1-\2-\3T00:00", tags)

        self.kwdict["search_tags"] = tags
        params = {"tags": tags}
        return self.api.posts_keyset(params)


class SankakuPoolExtractor(SankakuExtractor):
    """Extractor for image pools or books from sankaku.app"""
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool[id]} {pool[name_en]}")
    archive_fmt = "p_{pool}_{id}"
    pattern = rf"{BASE_PATTERN}/(?:books|pools?/show)/(\w+)"
    example = "https://sankaku.app/books/12345"

    def posts(self):
        self.kwdict["pool"] = pool = self.api.pools(self.groups[0])
        pool["tags"] = [tag["name"] for tag in pool["tags"]]
        pool["artist_tags"] = [tag["name"] for tag in pool["artist_tags"]]

        posts = pool.pop("posts")
        for num, post in enumerate(posts, 1):
            post["num"] = num
        return posts


class SankakuPostExtractor(SankakuExtractor):
    """Extractor for single posts from sankaku.app"""
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = rf"{BASE_PATTERN}/posts?(?:/show)?/(\w+)"
    example = "https://sankaku.app/post/show/12345"

    def posts(self):
        return self.api.posts(self.groups[0])


class SankakuBooksExtractor(SankakuExtractor):
    """Extractor for books by tag search on sankaku.app"""
    subcategory = "books"
    pattern = rf"{BASE_PATTERN}/books/?\?([^#]*)"
    example = "https://sankaku.app/books?tags=TAG"

    def items(self):
        query = text.parse_query(self.groups[0])
        tags = text.unquote(query.get("tags", "").replace("+", " "))
        params = {"tags": tags, "pool_type": "0"}
        for pool in self.api.pools_keyset(params):
            pool["_extractor"] = SankakuPoolExtractor
            url = f"https://sankaku.app/books/{pool['id']}"
            yield Message.Queue, url, pool
