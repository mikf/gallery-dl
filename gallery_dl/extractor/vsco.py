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
    """Base class for vsco extractors"""
    category = "vsco"
    root = "https://vsco.co"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1).lower()

    def items(self):
        yield Message.Version, 1
        yield Message.Directory, {"user": self.user}
        for img in self.images():
            url = "https://" + (img.get("video_url") or img["responsive_url"])
            data = text.nameext_from_url(url, {
                "id"    : img["_id"],
                "user"  : self.user,
                "grid"  : img["grid_name"],
                "meta"  : img.get("image_meta") or {},
                "tags"  : [tag["text"] for tag in img.get("tags") or ()],
                "date"  : text.parse_timestamp(img["upload_date"] // 1000),
                "video" : img["is_video"],
                "width" : img["width"],
                "height": img["height"],
                "description": img["description"],
            })
            yield Message.Url, url, data

    def images(self):
        """Return an iterable with all relevant image objects"""

    def _extract_preload_state(self, url):
        page = self.request(url, notfound=self.subcategory).text
        return json.loads(text.extract(page, "__PRELOADED_STATE__ = ", "<")[0])

    def _pagination(self, url, params, token, key, extra):
        headers = {
            "Referer"          : "{}/{}".format(self.root, self.user),
            "Authorization"    : "Bearer " + token,
            "X-Client-Platform": "web",
            "X-Client-Build"   : "1",
        }

        yield from map(self._transform_media, extra)

        while True:
            data = self.request(url, params=params, headers=headers).json()
            if not data.get(key):
                return
            yield from data[key]
            params["page"] += 1

    @staticmethod
    def _transform_media(media):
        media["_id"] = media["id"]
        media["is_video"] = media["isVideo"]
        media["grid_name"] = media["gridName"]
        media["upload_date"] = media["uploadDate"]
        media["responsive_url"] = media["responsiveUrl"]
        media["video_url"] = media.get("videoUrl")
        media["image_meta"] = media.get("imageMeta")
        return media


class VscoUserExtractor(VscoExtractor):
    """Extractor for images from a user on vsco.co"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"(?:/images(?:/\d+)?)?/?(?:$|[?#])"
    test = (
        ("https://vsco.co/missuri/images/1", {
            "range": "1-80",
            "count": 80,
            "pattern": r"https://im\.vsco\.co/[^/]+/[0-9a-f/]+/vsco\w+\.\w+",
        }),
        ("https://vsco.co/missuri"),
    )

    def images(self):
        url = "{}/{}/images/1".format(self.root, self.user)
        data = self._extract_preload_state(url)

        tkn = data["users"]["currentUser"]["tkn"]
        sid = str(data["sites"]["siteByUsername"][self.user]["site"]["id"])

        url = "{}/api/2.0/medias".format(self.root)
        params = {"page": 2, "size": "30", "site_id": sid}
        return self._pagination(url, params, tkn, "media", (
            data["medias"]["byId"][mid]["media"]
            for mid in data["medias"]["bySiteId"][sid]["medias"]["1"]
        ))


class VscoCollectionExtractor(VscoExtractor):
    """Extractor for images from a collection on vsco.co"""
    subcategory = "collection"
    directory_fmt = ("{category}", "{user}", "collection")
    archive_fmt = "c_{user}_{id}"
    pattern = BASE_PATTERN + r"/collection/"
    test = ("https://vsco.co/vsco/collection/1", {
        "range": "1-80",
        "count": 80,
        "pattern": r"https://im\.vsco\.co/[^/]+/[0-9a-f/]+/vsco\w+\.\w+",
    })

    def images(self):
        url = "{}/{}/collection/1".format(self.root, self.user)
        data = self._extract_preload_state(url)

        tkn = data["users"]["currentUser"]["tkn"]
        cid = (data["sites"]["siteByUsername"][self.user]
               ["site"]["siteCollectionId"])

        url = "{}/api/2.0/collections/{}/medias".format(self.root, cid)
        params = {"page": 2, "size": "20"}
        return self._pagination(url, params, tkn, "medias", (
            data["medias"]["byId"][mid]["media"]
            for mid in data
            ["collections"]["byCollectionId"][cid]["collection"]["1"]
        ))


class VscoImageExtractor(VscoExtractor):
    """Extractor for individual images on vsco.co"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/media/([0-9a-fA-F]+)"
    test = (
        ("https://vsco.co/erenyildiz/media/5d34b93ef632433030707ce2", {
            "url": "faa214d10f859f374ad91da3f7547d2439f5af08",
            "content": "1394d070828d82078035f19a92f404557b56b83f",
            "keyword": {
                "id"    : "5d34b93ef632433030707ce2",
                "user"  : "erenyildiz",
                "grid"  : "erenyildiz",
                "meta"  : dict,
                "tags"  : list,
                "date"  : "type:datetime",
                "video" : False,
                "width" : 1537,
                "height": 1537,
                "description": "re:Ni seviyorum. #vsco #vscox #vscochallenges",
            },
        }),
        ("https://vsco.co/jimenalazof/media/5b4feec558f6c45c18c040fd", {
            "url": "08e7eef3301756ce81206c0b47c1e9373756a74a",
            "content": "e739f058d726ee42c51c180a505747972a7dfa47",
            "keyword": {"video" : True},
        }),
    )

    def __init__(self, match):
        VscoExtractor.__init__(self, match)
        self.media_id = match.group(2)

    def images(self):
        url = "{}/{}/media/{}".format(self.root, self.user, self.media_id)
        data = self._extract_preload_state(url)
        media = data["medias"]["byId"].popitem()[1]["media"]
        return (self._transform_media(media),)
