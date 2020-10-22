# -*- coding: utf-8 -*-

# Copyright 2020 Leonardo Taccari
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://speakerdeck.com/"""

from .common import Extractor, Message
from .. import text


class SpeakerdeckPresentationExtractor(Extractor):
    """Extractor for images from a presentation on speakerdeck.com"""
    category = "speakerdeck"
    subcategory = "presentation"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{presentation}-{num:>02}.{extension}"
    archive_fmt = "{presentation}_{num}"
    pattern = (r"(?:https?://)?(?:www\.)?speakerdeck\.com"
               r"/([^/?#]+)/([^/?#]+)")
    test = (
        (("https://speakerdeck.com/speakerdeck/introduction-to-speakerdeck"), {
            "pattern": r"https://files.speakerdeck.com/presentations/"
                       r"50021f75cf1db900020005e7/slide_\d+.jpg",
            "content": "75c7abf0969b0bcab23e0da9712c95ee5113db3a",
            "count": 6,
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user, self.presentation = match.groups()
        self.presentation_id = None

    def items(self):
        data = self.get_job_metadata()
        imgs = self.get_image_urls()
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], url in enumerate(imgs, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        url = "https://speakerdeck.com/oembed.json"
        params = {
            "url": "https://speakerdeck.com/" + self.user +
                   "/" + self.presentation,
        }

        data = self.request(url, params=params).json()

        self.presentation_id, pos = \
            text.extract(data["html"], 'src="//speakerdeck.com/player/', '"')

        return {
            "user": self.user,
            "presentation": self.presentation,
            "presentation_id": self.presentation_id,
            "title": data["title"],
            "author": data["author_name"],
        }

    def get_image_urls(self):
        """Extract and return a list of all image-urls"""
        page = self.request("https://speakerdeck.com/player/" +
                            self.presentation_id).text
        return list(text.extract_iter(page, 'js-sd-slide" data-url="', '"'))
