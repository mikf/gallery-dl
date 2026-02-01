# -*- coding: utf-8 -*-

# Copyright 2019-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://500px.com/"""

from .common import Extractor, Message
from .. import util

BASE_PATTERN = r"(?:https?://)?(?:web\.)?500px\.com"


class _500pxExtractor(Extractor):
    """Base class for 500px extractors"""
    category = "500px"
    directory_fmt = ("{category}", "{user[username]}")
    filename_fmt = "{id}_{name}.{extension}"
    archive_fmt = "{id}"
    root = "https://500px.com"
    cookies_domain = ".500px.com"

    def items(self):
        data = self.metadata()

        for photo in self.photos():
            url = photo["images"][-1]["url"]
            photo["extension"] = photo["image_format"]
            if data:
                photo.update(data)
            yield Message.Directory, "", photo
            yield Message.Url, url, photo

    def metadata(self):
        """Returns general metadata"""

    def photos(self):
        """Returns an iterable containing all relevant photo IDs"""

    def _extend(self, edges):
        """Extend photos with additional metadata and higher resolution URLs"""
        ids = [str(edge["node"]["legacyId"]) for edge in edges]

        url = "https://api.500px.com/v1/photos"
        params = {
            "expanded_user_info"    : "true",
            "include_tags"          : "true",
            "include_geo"           : "true",
            "include_equipment_info": "true",
            "vendor_photos"         : "true",
            "include_licensing"     : "true",
            "include_releases"      : "true",
            "liked_by"              : "1",
            "following_sample"      : "100",
            "image_size"            : "4096",
            "ids"                   : ",".join(ids),
        }

        photos = self._request_api(url, params)["photos"]
        return [
            photos[pid] for pid in ids
            if pid in photos or
            self.log.warning("Unable to fetch photo %s", pid)
        ]

    def _request_api(self, url, params):
        headers = {
            "Origin": self.root,
            "x-csrf-token": self.cookies.get(
                "x-csrf-token", domain=".500px.com"),
        }
        return self.request_json(url, headers=headers, params=params)

    def _request_graphql(self, opname, variables):
        url = "https://api.500px.com/graphql"
        headers = {
            "x-csrf-token": self.cookies.get(
                "x-csrf-token", domain=".500px.com"),
        }
        data = {
            "operationName": opname,
            "variables"    : util.json_dumps(variables),
            "query"        : self.utils("graphql", opname),
        }
        return self.request_json(
            url, method="POST", headers=headers, json=data)["data"]


class _500pxUserExtractor(_500pxExtractor):
    """Extractor for photos from a user's photostream on 500px.com"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!photo/|liked)(?:p/)?([^/?#]+)/?(?:$|[?#])"
    example = "https://500px.com/USER"

    def __init__(self, match):
        _500pxExtractor.__init__(self, match)
        self.user = match[1]

    def photos(self):
        variables = {"username": self.user, "pageSize": 20}
        photos = self._request_graphql(
            "OtherPhotosQuery", variables,
        )["user"]["photos"]

        while True:
            yield from self._extend(photos["edges"])

            if not photos["pageInfo"]["hasNextPage"]:
                return

            variables["cursor"] = photos["pageInfo"]["endCursor"]
            photos = self._request_graphql(
                "OtherPhotosPaginationContainerQuery", variables,
            )["userByUsername"]["photos"]


class _500pxGalleryExtractor(_500pxExtractor):
    """Extractor for photo galleries on 500px.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user[username]}", "{gallery[name]}")
    pattern = (BASE_PATTERN + r"/(?!photo/)(?:p/)?"
               r"([^/?#]+)/galleries/([^/?#]+)")
    example = "https://500px.com/USER/galleries/GALLERY"

    def __init__(self, match):
        _500pxExtractor.__init__(self, match)
        self.user_name, self.gallery_name = match.groups()
        self.user_id = self._photos = None

    def metadata(self):
        user = self._request_graphql(
            "ProfileRendererQuery", {"username": self.user_name},
        )["profile"]
        self.user_id = str(user["legacyId"])

        variables = {
            "galleryOwnerLegacyId": self.user_id,
            "ownerLegacyId"       : self.user_id,
            "slug"                : self.gallery_name,
            "token"               : None,
            "pageSize"            : 20,
        }
        gallery = self._request_graphql(
            "GalleriesDetailQueryRendererQuery", variables,
        )["gallery"]

        self._photos = gallery["photos"]
        del gallery["photos"]
        return {
            "gallery": gallery,
            "user"   : user,
        }

    def photos(self):
        photos = self._photos
        variables = {
            "ownerLegacyId": self.user_id,
            "slug"         : self.gallery_name,
            "token"        : None,
            "pageSize"     : 20,
        }

        while True:
            yield from self._extend(photos["edges"])

            if not photos["pageInfo"]["hasNextPage"]:
                return

            variables["cursor"] = photos["pageInfo"]["endCursor"]
            photos = self._request_graphql(
                "GalleriesDetailPaginationContainerQuery", variables,
            )["galleryByOwnerIdAndSlugOrToken"]["photos"]


class _500pxFavoriteExtractor(_500pxExtractor):
    """Extractor for favorite 500px photos"""
    subcategory = "favorite"
    pattern = BASE_PATTERN + r"/liked/?$"
    example = "https://500px.com/liked"

    def photos(self):
        variables = {"pageSize": 20}
        photos = self._request_graphql(
            "LikedPhotosQueryRendererQuery", variables,
        )["likedPhotos"]

        while True:
            yield from self._extend(photos["edges"])

            if not photos["pageInfo"]["hasNextPage"]:
                return

            variables["cursor"] = photos["pageInfo"]["endCursor"]
            photos = self._request_graphql(
                "LikedPhotosPaginationContainerQuery", variables,
            )["likedPhotos"]


class _500pxImageExtractor(_500pxExtractor):
    """Extractor for individual images from 500px.com"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/photo/(\d+)"
    example = "https://500px.com/photo/12345/TITLE"

    def __init__(self, match):
        _500pxExtractor.__init__(self, match)
        self.photo_id = match[1]

    def photos(self):
        edges = ({"node": {"legacyId": self.photo_id}},)
        return self._extend(edges)
