# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://whentai.com/"""

from .common import Extractor, Message
from .. import text

class WhentaiUserExtractor(Extractor):
    """Extractor for images of a whentai-user"""
    category = "whentai"
    subcategory = "user"
    directory_fmt = ["{category}", "{user}"]
    filename_fmt = "{category}_{image-id:>05}_{title}.{extension}"
    pattern = [(r"(?:https?://)?(?:www\.)?whentai\.com/"
                r"(?:users|uploads)/(\d+)(?:/([^/?]+))?")]

    def __init__(self, match):
        Extractor.__init__(self)
        self.userid, self.user = match.groups()
        self.url = "http://whentai.com/uploads/" + self.userid
        self.session.headers["Referer"] = self.url

    def items(self):
        data = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, data
        for url, image in self.get_images():
            data.update(image)
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        if not self.user:
            page = self.request(self.url).text
            self.user = text.extract(page, ' alt="', '"')[0]
        return {
            "user": self.user,
            "user-id": self.userid,
        }

    def get_images(self):
        data = {"type": "image", "cnt": "50", "paid": "0", "from": "100000",
                "author": self.user, "post": "1"}
        while True:
            pos = 0
            page = self.request("http://whentai.com/ajax/getuploadslist",
                                method="POST", data=data).text
            if not page:
                return
            for _ in range(50):
                imageid, pos = text.extract(page, 'data-last-id="', '"', pos)
                if not imageid:
                    return
                url  , pos = text.extract(page, 'src="', '"', pos)
                title, pos = text.extract(page, 'alt="', '"', pos)
                yield url.replace("/t2", "/"), {
                    "image-id": imageid,
                    "title": title,
                }
            data["from"] = imageid


class WhentaiImageExtractor(Extractor):
    """Extractor for single images from whentai.com"""
    category = "whentai"
    subcategory = "image"
    directory_fmt = ["{category}", "{user}"]
    filename_fmt = "{category}_{image-id:>05}_{title}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?whentai\.com/view/(\d+)"]

    def __init__(self, match):
        Extractor.__init__(self)
        self.imageid = match.group(1)
        self.url = "http://whentai.com/view/" + self.imageid
        self.session.headers["Referer"] = self.url

    def items(self):
        data = self.get_image_metadata()
        url  = self.get_image_url(data["user"])
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data

    def get_image_url(self, user):
        data = {"type": "image", "cnt": "1", "paid": "0", "post": "1",
                "from": str(int(self.imageid) + 1), "author": user.replace("_", " ")}
        page = self.request("http://whentai.com/ajax/getuploadslist",
                            method="POST", data=data).text
        return text.extract(page, 'src="', '"')[0].replace("/t2", "/")

    def get_image_metadata(self):
        """Collect url and metadata for image"""
        page = self.request(self.url).text
        return text.extract_all(page, (
            ("title"  , '<li class="box1">\n', ' </li>'),
            ("user-id", '/users/', '/'),
            ("user"   , '', '"'),
        ), values={"image-id": self.imageid})[0]
