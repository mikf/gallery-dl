# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentai-cosplay-xxx.com/
(also works for hentai-img.com and porn-images-xxx.com)"""

from .common import GalleryExtractor
from .. import text


class HentaicosplaysGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from
    hentai-cosplay-xxx.com, hentai-img.com, and porn-images-xxx.com"""
    category = "hentaicosplays"
    directory_fmt = ("{site}", "{title}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{title}_{filename}"
    pattern = r"((?:https?://)?(?:\w{2}\.)?" \
              r"(hentai-cosplay(?:s|-xxx)|hentai-img|porn-images-xxx)\.com)/" \
              r"(?:image|story)/([\w-]+)"
    example = "https://hentai-cosplay-xxx.com/image/TITLE/"

    def __init__(self, match):
        root, self.site, self.slug = match.groups()
        self.root = text.ensure_http_scheme(root)
        if self.root == "https://hentai-cosplays.com":
            self.root = "https://hentai-cosplay-xxx.com"
        url = "{}/story/{}/".format(self.root, self.slug)
        GalleryExtractor.__init__(self, match, url)

    def _init(self):
        self.session.headers["Referer"] = self.gallery_url

    def metadata(self, page):
        title = text.extr(page, "<title>", "</title>")
        return {
            "title": text.unescape(title.rpartition(" Story Viewer - ")[0]),
            "slug" : self.slug,
            "site" : self.site,
        }

    def images(self, page):
        return [
            (url.replace("http:", "https:", 1), None)
            for url in text.extract_iter(
                page, '<amp-img class="auto-style" src="', '"')
        ]
