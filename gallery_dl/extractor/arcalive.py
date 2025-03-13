# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://arca.live/"""

from .common import Extractor, Message
from .. import text, util, exception
import re

BASE_PATTERN = r"(?:https?://)?(?:www\.)?arca\.live"


class ArcaliveExtractor(Extractor):
    """Base class for Arca.live extractors"""
    category = "arcalive"
    root = "https://arca.live"
    request_interval = (0.5, 1.5)

    def _init(self):
        self.api = ArcaliveAPI(self)


class ArcalivePostExtractor(ArcaliveExtractor):
    """Extractor for an arca.live post"""
    subcategory = "post"
    directory_fmt = ("{category}", "{boardSlug}")
    filename_fmt = "{id}_{num}{title:? //[b:230]}.{extension}"
    archive_fmt = "{id}_{num}"
    pattern = BASE_PATTERN + r"/b/(?:\w+)/(\d+)"
    example = "https://arca.live/b/breaking/123456789"

    def items(self):
        self.emoticons = self.config("emoticons", False)

        post = self.api.post(self.groups[0])
        files = self._extract_files(post)

        post["count"] = len(files)
        post["date"] = text.parse_datetime(
            post["createdAt"][:19], "%Y-%m-%dT%H:%M:%S")
        post["post_url"] = post_url = "{}/b/{}/{}".format(
            self.root, post["boardSlug"], post["id"])
        post["_http_headers"] = {"Referer": post_url + "?p=1"}

        yield Message.Directory, post
        for post["num"], file in enumerate(files, 1):
            post.update(file)
            url = file["url"]
            yield Message.Url, url, text.nameext_from_url(url, post)

    def _extract_files(self, post):
        files = []

        for media in self._extract_media(post["content"]):

            if not self.emoticons and 'class="arca-emoticon"' in media:
                continue

            src = (text.extr(media, 'data-originalurl="', '"') or
                   text.extr(media, 'src="', '"'))
            if not src:
                continue

            src = text.unescape(src.partition("?")[0])
            if src[0] == "/":
                if src[1] == "/":
                    url = "https:" + src
                else:
                    url = self.root + src
            else:
                url = src

            fallback = ()
            orig = text.extr(media, 'data-orig="', '"')
            if orig:
                path, _, ext = url.rpartition(".")
                if ext != orig:
                    fallback = (url + "?type=orig",)
                    url = path + "." + orig

            files.append({
                "url"   : url + "?type=orig",
                "width" : text.parse_int(text.extr(media, 'width="', '"')),
                "height": text.parse_int(text.extr(media, 'height="', '"')),
                "_fallback": fallback,
            })

        return files

    def _extract_media(self, content):
        ArcalivePostExtractor._extract_media = extr = re.compile(
            r"<(?:img|video) ([^>]+)").findall
        return extr(content)


class ArcaliveBoardExtractor(ArcaliveExtractor):
    """Extractor for an arca.live board's posts"""
    subcategory = "board"
    pattern = BASE_PATTERN + r"/b/(\w+)(?:/?\?([^#]+))?$"
    example = "https://arca.live/b/breaking"

    def items(self):
        board, query = self.groups
        params = text.parse_query(query)
        articles = self.api.board(board, params)

        for article in articles:
            article["_extractor"] = ArcalivePostExtractor
            url = "{}/b/{}/{}".format(self.root, board, article["id"])
            yield Message.Queue, url, article


class ArcaliveAPI():

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log
        self.root = extractor.root + "/api/app"

        headers = extractor.session.headers
        headers["User-Agent"] = "net.umanle.arca.android.playstore/0.9.75"
        headers["X-Device-Token"] = util.generate_token(64)

    def board(self, board_slug, params):
        endpoint = "/list/channel/" + board_slug
        return self._pagination(endpoint, params, "articles")

    def post(self, post_id):
        endpoint = "/view/article/breaking/" + str(post_id)
        return self._call(endpoint)

    def _call(self, endpoint, params=None):
        url = self.root + endpoint
        response = self.extractor.request(url, params=params)

        data = response.json()
        if response.status_code == 200:
            return data

        self.log.debug("Server response: %s", data)
        msg = data.get("message")
        raise exception.StopExtraction(
            "API request failed%s", ": " + msg if msg else "")

    def _pagination(self, endpoint, params, key):
        while True:
            data = self._call(endpoint, params)

            posts = data.get(key)
            if not posts:
                break
            yield from posts

            params.update(data["next"])
