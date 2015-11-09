# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://chan.sankakucomplex.com/"""

from .common import Extractor, Message
from .. import text
import os.path

info = {
    "category": "sankaku",
    "extractor": "SankakuExtractor",
    "directory": ["{category}", "{tags}"],
    "filename": "{category}_{id}_{md5}.{extension}",
    "pattern": [
        r"(?:https?://)?chan\.sankakucomplex\.com/\?tags=([^&]+)",
    ],
}

class SankakuExtractor(Extractor):

    url = "https://chan.sankakucomplex.com/"

    def __init__(self, match):
        Extractor.__init__(self)
        self.tags = text.unquote(match.group(1))
        self.session.headers["User-Agent"] = (
            "Mozilla/5.0 Gecko/20100101 Firefox/40.0"
        )

    def items(self):
        yield Message.Version, 1
        data = self.get_job_metadata()
        yield Message.Directory, data
        for image in self.get_images():
            data.update(image)
            yield Message.Url, image["file-url"], data

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        return {
            "category": info["category"],
            "tags": self.tags,
        }

    def get_images(self):
        image = {}
        params = {
            "tags": self.tags,
            "page": 1,
        }
        while True:
            pos = 0
            count = 0
            page = self.request(self.url, params=params).text
            while True:
                image["id"], pos = text.extract(page,
                    '<span class="thumb blacklisted" id=p', '>', pos)
                if not image["id"]:
                    break
                url , pos = text.extract(page, ' src="//c.sankakucomplex.com/', '"', pos)
                tags, pos = text.extract(page, ' title="', '"', pos)
                self.get_image_metadata(image, url)
                count += 1
                yield image
            if count < 20:
                return
            params["page"] += 1

    @staticmethod
    def get_image_metadata(image, url):
        image["file-url"] = "https://cs.sankakucomplex.com/data/" + url[13:]
        filename = text.filename_from_url(url)
        name, ext = os.path.splitext(filename)
        image["name"] = image["md5"] = name
        image["extension"] = ext[1:]
