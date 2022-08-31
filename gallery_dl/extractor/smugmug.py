# -*- coding: utf-8 -*-

# Copyright 2018-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.smugmug.com/"""

from .common import Extractor, Message
from .. import text, oauth, exception

BASE_PATTERN = (
    r"(?:smugmug:(?!album:)(?:https?://)?([^/]+)|"
    r"(?:https?://)?([\w-]+)\.smugmug\.com)")


class SmugmugExtractor(Extractor):
    """Base class for smugmug extractors"""
    category = "smugmug"
    filename_fmt = ("{category}_{User[NickName]:?/_/}"
                    "{Image[UploadKey]}_{Image[ImageKey]}.{extension}")
    cookiedomain = None
    empty_user = {
        "Uri": "",
        "ResponseLevel": "Public",
        "Name": "",
        "NickName": "",
        "QuickShare": False,
        "RefTag": "",
        "ViewPassHint": "",
        "WebUri": "",
        "Uris": None,
    }

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.api = SmugmugAPI(self)
        self.videos = self.config("videos", True)
        self.session = self.api.session

    def _select_format(self, image):
        details = image["Uris"]["ImageSizeDetails"]
        media = None

        if self.videos and image["IsVideo"]:
            fltr = "VideoSize"
        elif "ImageSizeOriginal" in details:
            media = details["ImageSizeOriginal"]
        else:
            fltr = "ImageSize"

        if not media:
            sizes = filter(lambda s: s[0].startswith(fltr), details.items())
            media = max(sizes, key=lambda s: s[1]["Width"])[1]
        del image["Uris"]

        for key in ("Url", "Width", "Height", "MD5", "Size", "Watermarked",
                    "Bitrate", "Duration"):
            if key in media:
                image[key] = media[key]
        return image["Url"]


class SmugmugAlbumExtractor(SmugmugExtractor):
    """Extractor for smugmug albums"""
    subcategory = "album"
    directory_fmt = ("{category}", "{User[NickName]}", "{Album[Name]}")
    archive_fmt = "a_{Album[AlbumKey]}_{Image[ImageKey]}"
    pattern = r"smugmug:album:([^:]+)$"
    test = (
        ("smugmug:album:cr4C7f", {
            "url": "2c2e576e47d4e9ce60b44871f08a8c66b5ebaceb",
        }),
        # empty
        ("smugmug:album:Fb7hMs", {
            "count": 0,
        }),
        # no "User"
        ("smugmug:album:6VRT8G", {
            "url": "c4a0f4c4bfd514b93cbdeb02b3345bf7ef6604df",
        }),
    )

    def __init__(self, match):
        SmugmugExtractor.__init__(self, match)
        self.album_id = match.group(1)

    def items(self):
        album = self.api.album(self.album_id, "User")
        user = album["Uris"].get("User") or self.empty_user.copy()

        del user["Uris"]
        del album["Uris"]
        data = {"Album": album, "User": user}

        yield Message.Directory, data

        for image in self.api.album_images(self.album_id, "ImageSizeDetails"):
            url = self._select_format(image)
            data["Image"] = image
            yield Message.Url, url, text.nameext_from_url(url, data)


class SmugmugImageExtractor(SmugmugExtractor):
    """Extractor for individual smugmug images"""
    subcategory = "image"
    archive_fmt = "{Image[ImageKey]}"
    pattern = BASE_PATTERN + r"(?:/[^/?#]+)+/i-([^/?#-]+)"
    test = (
        ("https://tdm.smugmug.com/Nature/Dove/i-kCsLJT6", {
            "url": "e6408fd2c64e721fd146130dceb56a971ceb4259",
            "keyword": "b31a63d07c9c26eb0f79f52d60d171a98938f99b",
            "content": "ecbd9d7b4f75a637abc8d35319be9ec065a44eb0",
        }),
        # video
        ("https://tstravels.smugmug.com/Dailies/Daily-Dose-2015/i-39JFNzB", {
            "url": "04d0ab1ff829ca7d78f5acb5548953df08e9a5ee",
            "keyword": "4cef98133ace511adc874c9d9abac5817ba0d856",
        }),
    )

    def __init__(self, match):
        SmugmugExtractor.__init__(self, match)
        self.image_id = match.group(3)

    def items(self):
        image = self.api.image(self.image_id, "ImageSizeDetails")
        url = self._select_format(image)

        data = {"Image": image}
        text.nameext_from_url(url, data)

        yield Message.Directory, data
        yield Message.Url, url, data


