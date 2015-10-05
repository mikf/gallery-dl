# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://www.deviantart.com/"""

from .common import AsynchronousExtractor, Message
from .. import text
import os.path
import re

info = {
    "category": "deviantart",
    "extractor": "DeviantArtExtractor",
    "directory": ["{category}", "{artist}"],
    "filename": "{category}_{index}_{title}.{extension}",
    "pattern": [
        r"(?:https?://)?([^\.]+)\.deviantart\.com/gallery/.*",
    ],
}

class DeviantArtExtractor(AsynchronousExtractor):

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.session.cookies["agegate_state"] = "1"
        self.artist = match.group(1)

    def items(self):
        metadata = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, metadata
        for url, data in self.get_works():
            data.update(metadata)
            yield Message.Url, url, data

    def get_works(self):
        """Yield all work-items for a deviantart-artist"""
        url = "http://{}.deviantart.com/gallery/".format(self.artist)
        params = {"catpath": "/", "offset": 0}
        while True:
            page = self.request(url, params=params).text
            _, pos = text.extract(page, '<div data-dwait-click="GMI.wake"', '')
            while True:
                image_info, pos = text.extract(page, '<a class="thumb', '</a>', pos)
                if not image_info:
                    break
                yield self.get_image_metadata(image_info)
            if pos == 0:
                break
            params["offset"] += 24

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        return {
            "category": info["category"],
            "artist": self.artist,
        }

    def get_image_metadata(self, image):
        """Collect metadata for an image"""
        match = self.extract_data(image, 'title',
            '(.+) by (.+), ([A-Z][a-z]{2} \d+, \d{4}) in')
        if image.startswith(" ismature"):
            # adult image
            url, _ = text.extract(image, 'href="', '"')
            page = self.request(url).text
            _     , pos = text.extract(page, ' class="dev-content-normal "', '')
            url   , pos = text.extract(page, ' src="', '"', pos)
            index , pos = text.extract(page, ' data-embed-id="', '"', pos)
            width , pos = text.extract(page, ' width="', '"', pos)
            height, pos = text.extract(page, ' height="', '"', pos)
        else:
            # normal image
            index = self.extract_data(image, 'href', '[^"]+-(\d+)').group(1)
            url, pos = text.extract(image, ' data-super-full-img="', '"', match.end())
            if url:
                width , pos = text.extract(image, ' data-super-full-width="', '"', pos)
                height, pos = text.extract(image, ' data-super-full-height="', '"', pos)
            else:
                url   , pos = text.extract(image, ' data-super-img="', '"', pos)
                width , pos = text.extract(image, ' data-super-width="', '"', pos)
                height, pos = text.extract(image, ' data-super-height="', '"', pos)
        name, ext = os.path.splitext(text.filename_from_url(url))
        return url, {
            "index": index,
            "title": match.group(1),
            "artist": match.group(2),
            "date": match.group(3),
            "width": width,
            "height": height,
            "name": name,
            "extension": ext[1:],
        }

    @staticmethod
    def extract_data(txt, attr, pattern):
        txt, _ = text.extract(txt, ' %s="' % attr, '"')
        return re.match(pattern, txt)
