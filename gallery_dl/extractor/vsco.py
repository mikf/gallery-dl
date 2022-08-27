# -*- coding: utf-8 -*-

# Copyright 2019-2022 Mike Fährmann
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
        videos = self.config("videos", True)
        yield Message.Directory, {"user": self.user}
        for img in self.images():

            if not img or "responsive_url" not in img:
                continue

            if img["is_video"]:
                if not videos:
                    continue
                url = "https://" + img["video_url"]
            else:
                base = img["responsive_url"].partition("/")[2]
                cdn, _, path = base.partition("/")
                if cdn.startswith("aws"):
                    url = "https://image-{}.vsco.co/{}".format(cdn, path)
                elif cdn.isdecimal():
                    url = "https://image.vsco.co/" + base
                else:
                    url = "https://" + img["responsive_url"]

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
                "description": img.get("description") or "",
            })
            yield Message.Url, url, data

    def images(self):
        """Return an iterable with all relevant image objects"""

    def _extract_preload_state(self, url):
        page = self.request(url, notfound=self.subcategory).text
        return json.loads(text.extract(page, "__PRELOADED_STATE__ = ", "<")[0])

    def _pagination(self, url, params, token, key, extra=None):
        headers = {
            "Referer"          : "{}/{}".format(self.root, self.user),
            "Authorization"    : "Bearer " + token,
            "X-Client-Platform": "web",
            "X-Client-Build"   : "1",
        }

        if extra:
            yield from map(self._transform_media, extra)

        while True:
            data = self.request(url, params=params, headers=headers).json()
            medias = data.get(key)
            if not medias:
                return

            if "cursor" in params:
                for media in medias:
                    yield media[media["type"]]
                cursor = data.get("next_cursor")
                if not cursor:
                    return
                params["cursor"] = cursor
            else:
                yield from medias
                params["page"] += 1

    @staticmethod
    def _transform_media(media):
        if "responsiveUrl" not in media:
            return None
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
    pattern = BASE_PATTERN + r"(?:/gallery|/images(?:/\d+)?)?/?(?:$|[?#])"
    test = (
        ("https://vsco.co/missuri/gallery", {
            "pattern": r"https://image(-aws.+)?\.vsco\.co"
                       r"/[0-9a-f/]+/[\w-]+\.\w+",
            "range": "1-80",
            "count": 80,
        }),
        ("https://vsco.co/missuri/images/1"),
        ("https://vsco.co/missuri"),
    )

    def images(self):
        url = "{}/{}/gallery".format(self.root, self.user)
        data = self._extract_preload_state(url)
        tkn = data["users"]["currentUser"]["tkn"]
        sid = str(data["sites"]["siteByUsername"][self.user]["site"]["id"])

        url = "{}/api/3.0/medias/profile".format(self.root)
        params = {
            "site_id"  : sid,
            "limit"    : "14",
            "cursor"   : None,
        }

        return self._pagination(url, params, tkn, "media")


class VscoCollectionExtractor(VscoExtractor):
    """Extractor for images from a collection on vsco.co"""
    subcategory = "collection"
    directory_fmt = ("{category}", "{user}", "collection")
    archive_fmt = "c_{user}_{id}"
    pattern = BASE_PATTERN + r"/collection/"
    test = ("https://vsco.co/vsco/collection/1", {
        "pattern": r"https://image(-aws.+)?\.vsco\.co/[0-9a-f/]+/[\w-]+\.\w+",
        "range": "1-80",
        "count": 80,
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
            data["medias"]["byId"][mid["id"]]["media"]
            for mid in data
            ["collections"]["byId"][cid]["1"]["collection"]
        ))


class VscoImageExtractor(VscoExtractor):
    """Extractor for individual images on vsco.co"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/media/([0-9a-fA-F]+)"
    test = (
        ("https://vsco.co/erenyildiz/media/5d34b93ef632433030707ce2", {
            "url": "a45f9712325b42742324b330c348b72477996031",
            "content": "1394d070828d82078035f19a92f404557b56b83f",
            "keyword": {
                "id"    : "5d34b93ef632433030707ce2",
                "user"  : "erenyildiz",
                "grid"  : "erenyildiz",
                "meta"  : dict,
                "tags"  : list,
                "date"  : "dt:2019-07-21 19:12:11",
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
