# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://nijie.info/"""

from .common import AsynchronousExtractor
from .common import Message
from .common import filename_from_url
import re

info = {
    "category": "nijie",
    "extractor": "NijieExtractor",
    "directory": ["{category}", "{artist-id}"],
    "filename": "{category}_{artist-id}_{image-id}_p{index:>02}.{extension}",
    "pattern": [
        r"(?:https?://)?(?:www\.)?nijie\.info/members(?:_illust)?\.php\?id=(\d+)",
    ],
}

class NijieExtractor(AsynchronousExtractor):

    popup_url = "https://nijie.info/view_popup.php?id="

    def __init__(self, match, config):
        AsynchronousExtractor.__init__(self, config)
        self.artist_id = match.group(1)
        self.artist_url = (
            "https://nijie.info/members_illust.php?id="
            + self.artist_id
        )
        self.session.headers["Referer"] = self.artist_url
        self.session.cookies["R18"] = "1"
        self.session.cookies["nijie_referer"] = "nijie.info"
        self.session.cookies.update(config["nijie-cookies"])

    def items(self):
        data = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, data
        for image_id in self.get_image_ids():
            for image_url, image_data in self.get_image_data(image_id):
                image_data.update(data)
                yield Message.Url, image_url, image_data

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        return {
            "category": info["category"],
            "artist-id": self.artist_id,
        }

    def get_image_ids(self):
        text = self.request(self.artist_url).text
        regex = r'<a href="/view\.php\?id=(\d+)"'
        return [m.group(1) for m in re.finditer(regex, text)]

    def get_image_data(self, image_id):
        """Get URL and metadata for images specified by 'image_id'"""
        text = self.request(self.popup_url + image_id).text
        matches = re.findall('<img src="([^"]+)"', text)
        for index, url in enumerate(matches):
            yield "https:" + url, {
                "count": len(matches),
                "index": index,
                "image-id": image_id,
                "name" : filename_from_url(url),
                "extension": url[url.rfind(".")+1:],
            }
