# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://imgchili.net/"""

from .common import Extractor, Message
from .. import text


class ImgchiliExtractor(Extractor):
    """Base class for imgchili extractors"""
    category = "imgchili"
    root = "https://imgchili.net"

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.group(0)
        self.match = match
        self.session.headers["Referer"] = self.root

    def items(self):
        page = self.request(self.url, encoding="utf-8").text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for url, image in self.get_images(page):
            data.update(image)
            yield Message.Url, url, data

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        return {}

    def get_images(self, page):
        """Collect image-urls and -metadata"""
        return []


class ImgchiliImageExtractor(ImgchiliExtractor):
    """Extractor for single images from imgchili.net"""
    subcategory = "image"
    pattern = [r"(?:https?://)?(?:www\.)?imgchili\.net/show/\d+/(\d+)_[^/]+"]
    test = [(("http://imgchili.net/show/89427/"
              "89427136_test___quot;___gt;.png"), {
        "url": "b93d92a6b58eb30a7ff6f9729cb748d25fea0c86",
        "keyword": "9c584f848766e4cc71d9e7f5f1f849e296ec05ae",
    })]

    def get_job_metadata(self, page):
        name1, pos = text.extract(page, '="description" content="', '. An ')
        name2, pos = text.extract(page, 'image called ', '" />\n', pos)
        _    , pos = text.extract(page, '<link rel="image_src"', '', pos)
        self.imgurl, pos = text.extract(page, ' href="', '"', pos)
        parts = name2.split("in the gallery ")
        name = parts[0] if not parts[0].endswith("...") else name1
        return text.nameext_from_url(name, {
            "image_id": self.match.group(1),
            "title": text.unescape(parts[-1]) if len(parts) > 1 else ""
        })

    def get_images(self, page):
        return [(self.imgurl, {})]


class ImgchiliAlbumExtractor(ImgchiliExtractor):
    """Extractor for image-albums from imgchili.net"""
    subcategory = "album"
    directory_fmt = ["{category}", "{title} - {key}"]
    filename_fmt = "{num:>03} {filename}"
    pattern = [r"(?:https?://)?(?:www\.)?imgchili\.net/album/([^/]+)"]
    test = [("http://imgchili.net/album/7a3824c59f77c8d39b260f9168d4b49b", {
        "url": "995e32b62c36d48b02ef4c7a7a19463924391e2a",
        "keyword": "ae0c56cfd1fe032e5bc22f1188767b2a923ae25e",
    })]

    def get_job_metadata(self, page):
        title = text.extract(page, "<h1>", "</h1>")[0]
        return {
            "title": text.unescape(title),
            "key": self.match.group(1),
        }

    def get_images(self, page):
        pos = 0
        num = 0
        while True:
            num += 1
            url  , pos = text.extract(page, '<img src="http://t', 'jpg"', pos)
            if not url:
                return
            imgid, pos = text.extract(page, ' alt="', '_', pos)
            name , pos = text.extract(page, '<strong>', '</strong>', pos)
            data = text.nameext_from_url(name, {"image_id": imgid, "num": num})
            yield "http://i" + url + data["extension"], data
