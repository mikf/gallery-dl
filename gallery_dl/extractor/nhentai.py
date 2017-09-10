# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://nhentai.net/"""

from .common import Extractor, Message
from .. import text
import json


class NhentaiGalleryExtractor(Extractor):
    """Extractor for image galleries from nhentai.net"""
    category = "nhentai"
    subcategory = "gallery"
    directory_fmt = ["{category}", "{gallery_id} {title}"]
    filename_fmt = "{category}_{gallery_id}_{num:>03}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?nhentai\.net/g/(\d+)"]
    test = [("http://nhentai.net/g/147850/", {
        "url": "5179dbf0f96af44005a0ff705a0ad64ac26547d0",
        "keyword": "82751294e75fc203b019ffd94d8c1f94a5b86494",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.gid = match.group(1)

    def items(self):
        ginfo = self.get_gallery_info()
        data = self.get_job_metadata(ginfo)
        urlfmt = "{}galleries/{}/{{}}.{{}}".format(
            ginfo["media_url"], data["media_id"])
        extdict = {"j": "jpg", "p": "png", "g": "gif"}
        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], image in enumerate(ginfo["images"]["pages"], 1):
            ext = extdict.get(image["t"], "jpg")
            data["width"] = image["w"]
            data["height"] = image["h"]
            data["extension"] = ext
            yield Message.Url, urlfmt.format(data["num"], ext), data

    def get_gallery_info(self):
        """Extract and return gallery-info"""
        page = self.request("https://nhentai.net/g/" + self.gid + "/1/").text
        media_url, pos = text.extract(
            page, ".reader({\n\t\t\tmedia_url: '", "'")
        json_data, pos = text.extract(
            page, "gallery: ", ",\n", pos)
        json_dict = json.loads(json_data)
        json_dict["media_url"] = media_url
        return json_dict

    def get_job_metadata(self, ginfo):
        """Collect metadata for extractor-job"""
        title_en = ginfo["title"].get("english", "")
        title_ja = ginfo["title"].get("japanese", "")
        return {
            "gallery_id": self.gid,
            "upload_date": ginfo["upload_date"],
            "media_id": ginfo["media_id"],
            "scanlator": ginfo["scanlator"],
            "count": ginfo["num_pages"],
            "title": title_en or title_ja,
            "title_en": title_en,
            "title_ja": title_ja,
        }
