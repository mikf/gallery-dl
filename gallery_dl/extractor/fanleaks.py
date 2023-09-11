# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fanleaks.club/"""

from .common import Extractor, Message
from .. import text


class FanleaksExtractor(Extractor):
    """Base class for Fanleaks extractors"""
    category = "fanleaks"
    directory_fmt = ("{category}", "{model}")
    filename_fmt = "{model_id}_{id}.{extension}"
    archive_fmt = "{model_id}_{id}"
    root = "https://fanleaks.club"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.model_id = match.group(1)

    def extract_post(self, url):
        extr = text.extract_from(self.request(url, notfound="post").text)
        data = {
            "model_id": self.model_id,
            "model"   : text.unescape(extr('text-lg">', "</a>")),
            "id"      : text.parse_int(self.id),
            "type"    : extr('type="', '"')[:5] or "photo",
        }
        url = extr('src="', '"')
        yield Message.Directory, data
        yield Message.Url, url, text.nameext_from_url(url, data)


class FanleaksPostExtractor(FanleaksExtractor):
    """Extractor for individual posts on fanleaks.club"""
    subcategory = "post"
    pattern = r"(?:https?://)?(?:www\.)?fanleaks\.club/([^/?#]+)/(\d+)"
    example = "https://fanleaks.club/MODEL/12345"

    def __init__(self, match):
        FanleaksExtractor.__init__(self, match)
        self.id = match.group(2)

    def items(self):
        url = "{}/{}/{}".format(self.root, self.model_id, self.id)
        return self.extract_post(url)


class FanleaksModelExtractor(FanleaksExtractor):
    """Extractor for all posts from a fanleaks model"""
    subcategory = "model"
    pattern = (r"(?:https?://)?(?:www\.)?fanleaks\.club"
               r"/(?!latest/?$)([^/?#]+)/?$")
    example = "https://fanleaks.club/MODEL"

    def items(self):
        page_num = 1
        page = self.request(
            self.root + "/" + self.model_id, notfound="model").text
        data = {
            "model_id": self.model_id,
            "model"   : text.unescape(text.extr(page, 'mt-4">', "</h1>")),
            "type"    : "photo",
        }
        page_url = text.extr(page, "url: '", "'")
        while True:
            page = self.request("{}{}".format(page_url, page_num)).text
            if not page:
                return

            for item in text.extract_iter(page, '<a href="/', "</a>"):
                self.id = id = text.extr(item, "/", '"')
                if "/icon-play.svg" in item:
                    url = "{}/{}/{}".format(self.root, self.model_id, id)
                    yield from self.extract_post(url)
                    continue

                data["id"] = text.parse_int(id)
                url = text.extr(item, 'src="', '"').replace(
                    "/thumbs/", "/", 1)
                yield Message.Directory, data
                yield Message.Url, url, text.nameext_from_url(url, data)
            page_num += 1
