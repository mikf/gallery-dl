# -*- coding: utf-8 -*-

# Copyright 2017-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.xvideos.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util

BASE_PATTERN = (r"(?:https?://)?(?:www\.)?xvideos\.com"
                r"/(?:profiles|(?:amateur-|model-)?channels)")


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
    pattern = BASE_PATTERN + r"/([^/?#]+)/photos/(\d+)"
    example = "https://www.xvideos.com/profiles/USER/photos/12345"

    def __init__(self, match):
        self.user, self.gallery_id = match.groups()
        url = "{}/profiles/{}/photos/{}".format(
            self.root, self.user, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)
        user = {
            "id"     : text.parse_int(extr('"id_user":', ',')),
            "display": extr('"display":"', '"'),
            "sex"    : extr('"sex":"', '"'),
            "name"   : self.user,
        }
        title = extr('"title":"', '"')
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

    def images(self, page):
        results = [
            (url, None)
            for url in text.extract_iter(
                page, '<a class="embed-responsive-item" href="', '"')
        ]

        if not results:
            return

        while len(results) % 500 == 0:
            path = text.rextract(page, ' href="', '"', page.find(">Next</"))[0]
            if not path:
                break
            page = self.request(self.root + path).text
            results.extend(
                (url, None)
                for url in text.extract_iter(
                    page, '<a class="embed-responsive-item" href="', '"')
            )

        return results


class XvideosUserExtractor(XvideosBase, Extractor):
    """Extractor for user profiles on xvideos.com"""
    subcategory = "user"
    categorytransfer = True
    pattern = BASE_PATTERN + r"/([^/?#]+)/?(?:#.*)?$"
    example = "https://www.xvideos.com/profiles/USER"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)

    def items(self):
        url = "{}/profiles/{}".format(self.root, self.user)
        page = self.request(url, notfound=self.subcategory).text
        data = util.json_loads(text.extr(
            page, "xv.conf=", ";</script>"))["data"]

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

        for gallery in galleries:
            url = "https://www.xvideos.com/profiles/{}/photos/{}".format(
                self.user, gallery["id"])
            yield Message.Queue, url, gallery
