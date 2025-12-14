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

        name = data["name"]
        file = text.nameext_from_name(name, data["file"])
        file["_http_headers"] = {"Referer": referer}

        root = data.get("publicUrlBase") or self.root
        url = f"{root}/content/links/{uuid}/files/get/{name}?path=/&force="
        if password:
            url = f"{url}&password={password}"

        yield Message.Directory, "", file
        yield Message.Url, url, file
