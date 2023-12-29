# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://tmohentai.com/"""

from .common import GalleryExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?tmohentai\.com"


class TmohentaiGalleryExtractor(GalleryExtractor):
    category = "tmohentai"
    root = "http://tmohentai.com"
    directory_fmt = ("{category}", "{title} ({gallery_id})")
    pattern = BASE_PATTERN + r"/(?:contents|reader)/(\w+)"
    example = "https://tmohentai.com/contents/12345a67b89c0"

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = "{}/contents/{}".format(self.root, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

    def images(self, page):
        fmt = "https://imgrojo.tmohentai.com/contents/{}/{{:>03}}.webp".format(
            self.gallery_id).format
        cnt = page.count('class="lanzador')
        return [(fmt(i), None) for i in range(0, cnt)]

    def metadata(self, page):
        extr = text.extract_from(page)

        return {
            "gallery_id": self.gallery_id,
            "title"     : text.unescape(extr("<h3>", "<").strip()),
            "artists"   : text.split_html(extr(
                "<label>Artists and Artists Groups</label>", "</ul>")),
            "genres"    : text.split_html(extr(
                "<label>Genders</label>", "</ul>")),
            "tags"      : text.split_html(extr(
                "<label>Tags</label>", "</ul>")),
            "uploader"  : text.remove_html(extr(
                "<label>Uploaded By</label>", "</ul>")),
            "language"  : extr("&nbsp;", "\n"),
        }
