# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.smugmug.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import memcache

BASE_PATTERN = (
    r"(?:smugmug:(?:https?://)?([^/]+)|"
    r"(?:https?://)?([^.]+\.smugmug\.com))")


class SmugmugExtractor(Extractor):
    """Base class for smugmug extractors"""
    category = "smugmug"
    filename_fmt = "{category}_{Owner[Name]}_{Image[ImageKey]}.{extension}"

    def __init__(self):
        Extractor.__init__(self)
        self.api = SmugmugAPI(self)

    def update_image(self, image):
        if "ArchivedUri" not in image:
            largest = self.api.image_largest(image["ImageKey"])
            for key in ("Url", "Width", "Height", "MD5", "Size"):
                if key in largest:
                    image[key] = largest[key]
            return image["Url"], image
        return image["ArchivedUri"], image


class SmugmugAlbumExtractor(SmugmugExtractor):
    subcategory = "album"
    directory_fmt = ["{category}", "{Owner[Name]}", "{Album[Name]}"]
    archive_fmt = "a_{Album[AlbumKey]}_{Image[ImageKey]}"
    pattern = [r"smugmug:album:([^:]+)$"]
    test = [("smugmug:album:xgkb4C", {
        "url": "eb6133445064115ad83d32cbc6472520a2d24d53",
        "content": "864f6953cb04121290407a579611bc5087d117ee",
    })]

    def __init__(self, match):
        SmugmugExtractor.__init__(self)
        self.album_id = match.group(1)

    def items(self):
        album = self.api.album(self.album_id)
        images = self.api.album_images(self.album_id)
        username = album["Uris"]["User"]["Uri"].rpartition("/")[2]
        owner = self.api.user(username)

        data = {
            "Album": album,
            "Owner": owner,
        }

        yield Message.Version, 1
        yield Message.Directory, data

        for image in images:
            url, image = self.update_image(image)
            data["Image"] = image
            yield Message.Url, url, text.nameext_from_url(url, data)


class SmugmugImageExtractor(SmugmugExtractor):
    subcategory = "image"
    directory_fmt = ["{category}", "{Owner[Name]}"]
    archive_fmt = "{Image[ImageKey]}"
    pattern = [BASE_PATTERN + r"(?:/[^/?&#]+)+/i-([^/?&#]+)"]
    test = [("https://mikf.smugmug.com/Test/n-xnNH3s/i-L4CxBdg", {
        "url": "905bfdef52ce1a731a4eae17e9ac348511e17ae4",
        "keyword": "d53df829d493ec3e31b8fe300872beb968812bfd",
        "content": "626fe50d25fe49beeda15e116938db36e163c01f",
    })]

    def __init__(self, match):
        SmugmugExtractor.__init__(self)
        self.image_id = match.group(3)

    def items(self):
        image = self.api.image(self.image_id)
        username = image["Uris"]["ImageOwner"]["Uri"].rpartition("/")[2]
        owner = self.api.user(username)

        url, image = self.update_image(image)

        data = {
            "Image": image,
            "Owner": owner,
        }
        del image["Uris"]
        del owner["Uris"]
        text.nameext_from_url(url, data)

        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data


class SmugmugNodeExtractor(SmugmugExtractor):
    """ """
    subcategory = "node"
    directory_fmt = ["{category}"]
    archive_fmt = "n_{Node[NodeID]}_{Image[ImageID]}"
    pattern = [BASE_PATTERN + r"(?:/[^/?&#]+)+/n-([^/?&#]+)$"]
    test = [("https://mikf.smugmug.com/Test/n-xnNH3s", {
        "pattern": "^smugmug:album:xgkb4C$",
    })]

    def __init__(self, match):
        SmugmugExtractor.__init__(self)
        self.node_id = match.group(3)

    def items(self):
        yield Message.Version, 1

        data = self.api.node(self.node_id)
        if data["Type"] == "Album":
            album_id = data["Uris"]["Album"]["Uri"].rpartition("/")[2]
            yield Message.Queue, "smugmug:album:" + album_id, data
        # ...


class SmugmugAPI():
    """Minimal interface for the smugmug API v2"""
    API_URL = "https://api.smugmug.com/api/v2/"
    API_KEY = "DFqxg4jf7GrtsQ5PnbNB8899zKfnDrdK"
    API_SECRET = ("fknV35p9r9BwZC4XbTzvCXpcSJRdD83S"
                  "9nMFQm25ndGBzNPnwRDbRnnVBvqt4xTq")
    HEADERS = {"Accept": "application/json"}

    def __init__(self, extractor):
        api_key = extractor.config("api-key", self.API_KEY)
        api_secret = extractor.config("api-secret", self.API_SECRET)
        token = extractor.config("access-token")
        token_secret = extractor.config("access-token-secret")

        if api_key and api_secret and token and token_secret:
            self.session = util.OAuthSession(
                extractor.session,
                api_key, api_secret,
                token, token_secret,
            )
            self.api_key = None
        else:
            self.session = extractor.session
            self.api_key = api_key

    def album(self, album_id):
        return self._call("album/" + album_id)["Album"]

    def album_images(self, album_id):
        return self._pagination("album/" + album_id + "!images")

    def image(self, image_id):
        return self._call("image/" + image_id)["Image"]

    def image_largest(self, image_id):
        endpoint = "image/" + image_id + "!largestimage"
        return self._call(endpoint)["LargestImage"]

    def image_sizes(self, image_id):
        return self._call("image/" + image_id + "!sizedetails")

    def node(self, node_id):
        return self._call("node/" + node_id)["Node"]

    @memcache(keyarg=1)
    def user(self, username):
        return self._call("user/" + username)["User"]

    def _call(self, endpoint, params=None):
        url = self.API_URL + endpoint
        params = params or {}
        if self.api_key:
            params["APIKey"] = self.api_key

        response = self.session.get(url, params=params, headers=self.HEADERS)
        data = response.json()

        if 200 <= data["Code"] < 400:
            return data["Response"]

        if data["Code"] == 404:
            raise exception.NotFoundError()
        if data["Code"] == 429:
            self.log.error("Rate limit reached")
            raise exception.StopExtraction()

    def _pagination(self, endpoint):
        params = {
            "start": 1,
            "count": 100,
        }
        while True:
            response = self._call(endpoint, params)

            obj = response[response["Locator"]]
            if isinstance(obj, list):
                yield from obj
            else:
                yield obj

            if "NextPage" not in response["Pages"]:
                return
            params["start"] += params["count"]
