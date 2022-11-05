# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://uploadir.com/"""

from .common import Extractor, Message
from .. import text


class UploadirFileExtractor(Extractor):
    """Extractor for uploadir files"""
    category = "uploadir"
    subcategory = "file"
    root = "https://uploadir.com"
    filename_fmt = "{filename} ({id}).{extension}"
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?uploadir\.com/(?:user/)?u(?:ploads)?/([^/?#]+)"
    test = (
        # image
        ("https://uploadir.com/u/rd3t46ry", {
            "pattern": r"https://uploadir\.com/u/rd3t46ry",
            "count": 1,
            "keyword": {
                "extension": "jpg",
                "filename": "Chloe and Rachel 4K jpg",
                "id": "rd3t46ry",
            },
        }),
        # archive
        ("https://uploadir.com/uploads/gxe8ti9v/downloads/new", {
            "pattern": r"https://uploadir\.com/uploads/gxe8ti9v/downloads",
            "count": 1,
            "keyword": {
                "extension": "zip",
                "filename": "NYAN-Mods-Pack#1",
                "id": "gxe8ti9v",
            },
        }),
        # utf-8 filename
        ("https://uploadir.com/u/fllda6xl", {
            "pattern": r"https://uploadir\.com/u/fllda6xl",
            "count": 1,
            "keyword": {
                "extension": "png",
                "filename": "_圖片_🖼_image_",
                "id": "fllda6xl",
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
        response = self.request(url, method="HEAD", allow_redirects=False)

        if 300 <= response.status_code < 400:
            url = response.headers["Location"]
            extr = text.extract_from(self.request(url).text)

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
            hcd = response.headers.get("Content-Disposition")
            name = (hcd.partition("filename*=UTF-8''")[2] or
                    text.extr(hcd, 'filename="', '"'))
            data = text.nameext_from_url(name)

        data["id"] = self.file_id
        yield Message.Directory, data
        yield Message.Url, url, data
