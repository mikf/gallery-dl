# -*- coding: utf-8 -*-

# Copyright 2025-2026 Mike Fährmann
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
    directory_fmt = ("{category}", "{post[title]} ({post[id]})", "{path:I}")
    archive_fmt = "{post[id]}_{path:J/}_{hash|id}"
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

        file = data["file"]
        file["path"] = []
        if file["type"] == "dir" and self.config("recursive", True):
            files = self._extract_files(file, url + "/bundle", params, headers)
            recursive = True
        else:
            files = (file,)
            recursive = False

        post = {
            "id"   : data["id"],
            "title": data["name"],
            "date" : self.parse_timestamp(file["modified"] / 1000),
        }

        base = (f"{data.get('publicUrlBase') or self.root}"
                f"/content/links/{uuid}/files/get/")
        headers = {"Referer": referer}
        password = "&password=" + text.escape(password) if password else ""

        for file in files:
            file["post"] = post
            file["date"] = self.parse_timestamp(file["modified"] / 1000)
            file["_http_headers"] = headers

            name = file["name"]
            text.nameext_from_name(name, file)

            if recursive:
                if path := file["path"]:
                    path = f"{'/'.join(path)}/{name}"
                else:
                    path = name
            else:
                path = ""
                password += "&force"

            url = (f"{base}{text.escape(name)}"
                   f"?path=/{text.escape(path)}{password}")

            yield Message.Directory, "", file
            yield Message.Url, url, file

    def _extract_files(self, dir, url, params, headers):
        path = dir["path"]
        params["path"] = "/" + "/".join(path)

        files = self.request_json(
            url, params=params, headers=headers)["files"]

        for file in files:
            if file["type"] == "dir":
                file["path"] = path.copy()
                file["path"].append(file["name"])
                yield from self._extract_files(
                    file, url, params.copy(), headers)
            else:
                file["path"] = path
                yield file
