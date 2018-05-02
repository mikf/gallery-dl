# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.smugmug.com/"""

from .common import Extractor, Message
from .. import text, util, exception

BASE_PATTERN = (
    r"(?:smugmug:(?!album:)(?:https?://)?([^/]+)|"
    r"(?:https?://)?([^.]+)\.smugmug\.com)")


class SmugmugExtractor(Extractor):
    """Base class for smugmug extractors"""
    category = "smugmug"
    filename_fmt = "{category}_{Owner[NickName]}_{Image[ImageKey]}.{extension}"

    def __init__(self):
        Extractor.__init__(self)
        self.api = SmugmugAPI(self)
        self.domain = None
        self.user = None

    def _resolve_user(self):
        if not self.user:
            self.user = self.api.site_user(self.domain)["NickName"]


class SmugmugAlbumExtractor(SmugmugExtractor):
    subcategory = "album"
    directory_fmt = ["{category}", "{Owner[NickName]}", "{Album[Name]}"]
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
        album = self.api.album(self.album_id, "User")
        owner = album["Uris"]["User"]

        del album["Uris"]
        del owner["Uris"]
        data = {"Album": album, "Owner": owner}

        yield Message.Version, 1
        yield Message.Directory, data

        for image in self.api.album_images(self.album_id, "LargestImage"):
            url = _apply_largest(image)
            data["Image"] = image
            yield Message.Url, url, text.nameext_from_url(url, data)


class SmugmugImageExtractor(SmugmugExtractor):
    subcategory = "image"
    directory_fmt = ["{category}", "{Owner[NickName]}"]
    archive_fmt = "{Image[ImageKey]}"
    pattern = [BASE_PATTERN + r"(?:/[^/?&#]+)+/i-([^/?&#]+)"]
    test = [("https://mikf.smugmug.com/Test/n-xnNH3s/i-L4CxBdg", {
        "url": "905bfdef52ce1a731a4eae17e9ac348511e17ae4",
        "keyword": "3fd6db2ab3d12a6d3cfc49ee57adc91fdd295a6c",
        "content": "626fe50d25fe49beeda15e116938db36e163c01f",
    })]

    def __init__(self, match):
        SmugmugExtractor.__init__(self)
        self.image_id = match.group(3)

    def items(self):
        image = self.api.image(self.image_id, "LargestImage,ImageOwner")
        owner = image["Uris"]["ImageOwner"]

        url = _apply_largest(image)

        del owner["Uris"]
        data = {"Image": image, "Owner": owner}
        text.nameext_from_url(url, data)

        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data


class SmugmugUserExtractor(SmugmugExtractor):
    subcategory = "user"
    pattern = [BASE_PATTERN + "(?:/browse)?/?$"]
    test = [
        ("https://mikf.smugmug.com/", {
            "pattern": "smugmug:album:xgkb4C$",
        }),
        ("https://mikf.smugmug.com/browse", None),
        ("smugmug:https://www.creativedogportraits.com/", {
            "pattern": "smugmug:album:txWXzs$",
        }),
        ("smugmug:www.creativedogportraits.com/", None),
        ("smugmug:www.creativedogportraits.com/browse", None),
    ]

    def __init__(self, match):
        SmugmugExtractor.__init__(self)
        self.domain = match.group(1)
        self.user = match.group(2)

    def items(self):
        self._resolve_user()
        yield Message.Version, 1
        for album in self.api.user_albums(self.user):
            uri = "smugmug:album:" + album["AlbumKey"]
            yield Message.Queue, uri, album


class SmugmugNodeExtractor(SmugmugExtractor):
    subcategory = "node"
    pattern = [BASE_PATTERN +
               r"((?:/[^/?&#a-z][^/?&#]*)+)"
               r"(?:/n-([^/?&#]+))?/?$"]
    test = [
        ("https://mikf.smugmug.com/Test/", {
            "pattern": "smugmug:album:xgkb4C$",
        }),
        ("https://mikf.smugmug.com/Test/n-xnNH3s", {
            "pattern": "smugmug:album:xgkb4C$",
        }),
        ("smugmug:https://www.creativedogportraits.com/PortfolioGallery/", {
            "pattern": "smugmug:album:txWXzs$",
        }),
    ]

    def __init__(self, match):
        SmugmugExtractor.__init__(self)
        self.domain, self.user, self.path, self.node_id = match.groups()

    def items(self):
        yield Message.Version, 1

        if self.node_id:
            node = self.api.node(self.node_id)
        else:
            self._resolve_user()
            data = self.api.user_urlpathlookup(self.user, self.path)
            node = data["Uris"]["Node"]

        nodes = (node,) if node["Type"] == "Album" else self.album_nodes(node)
        for node in nodes:
            yield Message.Queue, "smugmug:album:" + _get(node, "Album"), node

    def album_nodes(self, root):
        for node in self.api.node_children(root["NodeID"]):
            if node["Type"] == "Album":
                yield node
            elif node["Type"] == "Folder":
                yield from self.album_nodes(node)


class SmugmugAPI():
    """Minimal interface for the smugmug API v2"""
    API_DOMAIN = "api.smugmug.com"
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

        self.log = extractor.log

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
        return _unwrap(self._call("!siteuser", domain=domain)["Response"])

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
        if expands:
            endpoint += "?_expand=" + expands
        return _apply_expansions(self._call(endpoint, params), expands)

    def _pagination(self, endpoint, expands=None):
        if expands:
            endpoint += "?_expand=" + expands
        params = {"start": 1, "count": 100}

        while True:
            data = self._call(endpoint, params)
            yield from _apply_expansions_iter(data, expands)

            if "NextPage" not in data["Response"]["Pages"]:
                return
            params["start"] += params["count"]


def _apply_largest(image, delete=True):
    largest = image["Uris"]["LargestImage"]
    if delete:
        del image["Uris"]
    for key in ("Url", "Width", "Height", "MD5", "Size", "Watermarked"):
        if key in largest:
            image[key] = largest[key]
    return image["Url"]


def _get(obj, key):
    return obj["Uris"][key].rpartition("/")[2]


def _apply_expansions(data, expands):
    obj = _unwrap(data["Response"])

    if "Expansions" in data:
        expansions = data["Expansions"]
        uris = obj["Uris"]

        for name in expands.split(","):
            uri = uris[name]
            uris[name] = _unwrap(expansions[uri])

    return obj


def _apply_expansions_iter(data, expands):
    objs = _unwrap_iter(data["Response"])

    if "Expansions" in data:
        expansions = data["Expansions"]
        expands = expands.split(",")

        for obj in objs:
            uris = obj["Uris"]

            for name in expands:
                uri = uris[name]
                uris[name] = _unwrap(expansions[uri])

    return objs


def _unwrap(response):
    locator = response["Locator"]
    return response[locator] if locator in response else []


def _unwrap_iter(response):
    obj = _unwrap(response)
    if isinstance(obj, list):
        return obj
    return (obj,)
