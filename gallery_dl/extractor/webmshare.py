# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://webmshare.com/"""

from .common import Extractor, Message
from .. import text


class WebmshareVideoExtractor(Extractor):
    """Extractor for webmshare videos"""
    category = "webmshare"
    subcategory = "video"
    root = "https://webmshare.com"
    filename_fmt = "{id}{title:? //}.{extension}"
    archive_fmt = "{id}"
    pattern = (r"(?:https?://)?(?:s\d+\.)?webmshare\.com"
               r"/(?:play/|download-webm/)?(\w{3,})")
    test = (
        ("https://webmshare.com/O9mWY", {
            "keyword": {
                "date": "dt:2022-12-04 00:00:00",
                "extension": "webm",
                "filename": "O9mWY",
                "height": 568,
                "id": "O9mWY",
                "thumb": "https://s1.webmshare.com/t/O9mWY.jpg",
                "title": "Yeah buddy over here",
                "url": "https://s1.webmshare.com/O9mWY.webm",
                "views": int,
                "width": 320,
            },
        }),
        ("https://s1.webmshare.com/zBGAg.webm", {
            "keyword": {
                "date": "dt:2018-12-07 00:00:00",
                "height": 1080,
                "id": "zBGAg",
                "thumb": "https://s1.webmshare.com/t/zBGAg.jpg",
                "title": "",
                "url": "https://s1.webmshare.com/zBGAg.webm",
                "views": int,
                "width": 1920,
            },
        }),
        ("https://webmshare.com/play/zBGAg"),
        ("https://webmshare.com/download-webm/zBGAg"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.video_id = match.group(1)

    def items(self):
        url = "{}/{}".format(self.root, self.video_id)
        extr = text.extract_from(self.request(url).text)

        data = {
            "title": text.unescape(extr(
                'property="og:title" content="', '"').rpartition(" — ")[0]),
            "thumb": "https:" + extr('property="og:image" content="', '"'),
            "url"  : "https:" + extr('property="og:video" content="', '"'),
            "width": text.parse_int(extr(
                'property="og:video:width" content="', '"')),
            "height": text.parse_int(extr(
                'property="og:video:height" content="', '"')),
            "date" : text.parse_datetime(extr(
                "<small>Added ", "<"), "%B %d, %Y"),
            "views": text.parse_int(extr('glyphicon-eye-open"></span>', '<')),
            "id"       : self.video_id,
            "filename" : self.video_id,
            "extension": "webm",
        }

        if data["title"] == "webmshare":
            data["title"] = ""

        yield Message.Directory, data
        yield Message.Url, data["url"], data
