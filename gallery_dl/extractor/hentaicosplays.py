# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""
Extractor for https://hentai-cosplays.com/
(also works for hentai-img.com and porn-images-xxx.com)
"""

from .common import Extractor, Message
from .. import text


class HentaicosplaysGalleryExtractor(Extractor):
    """
    Extractor for image galleries from hentai-cosplays.com, hentai-img.com,
    and porn-images-xxx.com
    """
    category = "hentaicosplays"
    subcategory = "gallery"
    directory_fmt = ("{site}", "{title}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{title}_{filename}"
    root = "https://hentai-cosplays.com"
    pattern = r"(?:https?://)?(?:\w{2}.)?" \
              r"(hentai-cosplays|hentai-img|porn-images-xxx)\.com/" \
              r"(?:image|story)/([\w-]+)(/\w+/\d+)?"
    test = (
        ("https://hentai-cosplays.com/image/---devilism--tide-kurihara-/", {
            "pattern": r"https://static\d?.hentai-cosplays.com/upload/"
                       r"\d+/\d+/\d+/\d+.jpg$",
            "keyword": {
                "count": 18,
                "site": "hentai-cosplays",
                "title": str,
            },
        }),
        ("https://fr.porn-images-xxx.com/image/enako-enako-24/", {
            "pattern": r"https://static\d?.porn-images-xxx.com/upload/"
                       r"\d+/\d+/\d+/\d+.jpg$",
            "keyword": {
                "count": 11,
                "site": "porn-images-xxx",
                "title": str,
            },
        }),
        ("https://ja.hentai-img.com/image/hollow-cora-502/", {
            "pattern": r"https://static\d?.hentai-img.com/upload/"
                       r"\d+/\d+/\d+/\d+.jpg$",
            "keyword": {
                "count": 2,
                "site": "hentai-img",
                "title": str,
            },
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.site = match.group(1)
        self.title = match.group(2)

    def items(self):
        url = "https://{}.com/story/{}/".format(
            self.site, self.title)
        page = self.request(url).text
        data = self.metadata(page)
        images = text.extract_iter(page,
                                   '<amp-img class="auto-style" src="', '"')
        yield Message.Version, 1
        yield Message.Directory, data
        for image in images:
            yield Message.Url, image, text.nameext_from_url(image, data)

    def metadata(self, page):
        """Collect metadata for extractor-job"""
        title = text.extract(page, "<title>", "</title>")[0]
        title, _, _ = title.rpartition(" Story Viewer - ")
        return {
            "title": title,
            "site": self.site,
        }
