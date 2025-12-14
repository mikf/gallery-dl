# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nudostar.tv/"""

from .common import GalleryExtractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:[a-z]{2}.)?nudostar\.tv"


class NudostarExtractor(GalleryExtractor):
    """Base class for NudoStar extractors"""
    category = "nudostar"
    root = "https://nudostar.tv"


class NudostarModelExtractor(NudostarExtractor):
    """Extractor for NudoStar models"""
    subcategory = "model"
    pattern = rf"{BASE_PATTERN}(/models/([^/?#]+)/?)$"
    example = "https://nudostar.tv/models/MODEL/"

    def metadata(self, page):
        names = text.extr(page, "<title>", "<").rpartition(
            " Nude ")[0].split(" / ")
        slug = self.groups[1]

        return {
            "gallery_id" : slug,
            "model_slug" : slug,
            "model_names": names,
            "model"      : names[0],
            "title"      : "",
        }

    def images(self, page):
        path = text.extr(page, '" src="https://nudostar.tv', '"')
        path, cnt, end = path.rsplit("_", 2)

        base = f"{self.root}{path}_"
        ext = "." + end.rpartition(".")[2]

        return [
            (f"{base}{i:04}{ext}", None)
            for i in range(1, int(cnt)+1)
        ]


class NudostarImageExtractor(NudostarExtractor):
    """Extractor for NudoStar images"""
    subcategory = "image"
    pattern = rf"{BASE_PATTERN}(/models/([^/?#]+)/(\d+)/)"
    example = "https://nudostar.tv/models/MODEL/123/"

    def items(self):
        page = self.request(self.page_url, notfound=self.subcategory).text

        img_url = text.extract(
            page, 'src="', '"', page.index('class="headline"'))[0]

        data = NudostarModelExtractor.metadata(self, page)
        data = text.nameext_from_url(img_url, data)
        data["num"] = text.parse_int(self.groups[2])
        data["url"] = img_url

        yield Message.Directory, "", data
        yield Message.Url, img_url, data
