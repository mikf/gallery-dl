# -*- coding: utf-8 -*-

# Copyright 2020 Leonardo Taccari
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://speakerdeck.com/"""

from .common import GalleryExtractor
from .. import text


class SpeakerdeckPresentationExtractor(GalleryExtractor):
    """Extractor for images from a presentation on speakerdeck.com"""
    category = "speakerdeck"
    subcategory = "presentation"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{presentation}-{num:>02}.{extension}"
    archive_fmt = "{presentation}_{num}"
    root = "https://speakerdeck.com"
    pattern = r"(?:https?://)?(?:www\.)?speakerdeck\.com/([^/?#]+)/([^/?#]+)"
    example = "https://speakerdeck.com/USER/PRESENTATION"

    def metadata(self, _):
        user, presentation = self.groups

        url = self.root + "/oembed.json"
        params = {
            "url": f"{self.root}/{user}/{presentation}",
        }
        data = self.request_json(url, params=params)

        self.presentation_id = text.extr(
            data["html"], 'src="//speakerdeck.com/player/', '"')

        return {
            "user": user,
            "presentation": presentation,
            "presentation_id": self.presentation_id,
            "title": data["title"],
            "author": data["author_name"],
        }

    def images(self, _):
        url = f"{self.root}/player/{self.presentation_id}"
        page = self.request(url).text
        page = text.re(r"\s+").sub(" ", page)
        return [
            (url, None)
            for url in text.extract_iter(page, 'js-sd-slide" data-url="', '"')
        ]
