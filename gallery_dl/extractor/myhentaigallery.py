# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://myhentaigallery.com/"""

from .common import GalleryExtractor
from .. import text, exception


class MyhentaigalleryGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from myhentaigallery.com"""
    category = "myhentaigallery"
    directory_fmt = ("{category}", "{gallery_id} {artist:?[/] /J, }{title}")
    pattern = (r"(?:https?://)?myhentaigallery\.com"
               r"/gallery/(?:thumbnails|show)/(\d+)")
    test = (
        ("https://myhentaigallery.com/gallery/thumbnails/16247", {
            "pattern": r"https://images.myhentaicomics\.com/imagesgallery"
                       r"/images/[^/]+/original/\d+\.jpg",
            "keyword": {
                "artist"    : list,
                "count"     : 11,
                "gallery_id": 16247,
                "group"     : list,
                "parodies"  : list,
                "tags"      : ["Giantess"],
                "title"     : "Attack Of The 50ft Woman 1",
            },
        }),
        ("https://myhentaigallery.com/gallery/show/16247/1"),
    )
    root = "https://myhentaigallery.com"

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = "{}/gallery/thumbnails/{}".format(self.root, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)
        self.session.headers["Referer"] = url

    def metadata(self, page):
        extr = text.extract_from(page)
        split = text.split_html

        title = extr('<div class="comic-description">\n<h1>', '</h1>')
        if not title:
            raise exception.NotFoundError("gallery")

        return {
            "title"     : text.unescape(title),
            "gallery_id": text.parse_int(self.gallery_id),
            "tags"      : split(extr('<div>\nCategories:', '</div>')),
            "artist"    : split(extr('<div>\nArtists:'   , '</div>')),
            "group"     : split(extr('<div>\nGroups:'    , '</div>')),
            "parodies"  : split(extr('<div>\nParodies:'  , '</div>')),
        }

    def images(self, page):
        return [
            (text.unescape(text.extract(url, 'src="', '"')[0]).replace(
                "/thumbnail/", "/original/"), None)
            for url in text.extract_iter(page, 'class="comic-thumb"', '</div>')
        ]
