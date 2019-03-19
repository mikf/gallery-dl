# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://500px.com/"""

from .common import Extractor, Message
from .. import text


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
            fmt = photo["image_format"]
            photo["extension"] = "jpg" if fmt == "jpeg" else fmt
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

    def _extend(self, photos):
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
            "image_size"            : "32768",
            "ids"                   : ",".join(str(p["id"]) for p in photos),
        }

        data = self._api_call(url, params)["photos"]
        for photo in photos:
            pid = str(photo["id"])
            photo.update(data[pid])
        return photos

    def _api_call(self, url, params, csrf_token=None):
        headers = {"Origin": self.root, "X-CSRF-Token": csrf_token}
        return self.request(url, headers=headers, params=params).json()

    def _pagination(self, url, params, csrf):
        params["page"] = 1
        while True:
            data = self._api_call(url, params, csrf)
            yield from self._extend(data["photos"])

            if params["page"] >= data["total_pages"]:
                return
            params["page"] += 1


class _500pxUserExtractor(_500pxExtractor):
    """Extractor for photos from a user's photostream on 500px.com"""
    subcategory = "user"
    pattern = (r"(?:https?://)?500px\.com"
               r"/(?!photo/)([^/?&#]+)/?(?:$|\?|#)")
    test = ("https://500px.com/light_expression_photography", {
        "pattern": r"https?://drscdn.500px.org/photo/\d+/m%3D5000/v2",
        "range": "1-99",
        "count": 99,
    })

    def __init__(self, match):
        _500pxExtractor.__init__(self, match)
        self.user = match.group(1)

    def photos(self):
        # get csrf token and user id from webpage
        url = "{}/{}".format(self.root, self.user)
        page = self.request(url).text
        csrf_token, pos = text.extract(page, 'csrf-token" content="', '"')
        user_id   , pos = text.extract(page, '/user/', '"', pos)

        # get user photos
        url = "https://api.500px.com/v1/photos"
        params = {
            "feature"       : "user",
            "stream"        : "photos",
            "rpp"           : "50",
            "user_id"       : user_id,
        }
        return self._pagination(url, params, csrf_token)


class _500pxGalleryExtractor(_500pxExtractor):
    """Extractor for photo galleries on 500px.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user[username]}", "{gallery[name]}")
    pattern = (r"(?:https?://)?500px\.com"
               r"/(?!photo/)([^/?&#]+)/galleries/([^/?&#]+)")
    test = ("https://500px.com/fashvamp/galleries/lera", {
        "url": "8a520272ece83278166b4f8556f9c9da43c43c45",
        "count": 3,
        "keyword": {
            "gallery": dict,
            "user": dict,
        },
    })

    def __init__(self, match):
        _500pxExtractor.__init__(self, match)
        self.user_name, self.gallery_name = match.groups()
        self.user_id = self.gallery_id = self.csrf_token = None

    def metadata(self):
        # get csrf token and user id from webpage
        url = "{}/{}/galleries/{}".format(
            self.root, self.user_name, self.gallery_name)
        page = self.request(url).text
        self.csrf_token, pos = text.extract(page, 'csrf-token" content="', '"')
        self.user_id   , pos = text.extract(page, 'App.CuratorId =', '\n', pos)
        self.user_id = self.user_id.strip()

        # get gallery metadata; transform gallery name into id
        url = "https://api.500px.com/v1/users/{}/galleries/{}".format(
            self.user_id, self.gallery_name)
        params = {
            #  "include_user": "true",
            "include_cover": "1",
            "cover_size": "2048",
        }
        data = self._api_call(url, params, self.csrf_token)
        self.gallery_id = data["gallery"]["id"]
        return data

    def photos(self):
        url = "https://api.500px.com/v1/users/{}/galleries/{}/items".format(
            self.user_id, self.gallery_id)
        params = {
            "sort"             : "position",
            "sort_direction"   : "asc",
            "rpp"              : "50",
        }
        return self._pagination(url, params, self.csrf_token)


class _500pxImageExtractor(_500pxExtractor):
    """Extractor for individual images from 500px.com"""
    subcategory = "image"
    pattern = r"(?:https?://)?500px\.com/photo/(\d+)"
    test = ("https://500px.com/photo/222049255/queen-of-coasts", {
        "url": "d1eda7afeaa589f71f05b9bb5c0694e3ffb357cd",
        "count": 1,
        "keyword": {
            "camera": "Canon EOS 600D",
            "camera_info": dict,
            "collections_count": int,
            "comments": list,
            "comments_count": int,
            "converted": False,
            "converted_bits": int,
            "created_at": "2017-08-01T04:40:05-04:00",
            "crop_version": 0,
            "description": str,
            "editored_by": dict,
            "editors_choice": False,
            "extension": "jpg",
            "favorites_count": int,
            "feature": "popular",
            "feature_date": "2017-08-01T09:58:28+00:00",
            "focal_length": "208",
            "height": 3111,
            "id": 222049255,
            "image_format": "jpeg",
            "image_url": str,
            "images": list,
            "iso": "100",
            "lens": "EF-S55-250mm f/4-5.6 IS II",
            "lens_info": dict,
            "license_type": 0,
            "licensed_at": None,
            "liked": False,
            "location": None,
            "location_details": dict,
            "name": "Queen Of Coasts",
            "nsfw": False,
            "privacy": False,
            "profile": True,
            "rating": float,
            "sales_count": int,
            "status": 1,
            "store_download": False,
            "store_height": 3111,
            "store_width": 4637,
            "tags": list,
            "taken_at": "2017-05-04T13:36:51-04:00",
            "times_viewed": int,
            "url": "/photo/222049255/queen-of-coasts-by-olesya-nabieva",
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
        photos = ({"id": self.photo_id},)
        return self._extend(photos)
