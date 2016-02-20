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
    """Extract all images from a tumblr-user"""
    category = "tumblr"
    subcategory = "user"
    directory_fmt = ["{category}", "{user}"]
    filename_fmt = "{category}_{user}_{id}{offset}.{extension}"
    pattern = [r"(?:https?://)?([^.]+)\.tumblr\.com(?:/page/\d+)?/?$"]
    test = [("http://demo.tumblr.com/", {
        "url": "a62b4f5dcb838645342b3ec0eb2dfb0342779699",
        "keyword": "97e812ffa3319d4e46a91f09ddfbd24c9b97015a",
        "content": "31495fdb9f84edbb7f67972746a1521456f649e2",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.user = match.group(1)

    def items(self):
        images = self.get_image_data()
        data = self.get_job_metadata(images)
        yield Message.Version, 1
        yield Message.Directory, data
        for image in images:
            url = image["photo-url-1280"]
            image.update(data)
            image = text.nameext_from_url(url, image)
            image["hash"] = text.extract(image["name"], "_", "_")[0]
            yield Message.Url, url, image

    def get_job_metadata(self, image_data):
        """Collect metadata for extractor-job"""
        data = next(image_data)
        data["category"] = self.category
        data["user"] = self.user
        del data["cname"]
        del data["description"]
        del data["feeds"]
        return data

    def get_image_data(self):
        """Yield metadata for all images"""
        params = {"start": 0, "type": "photo"}
        url = "https://{}.tumblr.com/api/read/json".format(self.user)
        while True:
            page = self.request(url, params=params).text
            data = json.loads(page[22:-2])
            if params["start"] == 0:
                yield data["tumblelog"]
            for post in data["posts"]:
                photos = post["photos"]
                del post["photos"]
                if photos:
                    for photo in photos:
                        post.update(photo)
                        yield post
                else:
                    post["offset"] = "o1"
                    yield post
            if len(data["posts"]) < 20:
                break
            params["start"] += 20
