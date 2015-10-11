# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from albums at https://imgur.com/"""

from .common import Extractor, Message
from .. import text
import os.path

info = {
    "category": "imgur",
    "extractor": "ImgurExtractor",
    "directory": ["{category}", "{album-key} - {title}"],
    "filename": "{category}_{album-key}_{num:>03}_{name}.{extension}",
    "pattern": [
        r"(?:https?://)?(?:www\.)?imgur\.com/(?:a|gallery)/([^/?&#]+)",
    ],
}

class ImgurExtractor(Extractor):

    def __init__(self, match):
        Extractor.__init__(self)
        self.album = match.group(1)

    def items(self):
        page = self.request("https://imgur.com/a/" + self.album).text
        data = self.get_job_metadata(page)
        images = self.get_images(page)
        data["count"] = len(images)
        yield Message.Version, 1
        yield Message.Directory, data
        for image in images:
            data.update(image)
            yield Message.Url, image["url"], data

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        _    , pos = text.extract(page, '<h1 ', '>')
        title, pos = text.extract(page, '', '</h1>', pos)
        return {
            "category": info["category"],
            "album-key": self.album,
            "title": title,
            # "date": ...,
        }

    def get_images(self, page):
        """Build a list of all images in this album"""
        images = []
        pos = 0
        num = 0
        while True:
            url   , pos = text.extract(page, 'property="og:image"        content="', '"', pos)
            if not url:
                return images
            width , pos = text.extract(page, 'property="og:image:width"  content="', '"', pos)
            height, pos = text.extract(page, 'property="og:image:height" content="', '"', pos)
            name = os.path.splitext(text.filename_from_url(url))
            num += 1
            images.append({
                "url": "https" + url[4:],
                "width": width,
                "height": height,
                "name": name[0],
                "extension": name[1][1:],
                "num": num,
            })
