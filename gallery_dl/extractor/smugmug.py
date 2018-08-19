# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.smugmug.com/"""

from .common import Extractor, Message
from .. import text, oauth, exception

BASE_PATTERN = (
    r"(?:smugmug:(?!album:)(?:https?://)?([^/]+)|"
    r"(?:https?://)?([^.]+)\.smugmug\.com)")


class SmugmugExtractor(Extractor):
    """Base class for smugmug extractors"""
    category = "smugmug"
    filename_fmt = ("{category}_{User[NickName]}_"
                    "{Image[UploadKey]}_{Image[ImageKey]}.{extension}")

    def __init__(self):
        Extractor.__init__(self)
        self.api = SmugmugAPI(self)

    @staticmethod
    def _apply_largest(image, delete=True):
        largest = image["Uris"]["LargestImage"]
        if delete:
            del image["Uris"]
        for key in ("Url", "Width", "Height", "MD5", "Size", "Watermarked"):
            if key in largest:
                image[key] = largest[key]
        return image["Url"]


class SmugmugAlbumExtractor(SmugmugExtractor):
    """Extractor for smugmug albums"""
    subcategory = "album"
    directory_fmt = ["{category}", "{User[NickName]}", "{Album[Name]}"]
    archive_fmt = "a_{Album[AlbumKey]}_{Image[ImageKey]}"
    pattern = [r"smugmug:album:([^:]+)$"]
    test = [
        ("smugmug:album:SXvjbW", {
            "count": 0,
        }),
        ("smugmug:album:ddvxpg", {
            "url": "8775c2cf05f001e895435faa89f22a03214568bf",
        }),
    ]

    def __init__(self, match):
        SmugmugExtractor.__init__(self)
        self.album_id = match.group(1)

    def items(self):
        album = self.api.album(self.album_id, "User")
        user = album["Uris"]["User"]

        del user["Uris"]
        del album["Uris"]
        data = {"Album": album, "User": user}

        yield Message.Version, 1
        yield Message.Directory, data

        for image in self.api.album_images(self.album_id, "LargestImage"):
            url = self._apply_largest(image)
            data["Image"] = image
            yield Message.Url, url, text.nameext_from_url(url, data)


class SmugmugImageExtractor(SmugmugExtractor):
    """Extractor for individual smugmug images"""
    subcategory = "image"
    directory_fmt = ["{category}", "{User[NickName]}"]
    archive_fmt = "{Image[ImageKey]}"
    pattern = [BASE_PATTERN + r"(?:/[^/?&#]+)+/i-([^/?&#]+)"]
    test = [("https://acapella.smugmug.com/Micro-Macro/Drops/i-g2Dmf9z", {
        "url": "ab0d7aa001a53ff3fd228622070b39005b6fc179",
        "keyword": "a116167929c22338e6067b81c5d3bee641df3af3",
        "content": "64a8f69a1d824921eebbdf2420087937adfa45cd",
    })]

    def __init__(self, match):
        SmugmugExtractor.__init__(self)
        self.image_id = match.group(3)

    def items(self):
        image = self.api.image(self.image_id, "LargestImage,ImageOwner")
        user = image["Uris"]["ImageOwner"]
        url = self._apply_largest(image)

        del user["Uris"]
        data = {"Image": image, "User": user}
        text.nameext_from_url(url, data)

        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data


class SmugmugPathExtractor(SmugmugExtractor):
    """Extractor for smugmug albums from URL paths and users"""
    subcategory = "path"
    pattern = [BASE_PATTERN + r"((?:/[^/?&#a-mo-z][^/?&#]*)*)/?$"]
    test = [
        ("https://acapella.smugmug.com/Micro-Macro/Drops/", {
            "pattern": "smugmug:album:ddvxpg$",
        }),
        ("https://acapella.smugmug.com/", {
            "pattern": r"smugmug:album:\w+$",
            "url": "8bd8b3f4f8bdd584bf5ddfd509ff3c98f8bc323b",
        }),
        ("smugmug:www.creativedogportraits.com/PortfolioGallery/", {
            "pattern": "smugmug:album:txWXzs$",
        }),
        ("smugmug:www.creativedogportraits.com/", {
            "pattern": "smugmug:album:txWXzs$",
        }),
        ("smugmug:https://www.creativedogportraits.com/", None),
    ]

    def __init__(self, match):
        SmugmugExtractor.__init__(self)
        self.domain, self.user, self.path = match.groups()

    def items(self):
        yield Message.Version, 1

        if not self.user:
            self.user = self.api.site_user(self.domain)["NickName"]

        if self.path:
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
                yield Message.Queue, "smugmug:album:" + album_id, node

        else:
            for album in self.api.user_albums(self.user):
                uri = "smugmug:album:" + album["AlbumKey"]
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
    API_KEY = "DFqxg4jf7GrtsQ5PnbNB8899zKfnDrdK"
    API_SECRET = ("fknV35p9r9BwZC4XbTzvCXpcSJRdD83S"
                  "9nMFQm25ndGBzNPnwRDbRnnVBvqt4xTq")
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

        response = self.session.get(url, params=params, headers=self.HEADERS)
        data = response.json()

        if 200 <= data["Code"] < 400:
            return data
        if data["Code"] == 404:
            raise exception.NotFoundError()
        if data["Code"] == 429:
            self.log.error("Rate limit reached")
        else:
            self.log.error("API request failed")
            self.log.debug(data)
        raise exception.StopExtraction()

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
                    uri = uris[name]
                    uris[name] = unwrap(expansions[uri])

        return objs
