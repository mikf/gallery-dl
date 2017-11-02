# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.xvideos.com"""

from .common import Extractor, Message
from .. import text, util, exception


class XvideosGalleryExtractor(Extractor):
    """Extractor for user profile galleries from xvideos.com"""
    category = "xvideos"
    subcategory = "gallery"
    directory_fmt = ["{category}", "{user[name]}", "{title}"]
    filename_fmt = "{category}_{gallery_id}_{num:>03}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?xvideos\.com"
               r"/profiles/([^/?&#]+)/photos/(\d+)"]
    test = [
        (("https://www.xvideos.com/profiles"
          "/pervertedcouple/photos/751031/random_stuff"), {
            "url": "4f0d992e5dc39def2c3ac8e099d17bf09e76e3c7",
            "keyword": "71d64a9b2ba7015850d3aed3fbcae1e7e0481515",
        }),
        ("https://www.xvideos.com/profiles/pervertedcouple/photos/751032/", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.user, self.gid = match.groups()
        self.url = match.group(0)

    def items(self):
        response = self.request(self.url, fatal=False)
        if response.status_code in (403, 404):
            raise exception.NotFoundError("gallery")
        page = response.text
        data = self.get_metadata(page)
        imgs = self.get_images(page)
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for url in imgs:
            data["num"] = util.safe_int(url.rsplit("_", 2)[1])
            data["extension"] = url.rpartition(".")[2]
            yield Message.Url, url, data

    def get_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = text.extract_all(page, (
            ("userid" , '"id_user":', ','),
            ("display", '"display":"', '"'),
            ("title"  , '"title":"', '"'),
            ("descr"  , '<small>', '</small>'),
            ("tags"   , '<em>Tagged:</em>', '<'),
        ))[0]

        return {
            "user": {
                "id": util.safe_int(data["userid"]),
                "name": self.user,
                "display": data["display"],
                "description": text.remove_html(data["descr"]).strip(),
            },
            "tags": text.unescape(data["tags"] or "").strip().split(", "),
            "title": text.unescape(data["title"]),
            "gallery_id": util.safe_int(self.gid),
        }

    @staticmethod
    def get_images(page):
        """Return a list of all image urls for this gallery"""
        return list(text.extract_iter(
            page, '<a class="embed-responsive-item" href="', '"'))
