# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://koofr.net/"""

from .common import Extractor, Message
from .. import text


class KoofrSharedExtractor(Extractor):
    """Base class for koofr extractors"""
    category = "koofr"
    subcategory = "shared"
    root = "https://app.koofr.net"
    directory_fmt = ("{category}", "{date:%Y-%m-%d} {title}")
    archive_fmt = "{post[id]}_{hash|id}"
    pattern = (r"(?:https?://)?(?:"
               r"(?:app\.)?koofr\.(?:net|eu)/links/([\w-]+)|"
               r"k00\.fr/(\w+))")
    example = "https://app.koofr.net/links/UUID"

    def items(self):
        uuid, code = self.groups
        if code is not None:
            uuid = self.request_location(
                "https://k00.fr/" + code, method="GET").rpartition("/")[2]

        url = f"{self.root}/api/v2/public/links/{uuid}"
        referer = f"{self.root}/links/{uuid}"
        password = self.config("password")
        params = {"password": password or ""}
        headers = {
            "Referer"        : referer,
            "X-Client"       : "newfrontend",
            "X-Koofr-Version": "2.1",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
        }
        data = self.request_json(url, params=params, headers=headers)
        root = data.get("publicUrlBase") or self.root
        base = f"{root}/content/links/{uuid}/files/get/"
        headers = {"Referer": referer}
        file = data["file"]

        if file["type"] == "dir" and not self.config("zip", False):
            path = True
            url = url + "/bundle"
            params["path"] = "/"
            files = self.request_json(
                url, params=params, headers=headers)["files"]
        else:
            path = False
            files = (file,)

        if password:
            password = text.escape(password)

        post = {
            "id"   : data["id"],
            "title": data["name"],
            "count": len(files),
            "date" : self.parse_timestamp(file["modified"] / 1000),
        }

        yield Message.Directory, "", post
        for num, file in enumerate(files, 1):
            file["count"] = len(files)
            file["num"] = num
            file["post"] = post
            file["date"] = self.parse_timestamp(file["modified"] / 1000)
            file["_http_headers"] = headers

            name = file["name"]
            text.nameext_from_name(name, file)

            name = text.escape(name)
            url = (f"{base}{name}?path=%2F{name if path else '&force'}")
            if password:
                url = f"{url}&password={password}"

            yield Message.Url, url, file
