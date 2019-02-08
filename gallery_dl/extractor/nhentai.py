# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://nhentai.net/"""

from .common import Extractor, Message
from .. import text
import json


class NHentaiExtractor(Extractor):
    """Base class for nhentai extractors"""
    category = "nhentai"
    root = "https://nhentai.net"
    media_url = "https://i.nhentai.net"

    @staticmethod
    def transform_to_metadata(ginfo):
        """Transform an nhentai API response into compatible metadata"""
        title_en = ginfo["title"].get("english", "")
        title_ja = ginfo["title"].get("japanese", "")
        return {
            "gallery_id": ginfo["id"],
            "upload_date": ginfo["upload_date"],
            "media_id": ginfo["media_id"],
            "scanlator": ginfo["scanlator"],
            "count": ginfo["num_pages"],
            "title": title_en or title_ja,
            "title_en": title_en,
            "title_ja": title_ja,
        }


class NhentaiGalleryExtractor(NHentaiExtractor):
    """Extractor for image galleries from nhentai.net"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{gallery_id} {title}")
    filename_fmt = "{category}_{gallery_id}_{num:>03}.{extension}"
    archive_fmt = "{gallery_id}_{num}"
    pattern = r"(?:https?://)?nhentai\.net/g/(\d+)"
    test = ("https://nhentai.net/g/147850/", {
        "url": "5179dbf0f96af44005a0ff705a0ad64ac26547d0",
        "keyword": "2f94976e657f3043a89997e22f4de8e1b22d9175",
    })

    def __init__(self, match):
        NHentaiExtractor.__init__(self)
        self.gid = match.group(1)

    def items(self):
        ginfo = self.get_gallery_info(self.gid)
        data = self.transform_to_metadata(ginfo)
        urlfmt = "{}/galleries/{}/{{}}.{{}}".format(
            self.media_url, data["media_id"])
        extdict = {"j": "jpg", "p": "png", "g": "gif"}
        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], image in enumerate(ginfo["images"]["pages"], 1):
            ext = extdict.get(image["t"], "jpg")
            data["width"] = image["w"]
            data["height"] = image["h"]
            data["extension"] = ext
            yield Message.Url, urlfmt.format(data["num"], ext), data

    def get_gallery_info(self, gallery_id):
        """Extract and return info about a gallery by ID"""
        url = "{}/g/{}".format(self.root, gallery_id)
        page = self.request(url).text
        return json.loads(text.extract(page, "N.gallery(", ");")[0])


class NhentaiSearchExtractor(NHentaiExtractor):
    """Extractor for nhentai search results"""
    category = "nhentai"
    subcategory = "search"
    pattern = r"(?:https?://)?nhentai\.net/search/?\?([^#]+)"
    test = ("https://nhentai.net/search/?q=touhou", {
        "pattern": NhentaiGalleryExtractor.pattern,
        "count": 30,
        "range": "1-30",
    })

    def __init__(self, match):
        NHentaiExtractor.__init__(self)
        self.params = text.parse_query(match.group(1))

    def items(self):
        yield Message.Version, 1
        for gid in self._pagination(self.params):
            url = "{}/g/{}/".format(self.root, gid)
            yield Message.Queue, url, {}

    def _pagination(self, params):
        url = "{}/search/".format(self.root)
        params["page"] = text.parse_int(params.get("page"), 1)

        while True:
            page = self.request(url, params=params).text

            yield from text.extract_iter(page, 'href="/g/', '/')

            if 'class="next"' not in page:
                return
            params["page"] += 1
