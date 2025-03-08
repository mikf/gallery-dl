# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://tenor.com/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?tenor\.com/(?:\w\w(?:-\w\w)?/)?"


class TenorExtractor(Extractor):
    """Base class for tenor extractors"""
    category = "tenor"
    root = "https://tenor.com"
    filename_fmt = "{id}{title:? //}.{extension}"
    archive_fmt = "{id}"
    request_interval = (0.5, 1.5)

    def _init(self):
        formats = self.config("format")
        if formats is None:
            self.formats = ("gif", "mp4", "webm", "webp")
        else:
            if isinstance(formats, str):
                formats = formats.split(",")
            self.formats = formats

    def items(self):
        meta = self.metadata()

        for gif in self.gifs():
            fmt = self._extract_format(gif)
            if not fmt:
                self.log.warning("%s: Selected format(s) not available",
                                 gif.get("id"))
                continue

            url = fmt["url"]
            gif["width"], gif["height"] = fmt["dims"]
            gif["title"] = gif["h1_title"][:-4]
            gif["description"] = gif.pop("content_description", "")
            gif["date"] = text.parse_timestamp(gif["created"])
            if meta:
                gif.update(meta)

            yield Message.Directory, gif
            yield Message.Url, url, text.nameext_from_url(url, gif)

    def _extract_format(self, gif):
        media_formats = gif["media_formats"]
        for fmt in self.formats:
            if fmt in media_formats:
                return media_formats[fmt]

    def _search_results(self, query):
        url = "https://tenor.googleapis.com/v2/search"
        params = {
            "appversion": "browser-r20250225-1",
            "prettyPrint": "false",
            "key": "AIzaSyC-P6_qz3FzCoXGLk6tgitZo4jEJ5mLzD8",
            "client_key": "tenor_web",
            "locale": "en",
            "anon_id": "",
            "q": query,
            "limit": "50",
            "contentfilter": "low",
            "media_filter": "gif,gif_transparent,mediumgif,tinygif,"
                            "tinygif_transparent,webp,webp_transparent,"
                            "tinywebp,tinywebp_transparent,tinymp4,mp4,webm,"
                            "originalgif,gifpreview",
            "fields": "next,results.id,results.media_formats,results.title,"
                      "results.h1_title,results.long_title,results.itemurl,"
                      "results.url,results.created,results.user,"
                      "results.shares,results.embed,results.hasaudio,"
                      "results.policy_status,results.source_id,results.flags,"
                      "results.tags,results.content_rating,results.bg_color,"
                      "results.legacy_info,results.geographic_restriction,"
                      "results.content_description",
            "pos": None,
            "component": "web_desktop",
        }
        headers = {
            "Referer": self.root + "/",
            "Origin" : self.root,
        }

        while True:
            data = self.request(url, params=params, headers=headers).json()

            yield from data["results"]

            params["pos"] = data.get("next")
            if not params["pos"]:
                return

    def metadata(self):
        return False

    def gifs(self):
        return ()


class TenorImageExtractor(TenorExtractor):
    subcategory = "image"
    pattern = BASE_PATTERN + r"view/(?:[^/?#]*-)?(\d+)"
    example = "https://tenor.com/view/SLUG-1234567890"

    def gifs(self):
        url = "{}/view/{}".format(self.root, self.groups[0])
        page = self.request(url).text
        pos = page.index('id="store-cache"')
        data = util.json_loads(text.extract(page, ">", "</script>", pos)[0])
        return (data["gifs"]["byId"].popitem()[1]["results"][0],)


class TenorSearchExtractor(TenorExtractor):
    subcategory = "search"
    directory_fmt = ("{category}", "{search_tags}")
    pattern = BASE_PATTERN + r"search/([^/?#]+)"
    example = "https://tenor.com/search/QUERY"

    def metadata(self):
        query = text.unquote(self.groups[0])
        rest, _, last = query.rpartition("-")
        if last == "gifs":
            query = rest
        self.search_tags = query.replace("-", " ")

        return {"search_tags": self.search_tags}

    def gifs(self):
        return self._search_results(self.search_tags)


class TenorUserExtractor(TenorExtractor):
    subcategory = "user"
    directory_fmt = ("{category}", "@{user[username]}")
    pattern = BASE_PATTERN + r"(?:users|official)/([^/?#]+)"
    example = "https://tenor.com/users/USER"

    def gifs(self):
        return self._search_results("@" + self.groups[0])
