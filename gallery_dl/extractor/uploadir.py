# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://uploadir.com/"""

from .common import Extractor, Message
from .. import text
from email.utils import parsedate_tz
from datetime import datetime


class UploadirFileExtractor(Extractor):
    """Extractor for uploadir files"""
    category = "uploadir"
    subcategory = "file"
    root = "https://uploadir.com"
    pattern = r"(?:https?://)?uploadir\.com/(?:user/)?u(?:ploads)?/([^/?#]+)"
    test = (
        # image
        ("https://uploadir.com/u/rd3t46ry", {
            "pattern": r"https://uploadir\.com/u/rd3t46ry",
            "count": 1,
            "keyword": {
                "extension": "jpg",
                "filename": "Chloe and Rachel 4K jpg",
            },
        }),
        # archive
        ("https://uploadir.com/uploads/gxe8ti9v/downloads/new", {
            "pattern": r"https://uploadir\.com/uploads/gxe8ti9v/downloads",
            "count": 1,
            "keyword": {
                "extension": "zip",
                "filename": "NYAN-Mods-Pack#1",
            },
        }),
        ("https://uploadir.com/uploads/rd3t46ry"),
        ("https://uploadir.com/user/uploads/rd3t46ry"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.file_id = match.group(1)

    def items(self):
        url = "{}/u/{}".format(self.root, self.file_id)
        response = self.request(url, method="HEAD")

        if response.history:
            extr = text.extract_from(self.request(response.url).text)

            name = text.unescape(extr("<h2>", "</h2>").strip())
            url = self.root + extr('class="form" action="', '"')
            token = extr('name="authenticity_token" value="', '"')

            data = text.nameext_from_url(name, {
                "_http_method": "POST",
                "_http_data"  : {
                    "authenticity_token": token,
                    "upload_id": self.file_id,
                },
            })

        else:
            hget = response.headers.get
            hcd = hget("Content-Disposition")
            hlm = hget("Last-Modified")

            data = text.nameext_from_url(text.extr(hcd, 'filename="', '"'))
            if hlm:
                data["date"] = datetime(*parsedate_tz(hlm)[:6])

        yield Message.Directory, data
        yield Message.Url, url, data
