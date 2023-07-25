# -*- coding: utf-8 -*-

# Copyright 2020 Leonid "Bepis" Pavel
# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://imgchest.com/"""

from .common import GalleryExtractor
from .. import text, exception


class ImagechestGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from imgchest.com"""
    category = "imagechest"
    root = "https://imgchest.com"
    pattern = r"(?:https?://)?(?:www\.)?imgchest\.com/p/([A-Za-z0-9]{11})"
    test = (
        ("https://imgchest.com/p/3na7kr3by8d", {
            "pattern": r"https://cdn\.imgchest\.com/files/\w+\.(jpg|png)",
            "keyword": {
                "count": 3,
                "gallery_id": "3na7kr3by8d",
                "num": int,
                "title": "Wizardry - Video Game From The Mid 80's",
            },
            "url": "7328ca4ec2459378d725e3be19f661d2b045feda",
            "content": "076959e65be30249a2c651fbe6090dc30ba85193",
            "count": 3
        }),
        # "Load More Files" button (#4028)
        ("https://imgchest.com/p/9p4n3q2z7nq", {
            "pattern": r"https://cdn\.imgchest\.com/files/\w+\.(jpg|png)",
            "url": "f5674e8ba79d336193c9f698708d9dcc10e78cc7",
            "count": 52,
        }),
        ("https://imgchest.com/p/xxxxxxxxxxx", {
            "exception": exception.NotFoundError,
        }),
    )

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
            self.images = self._images_api

    def metadata(self, page):
        if "Sorry, but the page you requested could not be found." in page:
            raise exception.NotFoundError("gallery")

        return {
            "gallery_id": self.gallery_id,
            "title": text.unescape(text.extr(
                page, 'property="og:title" content="', '"').strip())
        }

    def images(self, page):
        if " More Files</button>" in page:
            url = "{}/p/{}/loadAll".format(self.root, self.gallery_id)
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Origin"          : self.root,
                "Referer"         : self.gallery_url,
            }
            csrf_token = text.extr(page, 'name="csrf-token" content="', '"')
            data = {"_token": csrf_token}
            page += self.request(
                url, method="POST", headers=headers, data=data).text

        return [
            (url, None)
            for url in text.extract_iter(page, 'data-url="', '"')
        ]

    def _metadata_api(self, page):
        post = self.api.post(self.gallery_id)

        post["date"] = text.parse_datetime(
            post["created"], "%Y-%m-%dT%H:%M:%S.%fZ")
        for img in post["images"]:
            img["date"] = text.parse_datetime(
                img["created"], "%Y-%m-%dT%H:%M:%S.%fZ")

        post["gallery_id"] = self.gallery_id
        post.pop("image_count", None)
        self._image_list = post.pop("images")

        return post

    def _images_api(self, page):
        return [
            (img["link"], img)
            for img in self._image_list
        ]


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
