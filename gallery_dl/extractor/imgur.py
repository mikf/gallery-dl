# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from albums at https://imgur.com/"""

from .common import Extractor, Message
from .. import text, exception


class ImgurAlbumExtractor(Extractor):
    """Extractor for image albums from imgur.com"""
    category = "imgur"
    subcategory = "album"
    directory_fmt = ["{category}", "{album-key} - {title}"]
    filename_fmt = "{category}_{album-key}_{num:>03}_{hash}{ext}"
    pattern = [r"(?:https?://)?(?:m\.|www\.)?imgur\.com/"
               r"(?:a|gallery)/([^/?&#]+)"]
    test = [
        ("https://imgur.com/a/TcBmP", {
            "url": "ce3552f550a5b5316bd9c7ae02e21e39f30c0563",
            "keyword": "21723f47bf4a42599d39fbf29c5f79323d420898",
        }),
        ("https://imgur.com/a/TcBmQ", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.album = match.group(1)

    def items(self):
        imgs = self.get_images()
        data = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, data
        for num, image in enumerate(imgs, 1):
            image["num"] = num
            image["extension"] = image["ext"][1:]
            image.update(data)
            url = "https://i.imgur.com/" + image["hash"] + image["ext"]
            yield Message.Url, url, image

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        page = self.request("https://imgur.com/a/" + self.album).text
        data = text.extract_all(page, (
            ('title', '<meta property="og:title" content="', '"'),
            ('count', '"num_images":"', '"'),
        ), values={"album-key": self.album})[0]
        data["title"] = text.unescape(data["title"])
        return data

    def get_images(self):
        """Return a list of all images in this album"""
        url = ("https://imgur.com/ajaxalbums/getimages/" +
               self.album + "/hit.json")
        data = self.request(url).json()["data"]
        if not data:
            raise exception.NotFoundError("album")
        return data["images"]
