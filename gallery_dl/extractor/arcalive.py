# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://arca.live/"""

from .common import Extractor, Message
from .. import text, util, exception


class ArcaliveExtractor(Extractor):
    """Base class for Arca.live extractors"""

    category = "arcalive"
    root = "https://arca.live"

    def _init(self):
        self.api = ArcaliveAPI(self)
        self.session.headers["User-Agent"] = "net.umanle.arca.android.playstore/0.9.75"
        self.session.headers["X-Device-Token"] = util.generate_token(64)


class ArcalivePostExtractor(ArcaliveExtractor):
    """Extractor for an arca.live post"""

    subcategory = "post"
    pattern = r"(?:https?://)?(?:www\.)?arca\.live/b/(?:\w+)/(\d+)"
    example = "https://arca.live/b/breaking/123456789"
    directory_fmt = ("{category}", "{boardSlug}")
    filename_fmt = "{id}_{num}.{extension}"
    archive_fmt = "{id}_{num}"

    def items(self):
        (post_id,) = self.groups
        post = self.api.post(post_id)

        image_urls = self.parse_content(post["content"])

        post["date"] = text.parse_datetime(post["createdAt"])
        post["count"] = len(image_urls)

        yield Message.Directory, post
        for post["num"], url in enumerate(image_urls, 1):
            yield Message.Url, url, text.nameext_from_url(url, post)

    def parse_content(self, content):
        # post["images"] doen't always have all the media
        # therefore, parse the content ourselves
        raise NotImplementedError


class ArcaliveBoardExtractor(ArcaliveExtractor):
    """Extractor for an arca.live board posts"""

    subcategory = "board"
    pattern = r"(?:https?://)?(?:www\.)?arca\.live/b/(\w+)(?:\?([^#]+))?"
    example = "https://arca.live/b/breaking"

    def items(self):
        board_slug, query_str = self.groups
        query = text.parse_query(query_str)
        articles = self.api.board(board_slug, query)

        for article in articles:
            article["_extractor"] = ArcalivePostExtractor
            url = "{}/b/{}/{}".format(self.root, board_slug, article["id"])
            yield Message.Queue, url, article


class ArcaliveAPI:
    def __init__(self, extractor):
        self.extractor = extractor

    def board(self, board_slug, params):
        endpoint = "/api/app/list/channel/" + str(board_slug)
        return self._pagination(endpoint, params, "articles")

    def post(self, post_id):
        endpoint = "/api/app/view/article/breaking/" + str(post_id)
        return self._call(endpoint)

    def _call(self, endpoint, params=None):
        url = self.extractor.root + endpoint
        response = self.extractor.request(url, params=params)
        data = response.json()

        if response.status_code != 200:
            self.extractor.log.debug("Server response: %s", data)
            if data.get("message"):
                raise exception.StopExtraction(
                    "API request failed: %s", data.get("message")
                )
            else:
                raise exception.StopExtraction("API request failed")

        return data

    def _pagination(self, endpoint, params, key):
        while True:
            data = self._call(endpoint, params)
            posts = data[key]
            if not posts:
                break

            yield from posts
            params.update(data["next"])
