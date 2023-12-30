# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for http://www.poringa.net/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
import itertools

BASE_PATTERN = r"(?:https?://)?(?:www\.)?poringa\.net"


class PoringaExtractor(Extractor):
    category = "poringa"
    directory_fmt = ("{category}", "{user}", "{post_id}")
    filename_fmt = "{post_id}_{title}_{num:>03}_{filename}.{extension}"
    archive_fmt = "{post_id}_{num}"
    root = "http://www.poringa.net"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.item = match.group(1)
        self.__cookies = True

    def items(self):
        for post_id in self.posts():
            url = "{}/posts/imagenes/{}".format(self.root, post_id)

            try:
                response = self.request(url)
            except exception.HttpError as exc:
                self.log.warning(
                    "Unable to fetch posts for '%s' (%s)", post_id, exc)
                continue

            if "/registro-login?" in response.url:
                self.log.warning("Private post '%s'", post_id)
                continue

            page = response.text
            title, pos = text.extract(
                page, 'property="og:title" content="', '"')

            try:
                pos = page.index('<div class="main-info', pos)
                user, pos = text.extract(
                    page, 'href="http://www.poringa.net/', '"', pos)
            except ValueError:
                user = None

            if not user:
                user = "poringa"

            data = {
                "post_id"      : post_id,
                "title"        : text.unescape(title),
                "user"         : text.unquote(user),
                "_http_headers": {"Referer": url},
            }

            main_post = text.extr(
                page, 'property="dc:content" role="main">', '</div>')
            urls = list(text.extract_iter(
                main_post, '<img class="imagen" border="0" src="', '"'))
            data["count"] = len(urls)

            yield Message.Directory, data
            for data["num"], url in enumerate(urls, 1):
                yield Message.Url, url, text.nameext_from_url(url, data)

    def posts(self):
        return ()

    def request(self, url, **kwargs):
        if self.__cookies:
            self.__cookies = False
            self.cookies_update(_cookie_cache())

        for _ in range(5):
            response = Extractor.request(self, url, **kwargs)
            if response.cookies:
                _cookie_cache.update("", response.cookies)
            if response.content.find(
                    b"<title>Please wait a few moments</title>", 0, 600) < 0:
                return response
            self.sleep(5.0, "check")

    def _pagination(self, url, params):
        for params["p"] in itertools.count(1):
            page = self.request(url, params=params).text

            posts_ids = PoringaPostExtractor.pattern.findall(page)
            posts_ids = list(dict.fromkeys(posts_ids))
            yield from posts_ids

            if len(posts_ids) < 19:
                return


class PoringaPostExtractor(PoringaExtractor):
    """Extractor for posts on poringa.net"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/posts/imagenes/(\d+)"
    example = "http://www.poringa.net/posts/imagenes/12345/TITLE.html"

    def posts(self):
        return (self.item,)


class PoringaUserExtractor(PoringaExtractor):
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(\w+)$"
    example = "http://www.poringa.net/USER"

    def posts(self):
        url = self.root + "/buscar/"
        params = {"q": self.item}
        return self._pagination(url, params)


class PoringaSearchExtractor(PoringaExtractor):
    subcategory = "search"
    pattern = BASE_PATTERN + r"/buscar/\?&?q=([^&#]+)"
    example = "http://www.poringa.net/buscar/?q=QUERY"

    def posts(self):
        url = self.root + "/buscar/"
        params = {"q": self.item}
        return self._pagination(url, params)


@cache()
def _cookie_cache():
    return ()
