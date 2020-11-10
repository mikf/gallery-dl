# -*- coding: utf-8 -*-

# Copyright 2017-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.xvideos.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text
import json


class XvideosBase():
    """Base class for xvideos extractors"""
    category = "xvideos"
    root = "https://www.xvideos.com"


class XvideosGalleryExtractor(XvideosBase, GalleryExtractor):
    """Extractor for user profile galleries on xvideos.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user[name]}",
                     "{gallery[id]} {gallery[title]}")
    filename_fmt = "{category}_{gallery[id]}_{num:>03}.{extension}"
    archive_fmt = "{gallery[id]}_{num}"
    pattern = (r"(?:https?://)?(?:www\.)?xvideos\.com"
               r"/(?:profiles|amateur-channels|model-channels)"
               r"/([^/?#]+)/photos/(\d+)")
    test = (
        ("https://www.xvideos.com/profiles/pervertedcouple/photos/751031", {
            "url": "cb4657a37eea5ab6b1d333491cee7eeb529b0645",
            "keyword": {
                "gallery": {
                    "id"   : 751031,
                    "title": "Random Stuff",
                    "tags" : list,
                },
                "user": {
                    "id"         : 20245371,
                    "name"       : "pervertedcouple",
                    "display"    : "Pervertedcouple",
                    "sex"        : "Woman",
                    "description": str,
                },
            },
        }),
        ("https://www.xvideos.com/amateur-channels/pervertedcouple/photos/12"),
        ("https://www.xvideos.com/model-channels/pervertedcouple/photos/12"),
    )

    def __init__(self, match):
        self.user, self.gallery_id = match.groups()
        url = "{}/profiles/{}/photos/{}".format(
            self.root, self.user, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)
        title = extr('"title":"', '"')
        user = {
            "id"     : text.parse_int(extr('"id_user":', ',')),
            "display": extr('"display":"', '"'),
            "sex"    : extr('"sex":"', '"'),
            "name"   : self.user,
        }
        user["description"] = extr(
            '<small class="mobile-hide">', '</small>').strip()
        tags = extr('<em>Tagged:</em>', '<').strip()

        return {
            "user": user,
            "gallery": {
                "id"   : text.parse_int(self.gallery_id),
                "title": text.unescape(title),
                "tags" : text.unescape(tags).split(", ") if tags else [],
            },
        }

    @staticmethod
    def images(page):
        """Return a list of all image urls for this gallery"""
        return [
            (url, None)
            for url in text.extract_iter(
                page, '<a class="embed-responsive-item" href="', '"')
        ]


class XvideosUserExtractor(XvideosBase, Extractor):
    """Extractor for user profiles on xvideos.com"""
    subcategory = "user"
    categorytransfer = True
    pattern = (r"(?:https?://)?(?:www\.)?xvideos\.com"
               r"/profiles/([^/?#]+)/?(?:#.*)?$")
    test = (
        ("https://www.xvideos.com/profiles/pervertedcouple", {
            "url": "a413f3e60d6d3a2de79bd44fa3b7a9c03db4336e",
            "keyword": "335a3304941ff2e666c0201e9122819b61b34adb",
        }),
        ("https://www.xvideos.com/profiles/pervertedcouple#_tabPhotos"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)

    def items(self):
        url = "{}/profiles/{}".format(self.root, self.user)
        page = self.request(url, notfound=self.subcategory).text
        data = json.loads(text.extract(
            page, "xv.conf=", ";</script>")[0])["data"]

        if not isinstance(data["galleries"], dict):
            return
        if "0" in data["galleries"]:
            del data["galleries"]["0"]

        galleries = [
            {
                "id"   : text.parse_int(gid),
                "title": text.unescape(gdata["title"]),
                "count": gdata["nb_pics"],
                "_extractor": XvideosGalleryExtractor,
            }
            for gid, gdata in data["galleries"].items()
        ]
        galleries.sort(key=lambda x: x["id"])

        yield Message.Version, 1
        for gallery in galleries:
            url = "https://www.xvideos.com/profiles/{}/photos/{}".format(
                self.user, gallery["id"])
            yield Message.Queue, url, gallery