class SmugmugPathExtractor(SmugmugExtractor):
    """Extractor for smugmug albums from URL paths and users"""
    subcategory = "path"
    pattern = BASE_PATTERN + r"((?:/[^/?#a-fh-mo-z][^/?#]*)*)/?$"
    test = (
        ("https://tdm.smugmug.com/Nature/Dove", {
            "pattern": "smugmug:album:cr4C7f$",
        }),
        ("https://tdm.smugmug.com/", {
            "pattern": SmugmugAlbumExtractor.pattern,
            "url": "1640028712875b90974e5aecd91b60e6de6138c7",
        }),
        # gallery node without owner
        ("https://www.smugmug.com/gallery/n-GLCjnD/", {
            "pattern": "smugmug:album:6VRT8G$",
        }),
        # custom domain
        ("smugmug:www.sitkapics.com/TREES-and-TRAILS/", {
            "pattern": "smugmug:album:ct8Nds$",
        }),
        ("smugmug:www.sitkapics.com/", {
            "pattern": r"smugmug:album:\w{6}$",
            "count": ">= 14",
        }),
        ("smugmug:https://www.sitkapics.com/"),
    )

    def __init__(self, match):
        SmugmugExtractor.__init__(self, match)
        self.domain, self.user, self.path = match.groups()

    def items(self):

        if not self.user:
            self.user = self.api.site_user(self.domain)["NickName"]

        if self.path:
            if self.path.startswith("/gallery/n-"):
                node = self.api.node(self.path[11:])
            else:
                data = self.api.user_urlpathlookup(self.user, self.path)
                node = data["Uris"]["Node"]

            if node["Type"] == "Album":
                nodes = (node,)
            elif node["Type"] == "Folder":
                nodes = self.album_nodes(node)
            else:
                nodes = ()

            for node in nodes:
                album_id = node["Uris"]["Album"].rpartition("/")[2]
                node["_extractor"] = SmugmugAlbumExtractor
                yield Message.Queue, "smugmug:album:" + album_id, node

        else:
            for album in self.api.user_albums(self.user):
                uri = "smugmug:album:" + album["AlbumKey"]
                album["_extractor"] = SmugmugAlbumExtractor
                yield Message.Queue, uri, album

    def album_nodes(self, root):
        """Yield all descendant album nodes of 'root'"""
        for node in self.api.node_children(root["NodeID"]):
            if node["Type"] == "Album":
                yield node
            elif node["Type"] == "Folder":
                yield from self.album_nodes(node)


class SmugmugAPI(oauth.OAuth1API):
    """Minimal interface for the smugmug API v2"""
    API_DOMAIN = "api.smugmug.com"
    API_KEY = "RCVHDGjcbc4Fhzq4qzqLdZmvwmwB6LM2"
    API_SECRET = ("jGrdndvJqhTx8XSNs7TFTSSthhZHq92d"
                  "dMpbpDpkDVNM7TDgnvLFMtfB5Mg5kH73")
    HEADERS = {"Accept": "application/json"}

    def album(self, album_id, expands=None):
        return self._expansion("album/" + album_id, expands)

    def image(self, image_id, expands=None):
        return self._expansion("image/" + image_id, expands)

    def node(self, node_id, expands=None):
        return self._expansion("node/" + node_id, expands)

    def user(self, username, expands=None):
        return self._expansion("user/" + username, expands)

    def album_images(self, album_id, expands=None):
        return self._pagination("album/" + album_id + "!images", expands)

    def node_children(self, node_id, expands=None):
        return self._pagination("node/" + node_id + "!children", expands)

    def user_albums(self, username, expands=None):
        return self._pagination("user/" + username + "!albums", expands)

    def site_user(self, domain):
        return self._call("!siteuser", domain=domain)["Response"]["User"]

    def user_urlpathlookup(self, username, path):
        endpoint = "user/" + username + "!urlpathlookup"
        params = {"urlpath": path}
        return self._expansion(endpoint, "Node", params)

    def _call(self, endpoint, params=None, domain=API_DOMAIN):
        url = "https://{}/api/v2/{}".format(domain, endpoint)
        params = params or {}
        if self.api_key:
            params["APIKey"] = self.api_key
        params["_verbosity"] = "1"

        response = self.request(url, params=params, headers=self.HEADERS)
        data = response.json()

        if 200 <= data["Code"] < 400:
            return data
        if data["Code"] == 404:
            raise exception.NotFoundError()
        if data["Code"] == 429:
            raise exception.StopExtraction("Rate limit reached")
        self.log.debug(data)
        raise exception.StopExtraction("API request failed")

    def _expansion(self, endpoint, expands, params=None):
        endpoint = self._extend(endpoint, expands)
        result = self._apply_expansions(self._call(endpoint, params), expands)
        if not result:
            raise exception.NotFoundError()
        return result[0]

    def _pagination(self, endpoint, expands=None):
        endpoint = self._extend(endpoint, expands)
        params = {"start": 1, "count": 100}

        while True:
            data = self._call(endpoint, params)
            yield from self._apply_expansions(data, expands)

            if "NextPage" not in data["Response"]["Pages"]:
                return
            params["start"] += params["count"]

    @staticmethod
    def _extend(endpoint, expands):
        if expands:
            endpoint += "?_expand=" + expands
        return endpoint

    @staticmethod
    def _apply_expansions(data, expands):

        def unwrap(response):
            locator = response["Locator"]
            return response[locator] if locator in response else []

        objs = unwrap(data["Response"])
        if not isinstance(objs, list):
            objs = (objs,)

        if "Expansions" in data:
            expansions = data["Expansions"]
            expands = expands.split(",")

            for obj in objs:
                uris = obj["Uris"]

                for name in expands:
                    if name in uris:
                        uri = uris[name]
                        uris[name] = unwrap(expansions[uri])

        return objs
