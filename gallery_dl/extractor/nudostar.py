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
    pattern = BASE_PATTERN + r"(/models/([^/?#]+)/?)$"
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

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user_id, self.image_id = match.groups()

    def items(self):
        """Return a list of all (image-url, metadata)-tuples"""
        pagetext = self.request(self.url, notfound=self.subcategory).text
        url_regex = (
            r'<a href=\"https://nudostar\.tv/models/[^&#]+'
            r'\s+<img src=\"([^&\"]+)\"'
        )
        match = re.search(url_regex, pagetext)
        image_url = match.group(1)
        data = text.nameext_from_url(image_url, {"url": image_url})
        data["extension"] = text.ext_from_url(image_url)
        data["filename"] = f"{self.user_id}-{self.image_id}"
        data["user_id"] = self.user_id

        yield Message.Directory, data
        yield Message.Url, image_url, data
