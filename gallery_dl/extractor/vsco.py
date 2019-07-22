# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://vsco.co/"""

from .common import Extractor, Message
from .. import text
import json


BASE_PATTERN = r"(?:https?://)?(?:www\.)?vsco\.co/([^/]+)"


class VscoExtractor(Extractor):
    category = "vsco"
    root = "https://vsco.co"
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1).lower()

    def items(self):
        yield Message.Version, 1
        yield Message.Directory, {"user": self.user}
        for img in self.images():
            url = "https://" + img["responsive_url"]
            data = text.nameext_from_url(url, {
                "id"    : img["_id"],
                "user"  : self.user,
                "grid"  : img["grid_name"],
                "meta"  : img.get("image_meta") or {},
                "tags"  : [tag["text"] for tag in img.get("tags") or ()],
                "date"  : text.parse_timestamp(img["upload_date"] // 1000),
                "width" : img["width"],
                "height": img["height"],
                "description": img["description"],
            })
            yield Message.Url, url, data

    def _pagination(self, url, params, token, extra):
        yield from extra

        headers = {
            "Referer"          : "{}/{}".format(self.root, self.user),
            "Authorization"    : "Bearer " + token,
            "X-Client-Platform": "web",
            "X-Client-Build"   : "1",
        }

        while True:
            data = self.request(url, headers=headers, params=params).json()
            if not data.get("media"):
                return
            yield from data["media"]
            params["page"] += 1


class VscoUserExtractor(VscoExtractor):
    subcategory = "user"
    directory_fmt = ("{category}", "{user}")
    pattern = BASE_PATTERN + r"/images/"
    test = ("https://vsco.co/missuri/images/1", {
        "range": "1-80",
        "count": 80,
        "pattern": r"https://im\.vsco\.co/[^/]+/[0-9a-f/]+/vsco\w+\.\w+",
        "keyword": {
            "id"    : str,
            "user"  : "missuri",
            "grid"  : "anybodyseenmylife",
            "meta"  : dict,
            "tags"  : list,
            "date"  : "type:datetime",
            "width" : int,
            "height": int,
            "description": str,
        },
    })

    def images(self):
        url = "{}/{}/images/1".format(self.root, self.user)
        page = self.request(url, notfound="user").text
        data = json.loads(text.extract(page, "__PRELOADED_STATE__ = ", "<")[0])
        site_id = str(data["sites"]["siteByUsername"][self.user]["site"]["id"])
        token = data["users"]["currentUser"]["tkn"]

        url = "https://vsco.co/api/2.0/medias"
        params = {
            "site_id": site_id,
            "page"   : 2,
            "size"   : "30",
        }

        extra = []
        medias = data["medias"]["byId"]
        for mid in data["medias"]["bySiteId"][site_id]["medias"]["1"]:
            media = medias[mid]["media"]
            media["_id"] = media["id"]
            media["grid_name"] = media["gridName"]
            media["image_meta"] = media["imageMeta"]
            media["upload_date"] = media["uploadDate"]
            media["responsive_url"] = media["responsiveUrl"]
            extra.append(media)

        return self._pagination(url, params, token, extra)
