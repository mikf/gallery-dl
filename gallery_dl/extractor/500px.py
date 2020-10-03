# -*- coding: utf-8 -*-

# Copyright 2019-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://500px.com/"""

from .common import Extractor, Message
import json


BASE_PATTERN = r"(?:https?://)?(?:web\.)?500px\.com"


class _500pxExtractor(Extractor):
    """Base class for 500px extractors"""
    category = "500px"
    directory_fmt = ("{category}", "{user[username]}")
    filename_fmt = "{id}_{name}.{extension}"
    archive_fmt = "{id}"
    root = "https://500px.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.session.headers["Referer"] = self.root + "/"

    def items(self):
        first = True
        data = self.metadata()
        yield Message.Version, 1

        for photo in self.photos():
            url = photo["images"][-1]["url"]
            photo["extension"] = photo["image_format"]
            if data:
                photo.update(data)
            if first:
                first = False
                yield Message.Directory, photo
            yield Message.Url, url, photo

    def metadata(self):
        """Returns general metadata"""

    def photos(self):
        """Returns an iterable containing all relevant photo IDs"""

    def _extend(self, edges):
        """Extend photos with additional metadata and higher resolution URLs"""
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
            "ids"                   : ",".join(
                str(edge["node"]["legacyId"]) for edge in edges),
        }

        data = self._request_api(url, params)["photos"]
        return [
            data[str(edge["node"]["legacyId"])]
            for edge in edges
        ]

    def _request_api(self, url, params, csrf_token=None):
        headers = {"Origin": self.root, "X-CSRF-Token": csrf_token}
        return self.request(url, headers=headers, params=params).json()

    def _request_graphql(self, opname, variables, query_hash):
        url = "https://api.500px.com/graphql"
        params = {
            "operationName": opname,
            "variables"    : json.dumps(variables),
            "extensions"   : '{"persistedQuery":{"version":1'
                             ',"sha256Hash":"' + query_hash + '"}}',
        }
        return self.request(url, params=params).json()["data"]


class _500pxUserExtractor(_500pxExtractor):
    """Extractor for photos from a user's photostream on 500px.com"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!photo/)(?:p/)?([^/?&#]+)/?(?:$|\?|#)"
    test = (
        ("https://500px.com/p/light_expression_photography", {
            "pattern": r"https?://drscdn.500px.org/photo/\d+/m%3D4096/v2",
            "range": "1-99",
            "count": 99,
        }),
        ("https://500px.com/light_expression_photography"),
        ("https://web.500px.com/light_expression_photography"),
    )

    def __init__(self, match):
        _500pxExtractor.__init__(self, match)
        self.user = match.group(1)

    def photos(self):
        variables = {"username": self.user, "pageSize": 20}
        photos = self._request_graphql(
            "OtherPhotosQuery", variables,
            "54524abbdc809f8d4e10d37839e8ab2d"
            "3035413688cad9c7fbece13b66637e9d",
        )["user"]["photos"]

        while True:
            yield from self._extend(photos["edges"])

            if not photos["pageInfo"]["hasNextPage"]:
                return

            variables["cursor"] = photos["pageInfo"]["endCursor"]
            photos = self._request_graphql(
                "OtherPhotosPaginationContainerQuery", variables,
                "6d31e01104456ce642a2c6fc2f936812"
                "b0f2a65c442d03e1521d769c20efe507",
            )["userByUsername"]["photos"]


class _500pxGalleryExtractor(_500pxExtractor):
    """Extractor for photo galleries on 500px.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user[username]}", "{gallery[name]}")
    pattern = (BASE_PATTERN + r"/(?!photo/)(?:p/)?"
               r"([^/?&#]+)/galleries/([^/?&#]+)")
    test = (
        ("https://500px.com/p/fashvamp/galleries/lera", {
            "url": "002dc81dee5b4a655f0e31ad8349e8903b296df6",
            "count": 3,
            "keyword": {
                "gallery": dict,
                "user": dict,
            },
        }),
        ("https://500px.com/fashvamp/galleries/lera"),
    )

    def __init__(self, match):
        _500pxExtractor.__init__(self, match)
        self.user_name, self.gallery_name = match.groups()
        self.user_id = self._photos = None

    def metadata(self):
        user = self._request_graphql(
            "ProfileRendererQuery", {"username": self.user_name},
            "4d02ff5c13927a3ac73b3eef306490508bc765956940c31051468cf30402a503",
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
            "fd367cacf9bebcdc0620bd749dbd8fc9b0ccbeb54fc76b8b4b95e66a8c0cba49",
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
                "457c66d976f56863c81795f03e98cb54"
                "3c7c6cdae7abeab8fe9e8e8a67479fa9",
            )["galleryByOwnerIdAndSlugOrToken"]["photos"]


class _500pxImageExtractor(_500pxExtractor):
    """Extractor for individual images from 500px.com"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/photo/(\d+)"
    test = ("https://500px.com/photo/222049255/queen-of-coasts", {
        "url": "fbdf7df39325cae02f5688e9f92935b0e7113315",
        "count": 1,
        "keyword": {
            "camera": "Canon EOS 600D",
            "camera_info": dict,
            "comments": list,
            "comments_count": int,
            "created_at": "2017-08-01T08:40:05+00:00",
            "description": str,
            "editored_by": None,
            "editors_choice": False,
            "extension": "jpg",
            "feature": "popular",
            "feature_date": "2017-08-01T09:58:28+00:00",
            "focal_length": "208",
            "height": 3111,
            "id": 222049255,
            "image_format": "jpg",
            "image_url": list,
            "images": list,
            "iso": "100",
            "lens": "EF-S55-250mm f/4-5.6 IS II",
            "lens_info": dict,
            "liked": None,
            "location": None,
            "location_details": dict,
            "name": "Queen Of Coasts",
            "nsfw": False,
            "privacy": False,
            "profile": True,
            "rating": float,
            "status": 1,
            "tags": list,
            "taken_at": "2017-05-04T17:36:51+00:00",
            "times_viewed": int,
            "url": "/photo/222049255/Queen-Of-Coasts-by-Olesya-Nabieva",
            "user": dict,
            "user_id": 12847235,
            "votes_count": int,
            "watermark": True,
            "width": 4637,
        },
    })

    def __init__(self, match):
        _500pxExtractor.__init__(self, match)
        self.photo_id = match.group(1)

    def photos(self):
        edges = ({"node": {"legacyId": self.photo_id}},)
        return self._extend(edges)
