# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://vsco.co/"""

from .common import Extractor, Message
from .. import text, util


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
        return util.json_loads(text.extr(page, "__PRELOADED_STATE__ = ", "<"))

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
    example = "https://vsco.co/USER/gallery"

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
    example = "https://vsco.co/USER/collection/12345"

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
    example = "https://vsco.co/USER/media/0123456789abcdef"

    def __init__(self, match):
        VscoExtractor.__init__(self, match)
        self.media_id = match.group(2)

    def images(self):
        url = "{}/{}/media/{}".format(self.root, self.user, self.media_id)
        data = self._extract_preload_state(url)
        media = data["medias"]["byId"].popitem()[1]["media"]
        return (self._transform_media(media),)
