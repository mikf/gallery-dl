# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fanleaks.club/"""

from .common import Extractor, Message
from .. import text, exception


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
    """Extractor for individual posts on fanleak.club"""
    subcategory = "post"
    pattern = r"(?:https?://)?(?:www\.)?fanleaks\.club/([^/?#]+)/(\d+)"
    test = (
        ("https://fanleaks.club/selti/880", {
            "pattern": (r"https://fanleaks\.club//models"
                        r"/selti/images/selti_0880\.jpg"),
            "keyword": {
                "model_id": "selti",
                "model"   : "Selti",
                "id"      : 880,
                "type"    : "photo",
            },
        }),
        ("https://fanleaks.club/daisy-keech/1038", {
            "pattern": (r"https://fanleaks\.club//models"
                        r"/daisy-keech/videos/daisy-keech_1038\.mp4"),
            "keyword": {
                "model_id": "daisy-keech",
                "model"   : "Daisy Keech",
                "id"      : 1038,
                "type"    : "video",
            },
        }),
        ("https://fanleaks.club/hannahowo/000", {
            "exception": exception.NotFoundError,
        }),
    )

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
    test = (
        ("https://fanleaks.club/hannahowo", {
            "pattern": (r"https://fanleaks\.club//models"
                        r"/hannahowo/(images|videos)/hannahowo_\d+\.\w+"),
            "range"  : "1-100",
            "count"  : 100,
        }),
        ("https://fanleaks.club/belle-delphine", {
            "pattern": (r"https://fanleaks\.club//models"
                        r"/belle-delphine/(images|videos)"
                        r"/belle-delphine_\d+\.\w+"),
            "range"  : "1-100",
            "count"  : 100,
        }),
        ("https://fanleaks.club/daisy-keech"),
    )

    def items(self):
        page_num = 1
        page = self.request(
            self.root + "/" + self.model_id, notfound="model").text
        data = {
            "model_id": self.model_id,
            "model"   : text.unescape(
                text.extr(page, 'mt-4">', "</h1>")),
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
