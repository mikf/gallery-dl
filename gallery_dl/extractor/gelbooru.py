# -*- coding: utf-8 -*-

# Copyright 2014-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://gelbooru.com/"""

from .common import Extractor, Message
from . import gelbooru_v02
from .. import text, exception
import binascii

BASE_PATTERN = r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?\?"


class GelbooruBase():
    """Base class for gelbooru extractors"""
    category = "gelbooru"
    basecategory = "booru"
    root = "https://gelbooru.com"
    offset = 0

    def _api_request(self, params, key="post", log=False):
        if "s" not in params:
            params["s"] = "post"
        params["api_key"] = self.api_key
        params["user_id"] = self.user_id

        url = self.root + "/index.php?page=dapi&q=index&json=1"
        data = self.request(url, params=params).json()

        if not key:
            return data

        try:
            posts = data[key]
        except KeyError:
            if log:
                self.log.error("Incomplete API response (missing '%s')", key)
                self.log.debug("%s", data)
            return []

        if not isinstance(posts, list):
            return (posts,)
        return posts

    def _pagination(self, params):
        params["pid"] = self.page_start
        params["limit"] = self.per_page
        limit = self.per_page // 2
        pid = False

        if "tags" in params:
            tags = params["tags"].split()
            op = "<"
            id = False

            for tag in tags:
                if tag.startswith("sort:"):
                    if tag == "sort:id:asc":
                        op = ">"
                    elif tag == "sort:id" or tag.startswith("sort:id:"):
                        op = "<"
                    else:
                        pid = True
                elif tag.startswith("id:"):
                    id = True

            if not pid:
                if id:
                    tag = "id:" + op
                    tags = [t for t in tags if not t.startswith(tag)]
                tags = "{} id:{}".format(" ".join(tags), op)

        while True:
            posts = self._api_request(params)

            yield from posts

            if len(posts) < limit:
                return

            if pid:
                params["pid"] += 1
            else:
                if "pid" in params:
                    del params["pid"]
                params["tags"] = tags + str(posts[-1]["id"])

    def _pagination_html(self, params):
        url = self.root + "/index.php"
        params["pid"] = self.offset

        data = {}
        while True:
            num_ids = 0
            page = self.request(url, params=params).text

            for data["id"] in text.extract_iter(page, '" id="p', '"'):
                num_ids += 1
                yield from self._api_request(data)

            if num_ids < self.per_page:
                return
            params["pid"] += self.per_page

    @staticmethod
    def _file_url(post):
        url = post["file_url"]
        if url.endswith((".webm", ".mp4")):
            md5 = post["md5"]
            path = "/images/{}/{}/{}.webm".format(md5[0:2], md5[2:4], md5)
            post["_fallback"] = GelbooruBase._video_fallback(path)
            url = "https://img3.gelbooru.com" + path
        return url

    @staticmethod
    def _video_fallback(path):
        yield "https://img2.gelbooru.com" + path
        yield "https://img1.gelbooru.com" + path

    def _notes(self, post, page):
        notes_data = text.extr(page, '<section id="notes"', '</section>')
        if not notes_data:
            return

        post["notes"] = notes = []
        extr = text.extract
        for note in text.extract_iter(notes_data, '<article', '</article>'):
            notes.append({
                "width" : int(extr(note, 'data-width="', '"')[0]),
                "height": int(extr(note, 'data-height="', '"')[0]),
                "x"     : int(extr(note, 'data-x="', '"')[0]),
                "y"     : int(extr(note, 'data-y="', '"')[0]),
                "body"  : extr(note, 'data-body="', '"')[0],
            })

    def _skip_offset(self, num):
        self.offset += num
        return num


class GelbooruTagExtractor(GelbooruBase,
                           gelbooru_v02.GelbooruV02TagExtractor):
    """Extractor for images from gelbooru.com based on search-tags"""
    pattern = BASE_PATTERN + r"page=post&s=list&tags=([^&#]*)"
    example = "https://gelbooru.com/index.php?page=post&s=list&tags=TAG"


