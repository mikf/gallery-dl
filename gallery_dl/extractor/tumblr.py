# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.tumblr.com/"""

from .common import Extractor, Message
from .. import text
import json


class TumblrUserExtractor(Extractor):
    """Extractor for all images from a tumblr-user"""
    category = "tumblr"
    subcategory = "user"
    directory_fmt = ["{category}", "{user}"]
    filename_fmt = "{category}_{user}_{id}{offset}.{extension}"
    pattern = [r"(?:https?://)?([^.]+)\.tumblr\.com(?:/page/\d+)?/?$"]
    test = [("http://demo.tumblr.com/", {
        "url": "5c113da25a605b7449de8ca1606eec5502b4dc9f",
        "keyword": "8704a9bbb65b6e52dc1ccdf2c2449bd4abe3d389",
        "content": "31495fdb9f84edbb7f67972746a1521456f649e2",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.user = match.group(1)
        self.api_url = "https://{}.tumblr.com/api/read/json".format(self.user)
        self.api_params = {"start": 0, "type": "photo"}

    def items(self):
        images = self.get_image_data()
        data = self.get_job_metadata(images)
        yield Message.Version, 1
        yield Message.Directory, data
        for image in images:
            url = image["photo-url-1280"]
            self.delete_keywords(image)
            image.update(data)
            image = text.nameext_from_url(url, image)
            image["hash"] = text.extract(image["name"], "_", "_")[0]
            yield Message.Url, url, image

    def get_job_metadata(self, image_data):
        """Collect metadata for extractor-job"""
        data = next(image_data)
        data["user"] = self.user
        del data["cname"]
        del data["description"]
        del data["feeds"]
        return data

    def get_image_data(self):
        """Yield metadata for all images from a user"""
        params = self.api_params.copy()
        while True:
            page = self.request(self.api_url, params=params).text
            data = json.loads(page[22:-2])
            if params["start"] == 0:
                yield data["tumblelog"]
            for post in data["posts"]:
                yield from self.get_images_from_post(post)
            if len(data["posts"]) < 20:
                break
            params["start"] += 20

    @staticmethod
    def get_images_from_post(post):
        """Yield all images from a single post"""
        try:
            photos = post["photos"]
        except KeyError:
            return
        del post["photos"]
        if photos:
            for photo in photos:
                post.update(photo)
                yield post
        else:
            post["offset"] = "o1"
            yield post

    @staticmethod
    def delete_keywords(data):
        """Delete unnecessary keywords from dict"""
        keys = [
            k for k in data.keys()
            if k.startswith("photo-url-") or k.endswith("-button")
        ]
        for key in keys:
            del data[key]


class TumblrPostExtractor(TumblrUserExtractor):
    """Extractor for images from a single post on tumblr"""
    subcategory = "post"
    pattern = [r"(?:https?://)?([^.]+)\.tumblr\.com/post/(\d+)"]
    test = [("http://demo.tumblr.com/post/459265350", {
        "url": "5c113da25a605b7449de8ca1606eec5502b4dc9f",
        "keyword": "821236db342fb0d1bf8a177ca3108349168e6cd0",
    })]

    def __init__(self, match):
        TumblrUserExtractor.__init__(self, match)
        self.api_params["id"] = match.group(2)


class TumblrTagExtractor(TumblrUserExtractor):
    """Extractor for images from a tumblr-user by tag"""
    subcategory = "tag"
    pattern = [r"(?:https?://)?([^.]+)\.tumblr\.com/tagged/(.+)"]
    test = [("http://demo.tumblr.com/tagged/Times Square", {
        "url": "5c113da25a605b7449de8ca1606eec5502b4dc9f",
        "keyword": "e182759d3a26c9f72ccc8ddc22a382aad598d6dc",
    })]

    def __init__(self, match):
        TumblrUserExtractor.__init__(self, match)
        self.api_params["tagged"] = match.group(2)
