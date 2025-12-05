# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://arca.live/"""

from .common import Extractor, Message
from .. import text, util, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?arca\.live"


class ArcaliveExtractor(Extractor):
    """Base class for Arca.live extractors"""
    category = "arcalive"
    root = "https://arca.live"
    useragent = "net.umanle.arca.android.playstore/0.9.75"
    request_interval = (0.5, 1.5)

    def _init(self):
        self.api = ArcaliveAPI(self)

    def items(self):
        for article in self.articles():
            article["_extractor"] = ArcalivePostExtractor
            board = self.board or article.get("boardSlug") or "breaking"
            url = f"{self.root}/b/{board}/{article['id']}"
            yield Message.Queue, url, article


class ArcalivePostExtractor(ArcaliveExtractor):
    """Extractor for an arca.live post"""
    subcategory = "post"
    directory_fmt = ("{category}", "{boardSlug}")
    filename_fmt = "{id}_{num}{title:? //[b:230]}.{extension}"
    archive_fmt = "{id}_{num}"
    pattern = rf"{BASE_PATTERN}/b/(?:\w+)/(\d+)"
    example = "https://arca.live/b/breaking/123456789"

    def items(self):
        self.emoticons = self.config("emoticons", False)
        self.gifs = gifs = self.config("gifs", True)
        if gifs:
            self.gifs_fallback = (gifs != "check")

        post = self.api.post(self.groups[0])
        files = self._extract_files(post)

        post["count"] = len(files)
        post["date"] = self.parse_datetime_iso(post["createdAt"][:19])
        post["post_url"] = post_url = \
            f"{self.root}/b/{post['boardSlug']}/{post['id']}"
        post["_http_headers"] = {"Referer": post_url + "?p=1"}

        yield Message.Directory, "", post
        for post["num"], file in enumerate(files, 1):
            post.update(file)
            url = file["url"]
            yield Message.Url, url, text.nameext_from_url(url, post)

    def _extract_files(self, post):
        files = []

        for video, media in text.re(r"<(?:img|vide(o)) ([^>]+)").findall(
                post["content"]):
            if not self.emoticons and 'class="arca-emoticon"' in media:
                continue

            src = (text.extr(media, 'data-originalurl="', '"') or
                   text.extr(media, 'src="', '"'))
            if not src:
                continue

            src, _, query = text.unescape(src).partition("?")
            if src[0] == "/":
                if src[1] == "/":
                    url = "https:" + src.replace(
                        "//ac-p.namu", "//ac-o.namu", 1)
                else:
                    url = self.root + src
            else:
                url = src

            fallback = ()
            query = f"?type=orig&{query}"
            if orig := text.extr(media, 'data-orig="', '"'):
                path, _, ext = url.rpartition(".")
                if ext != orig:
                    fallback = (url + query,)
                    url = path + "." + orig
            elif video and self.gifs:
                url_gif = url.rpartition(".")[0] + ".gif"
                if self.gifs_fallback:
                    fallback = (url + query,)
                    url = url_gif
                else:
                    response = self.request(
                        url_gif + query, method="HEAD", fatal=False)
                    if response.status_code < 400:
                        fallback = (url + query,)
                        url = url_gif

            files.append({
                "url"   : url + query,
                "width" : text.parse_int(text.extr(media, 'width="', '"')),
                "height": text.parse_int(text.extr(media, 'height="', '"')),
                "_fallback": fallback,
            })

        return files


class ArcaliveBoardExtractor(ArcaliveExtractor):
    """Extractor for an arca.live board's posts"""
    subcategory = "board"
    pattern = rf"{BASE_PATTERN}/b/([^/?#]+)/?(?:\?([^#]+))?$"
    example = "https://arca.live/b/breaking"

    def articles(self):
        self.board, query = self.groups
        params = text.parse_query(query)
        return self.api.board(self.board, params)


class ArcaliveUserExtractor(ArcaliveExtractor):
    """Extractor for an arca.live users's posts"""
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}/u/@([^/?#]+)/?(?:\?([^#]+))?$"
    example = "https://arca.live/u/@USER"

    def articles(self):
        self.board = None
        user, query = self.groups
        params = text.parse_query(query)
        return self.api.user_posts(text.unquote(user), params)


class ArcaliveAPI():

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log
        self.root = extractor.root + "/api/app"

        extractor.session.headers["X-Device-Token"] = util.generate_token(64)

    def board(self, board_slug, params):
        endpoint = "/list/channel/" + board_slug
        return self._pagination(endpoint, params, "articles")

    def post(self, post_id):
        endpoint = "/view/article/breaking/" + str(post_id)
        return self._call(endpoint)

    def user_posts(self, username, params):
        endpoint = "/list/channel/breaking"
        params["target"] = "nickname"
        params["keyword"] = username
        return self._pagination(endpoint, params, "articles")

    def _call(self, endpoint, params=None):
        url = self.root + endpoint
        response = self.extractor.request(url, params=params)

        data = response.json()
        if response.status_code == 200:
            return data

        self.log.debug("Server response: %s", data)
        msg = f": {msg}" if (msg := data.get("message")) else ""
        raise exception.AbortExtraction(f"API request failed{msg}")

    def _pagination(self, endpoint, params, key):
        while True:
            data = self._call(endpoint, params)

            posts = data.get(key)
            if not posts:
                break
            yield from posts

            params.update(data["next"])
