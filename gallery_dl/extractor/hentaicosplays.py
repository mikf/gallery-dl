# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentai-cosplay-xxx.com/
(also works for hentai-img-xxx.com and porn-image.com)"""

from .common import BaseExtractor, GalleryExtractor
from .. import text


class HentaicosplaysExtractor(BaseExtractor):
    basecategory = "hentaicosplays"


BASE_PATTERN = HentaicosplaysExtractor.update({
    "hentaicosplay": {
        "root": "https://hentai-cosplay-xxx.com",
        "pattern": r"(?:\w\w\.)?hentai-cosplays?(?:-xxx)?\.com",
    },
    "hentaiimg": {
        "root": "https://hentai-img-xxx.com",
        "pattern": r"(?:\w\w\.)?hentai-img(?:-xxx)?\.com",
    },
    "pornimage": {
        "root": "https://porn-image.com",
        "pattern": r"(?:\w\w\.)?porn-images?(?:-xxx)?\.com",
    },
})


class HentaicosplaysGalleryExtractor(
        HentaicosplaysExtractor, GalleryExtractor):
    """Extractor for image galleries from
    hentai-cosplay-xxx.com, hentai-img-xxx.com, and porn-image.com"""
    directory_fmt = ("{site}", "{title}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{title}_{filename}"
    pattern = BASE_PATTERN + r"/(?:image|story)/([\w-]+)"
    example = "https://hentai-cosplay-xxx.com/image/TITLE/"

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        self.slug = self.groups[-1]
        self.gallery_url = "{}/story/{}/".format(self.root, self.slug)

    def _init(self):
        self.session.headers["Referer"] = self.gallery_url

    def metadata(self, page):
        title = text.extr(page, "<title>", "</title>")
        return {
            "title": text.unescape(title.rpartition(" Story Viewer - ")[0]),
            "slug" : self.slug,
            "site" : self.root.partition("://")[2].rpartition(".")[0],
        }

    def images(self, page):
        return [
            (url.replace("http:", "https:", 1), None)
            for url in text.extract_iter(
                page, '<amp-img class="auto-style" src="', '"')
        ]