class GelbooruPoolExtractor(GelbooruBase,
                            gelbooru_v02.GelbooruV02PoolExtractor):
    """Extractor for gelbooru pools"""
    per_page = 45
    pattern = BASE_PATTERN + r"page=pool&s=show&id=(\d+)"
    example = "https://gelbooru.com/index.php?page=pool&s=show&id=12345"

    skip = GelbooruBase._skip_offset

    def metadata(self):
        url = self.root + "/index.php"
        self._params = {
            "page": "pool",
            "s"   : "show",
            "id"  : self.pool_id,
        }
        page = self.request(url, params=self._params).text

        name, pos = text.extract(page, "<h3>Now Viewing: ", "</h3>")
        if not name:
            raise exception.NotFoundError("pool")

        return {
            "pool": text.parse_int(self.pool_id),
            "pool_name": text.unescape(name),
        }

    def posts(self):
        return self._pagination_html(self._params)


class GelbooruFavoriteExtractor(GelbooruBase,
                                gelbooru_v02.GelbooruV02FavoriteExtractor):
    """Extractor for gelbooru favorites"""
    per_page = 100
    pattern = BASE_PATTERN + r"page=favorites&s=view&id=(\d+)"
    example = "https://gelbooru.com/index.php?page=favorites&s=view&id=12345"

    skip = GelbooruBase._skip_offset

    def posts(self):
        # get number of favorites
        params = {
            "s"    : "favorite",
            "id"   : self.favorite_id,
            "limit": "2",
        }
        data = self._api_request(params, None, True)

        count = data["@attributes"]["count"]
        self.log.debug("API reports %s favorite entries", count)

        favs = data["favorite"]
        try:
            order = 1 if favs[0]["id"] < favs[1]["id"] else -1
        except LookupError as exc:
            self.log.debug(
                "Error when determining API favorite order (%s: %s)",
                exc.__class__.__name__, exc)
            order = -1
        else:
            self.log.debug("API yields favorites in %sscending order",
                           "a" if order > 0 else "de")

        order_favs = self.config("order-posts")
        if order_favs and order_favs[0] in ("r", "a"):
            self.log.debug("Returning them in reverse")
            order = -order

        if order < 0:
            return self._pagination(params, count)
        return self._pagination_reverse(params, count)

    def _pagination(self, params, count):
        if self.offset:
            pnum, skip = divmod(self.offset, self.per_page)
        else:
            pnum = skip = 0

        params["pid"] = pnum
        params["limit"] = self.per_page

        while True:
            favs = self._api_request(params, "favorite")

            if not favs:
                return

            if skip:
                favs = favs[skip:]
                skip = 0

            for fav in favs:
                for post in self._api_request({"id": fav["favorite"]}):
                    post["date_favorited"] = text.parse_timestamp(fav["added"])
                    yield post

            params["pid"] += 1

    def _pagination_reverse(self, params, count):
        pnum, last = divmod(count-1, self.per_page)
        if self.offset > last:
            # page number change
            self.offset -= last
            diff, self.offset = divmod(self.offset-1, self.per_page)
            pnum -= diff + 1
        skip = self.offset

        params["pid"] = pnum
        params["limit"] = self.per_page

        while True:
            favs = self._api_request(params, "favorite")
            favs.reverse()

            if skip:
                favs = favs[skip:]
                skip = 0

            for fav in favs:
                for post in self._api_request({"id": fav["favorite"]}):
                    post["date_favorited"] = text.parse_timestamp(fav["added"])
                    yield post

            params["pid"] -= 1
            if params["pid"] < 0:
                return


class GelbooruPostExtractor(GelbooruBase,
                            gelbooru_v02.GelbooruV02PostExtractor):
    """Extractor for single images from gelbooru.com"""
    pattern = (BASE_PATTERN +
               r"(?=(?:[^#]+&)?page=post(?:&|#|$))"
               r"(?=(?:[^#]+&)?s=view(?:&|#|$))"
               r"(?:[^#]+&)?id=(\d+)")
    example = "https://gelbooru.com/index.php?page=post&s=view&id=12345"


class GelbooruRedirectExtractor(GelbooruBase, Extractor):
    subcategory = "redirect"
    pattern = (r"(?:https?://)?(?:www\.)?gelbooru\.com"
               r"/redirect\.php\?s=([^&#]+)")
    example = "https://gelbooru.com/redirect.php?s=BASE64"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.url_base64 = match.group(1)

    def items(self):
        url = text.ensure_http_scheme(binascii.a2b_base64(
            self.url_base64).decode())
        data = {"_extractor": GelbooruPostExtractor}
        yield Message.Queue, url, data
