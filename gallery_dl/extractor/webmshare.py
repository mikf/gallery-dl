# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
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
    example = "https://webmshare.com/_ID_"

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
