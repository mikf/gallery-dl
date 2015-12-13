# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://nijie.info/"""

from .common import AsynchronousExtractor, Message
from .. import config, text

class NijieUserExtractor(AsynchronousExtractor):
    """Extract all works of a single nijie-user"""
    category = "nijie"
    directory_fmt = ["{category}", "{artist-id}"]
    filename_fmt = "{category}_{artist-id}_{image-id}_p{index:>02}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?nijie\.info/members(?:_illust)?\.php\?id=(\d+)"]
    test = [("https://nijie.info/members_illust.php?id=44", {
        "url": "585d821df4716b1098660a0be426d01db4b65f2a",
        "keyword": "30c981b9d7351ec275b9840d8bc2b4ef3da8c4b4",
    })]
    popup_url = "https://nijie.info/view_popup.php?id="

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.artist_id = match.group(1)
        self.artist_url = (
            "https://nijie.info/members_illust.php?id="
            + self.artist_id
        )
        self.session.headers["Referer"] = self.artist_url

    def items(self):
        self.login()
        data = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, data
        for image_id in self.get_image_ids():
            for image_url, image_data in self.get_image_data(image_id):
                image_data.update(data)
                yield Message.Url, image_url, image_data

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        return {
            "category": self.category,
            "artist-id": self.artist_id,
        }

    def get_image_ids(self):
        """Collect all image-ids for a specific artist"""
        page = self.request(self.artist_url).text
        return list(text.extract_iter(page, ' illust_id="', '"'))

    def get_image_data(self, image_id):
        """Get URL and metadata for images specified by 'image_id'"""
        page = self.request(self.popup_url + image_id).text
        images = list(text.extract_iter(page, '<img src="//pic', '"'))
        for index, url in enumerate(images):
            yield "https://pic" + url, text.nameext_from_url(url, {
                "count": len(images),
                "index": index,
                "image-id": image_id,
            })

    def login(self):
        """Login and obtain session cookie"""
        params = {
            "email": config.get(("extractor", self.category, "email")),
            "password": config.get(("extractor", self.category, "password")),
        }
        page = self.session.post("https://nijie.info/login_int.php", data=params).text
        if "//nijie.info/login.php" in page:
            raise Exception("login failed")
