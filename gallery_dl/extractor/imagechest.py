# -*- coding: utf-8 -*-

# Copyright 2020 Leonid "Bepis" Pavel
# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://imgchest.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?imgchest\.com"


class ImagechestGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from imgchest.com"""
    category = "imagechest"
    root = "https://imgchest.com"
    pattern = BASE_PATTERN + r"/p/([A-Za-z0-9]{11})"
    example = "https://imgchest.com/p/abcdefghijk"

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = self.root + "/p/" + self.gallery_id
        GalleryExtractor.__init__(self, match, url)

    def _init(self):
        access_token = self.config("access-token")
        if access_token:
            self.api = ImagechestAPI(self, access_token)
            self.gallery_url = None
            self.metadata = self._metadata_api

    def metadata(self, page):
        try:
            data = util.json_loads(text.unescape(text.extr(
                page, 'data-page="', '"')))
            post = data["props"]["post"]
        except Exception:
            if "<title>Not Found</title>" in page:
                raise exception.NotFoundError("gallery")
            self.files = ()
            return {}

        self.files = post.pop("files", ())
        post["gallery_id"] = self.gallery_id
        post["tags"] = [tag["name"] for tag in post["tags"]]

        return post

    def _metadata_api(self, page):
        post = self.api.post(self.gallery_id)

        post["date"] = text.parse_datetime(
            post["created"], "%Y-%m-%dT%H:%M:%S.%fZ")
        for img in post["images"]:
            img["date"] = text.parse_datetime(
                img["created"], "%Y-%m-%dT%H:%M:%S.%fZ")

        post["gallery_id"] = self.gallery_id
        post.pop("image_count", None)
        self.files = post.pop("images")

        return post

    def images(self, page):
        try:
            return [
                (file["link"], file)
                for file in self.files
            ]
        except Exception:
            return ()


class ImagechestUserExtractor(Extractor):
    """Extractor for imgchest.com user profiles"""
    category = "imagechest"
    subcategory = "user"
    root = "https://imgchest.com"
    pattern = BASE_PATTERN + r"/u/([^/?#]+)"
    example = "https://imgchest.com/u/USER"

    def items(self):
        url = self.root + "/api/posts"
        params = {
            "page"    : 1,
            "sort"    : "new",
            "tag"     : "",
            "q"       : "",
            "username": text.unquote(self.groups[0]),
            "nsfw"    : "true",
        }

        while True:
            try:
                data = self.request(url, params=params).json()["data"]
            except (TypeError, KeyError):
                return

            if not data:
                return

            for gallery in data:
                gallery["_extractor"] = ImagechestGalleryExtractor
                yield Message.Queue, gallery["link"], gallery

            params["page"] += 1


class ImagechestAPI():
    """Interface for the Image Chest API

    https://imgchest.com/docs/api/1.0/general/overview
    """
    root = "https://api.imgchest.com"

    def __init__(self, extractor, access_token):
        self.extractor = extractor
        self.headers = {"Authorization": "Bearer " + access_token}

    def file(self, file_id):
        endpoint = "/v1/file/" + file_id
        return self._call(endpoint)

    def post(self, post_id):
        endpoint = "/v1/post/" + post_id
        return self._call(endpoint)

    def user(self, username):
        endpoint = "/v1/user/" + username
        return self._call(endpoint)

    def _call(self, endpoint):
        url = self.root + endpoint

        while True:
            response = self.extractor.request(
                url, headers=self.headers, fatal=None, allow_redirects=False)

            if response.status_code < 300:
                return response.json()["data"]

            elif response.status_code < 400:
                raise exception.AuthenticationError("Invalid API access token")

            elif response.status_code == 429:
                self.extractor.wait(seconds=600)

            else:
                self.extractor.log.debug(response.text)
                raise exception.StopExtraction("API request failed")
