# -*- coding: utf-8 -*-

# Copyright 2018-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.smugmug.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = (
    r"(?:smugmug:(?!album:)(?:https?://)?([^/]+)|"
    r"(?:https?://)?([\w-]+)\.smugmug\.com)")


class SmugmugExtractor(Extractor):
    """Base class for smugmug extractors"""
    category = "smugmug"
    filename_fmt = ("{category}_{User[NickName]:?/_/}"
                    "{Image[UploadKey]}_{Image[ImageKey]}.{extension}")

    def _init(self):
        self.api = self.utils().SmugmugAPI(self)
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
    example = "smugmug:album:ID"

    def __init__(self, match):
        SmugmugExtractor.__init__(self, match)
        self.album_id = match[1]

    def items(self):
        album = self.api.album(self.album_id, "User")
        user = album["Uris"].get("User") or self.utils().NullUser.copy()

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
    pattern = rf"{BASE_PATTERN}(?:/[^/?#]+)+/i-([^/?#-]+)"
    example = "https://USER.smugmug.com/PATH/i-ID"

    def __init__(self, match):
        SmugmugExtractor.__init__(self, match)
        self.image_id = match[3]

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
    pattern = rf"{BASE_PATTERN}((?:/[^/?#a-fh-mo-z][^/?#]*)*)/?$"
    example = "https://USER.smugmug.com/PATH"

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
