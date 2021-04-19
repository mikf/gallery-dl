# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentai-cosplays.com/
(also works for hentai-img.com and porn-images-xxx.com)"""

from .common import GalleryExtractor
from .. import text
import re


class HentaicosplaysGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from
    hentai-cosplays.com, hentai-img.com, and porn-images-xxx.com"""
    category = "hentaicosplays"
    directory_fmt = ("{site}", "{title}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{title}_{filename}"
    pattern = r"((?:https?://)?(?:\w{2}\.)?" \
              r"(hentai-cosplays|hentai-img|porn-images-xxx)\.com)/" \
              r"(?:image|story)/([\w-]+)"
    test = (
        ("https://hentai-cosplays.com/image/---devilism--tide-kurihara-/", {
            "pattern": r"https://static\d?.hentai-cosplays.com/upload/"
                       r"\d+/\d+/\d+/\d+.jpg$",
            "keyword": {
                "count": 18,
                "site": "hentai-cosplays",
                "slug": "---devilism--tide-kurihara-",
                "title": str,
            },
        }),
        ("https://fr.porn-images-xxx.com/image/enako-enako-24/", {
            "pattern": r"https://static\d?.porn-images-xxx.com/upload/"
                       r"\d+/\d+/\d+/\d+.jpg$",
            "keyword": {
                "count": 11,
                "site": "porn-images-xxx",
                "slug": "enako-enako-24",
                "title": str,
            },
        }),
        ("https://ja.hentai-img.com/image/hollow-cora-502/", {
            "pattern": r"https://static\d?.hentai-img.com/upload/"
                       r"\d+/\d+/\d+/\d+.jpg$",
            "keyword": {
                "count": 2,
                "site": "hentai-img",
                "slug": "hollow-cora-502",
                "title": str,
            },
        }),
    )

    def __init__(self, match):
        root, self.site, path = match.groups()
        self.root = text.ensure_http_scheme(root)
        url = "{}/story/{}/".format(self.root, path)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        title = text.extract(page, "<title>", "</title>")[0]
        _slug_raw = text.extract(page, '<meta property="og:url" content="', '"')[0]
        slug = re.match(r"^https://[^/]+\/[^/]+\/(?P<slug>[^/]+)/$", _slug_raw).groupdict()["slug"]
        return {
            "title": text.unescape(title.rpartition(" Story Viewer - ")[0]),
            "slug" : slug,
            "site" : self.site,
        }

    def images(self, page):
        return [
            (url, None)
            for url in text.extract_iter(
                page, '<amp-img class="auto-style" src="', '"')
        ]
