# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from albums at https://imgur.com/"""

from .common import Extractor, Message
from .. import text
from urllib.parse import urljoin
import os.path

class ImgurAlbumExtractor(Extractor):
    """Extractor for image albums from imgur.com"""
    category = "imgur"
    subcategory = "album"
    directory_fmt = ["{category}", "{album-key} - {title}"]
    filename_fmt = "{category}_{album-key}_{num:>03}_{name}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?imgur\.com/(?:a|gallery)/([^/?&#]+)"]
    test = [("https://imgur.com/a/TcBmP", {
        "url": "ce3552f550a5b5316bd9c7ae02e21e39f30c0563",
        "keyword": "c76bbf86f8f114cdaadab396c0ea4acf47aa44eb",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.album = match.group(1)

    def items(self):
        data = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, data
        for num, url in enumerate(self.get_image_urls(), 1):
            name, ext = os.path.splitext(url[20:])
            data["num"] = num
            data["name"] = name
            data["extension"] = ext[1:]
            yield Message.Url, url, data

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        page = self.request("https://imgur.com/a/" + self.album).text
        data = text.extract_all(page, (
            ('title', '<meta property="og:title" content="', '"'),
            ('count', '"num_images":"', '"'),
            ('date' , '"datetime":"', ' '),
            ('time' , '', '"'),
        ), values={"album-key": self.album})[0]
        data["title"] = text.unescape(data["title"])
        return data

    def get_image_urls(self):
        """Yield urls of all images in this album"""
        num = 0
        while True:
            url = "https://imgur.com/a/{}/all/page/{}?scrolled".format(self.album, num)
            page = self.request(url).text
            pos = begin = text.extract(page, '<div class="posts">', '')[1]
            while True:
                url, pos = text.extract(page, '<a href="', '"', pos)
                if not url:
                    break
                yield urljoin("https:", url)
            if pos == begin:
                return
            num += 1
