# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://twitter.com/"""

from .common import Extractor, Message
from .. import text


class TwitterTweetExtractor(Extractor):
    """Extractor for images from tweets on twitter.com"""
    category = "twitter"
    subcategory = "tweet"
    directory_fmt = ["{category}", "{user}"]
    filename_fmt = "{tweet-id}_{num}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.|mobile\.)?twitter\.com/"
               r"(([^/]+)/status/(\d+))"]
    test = [("https://twitter.com/PicturesEarth/status/672897688871018500", {
        "url": "d9e68d41301d2fe382eb27711dea28366be03b1a",
        "keyword": "3cd8e27026a2112008985b1b53f5e4baf4616177",
        "content": "a1f2f04cb2d8df24b1afa7a39910afda23484342",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.path, self.user, self.tid = match.groups()

    def items(self):
        self.session.headers["User-Agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64; rv:48.0) "
            "Gecko/20100101 Firefox/48.0"
        )
        page = self.request("https://twitter.com/" + self.path).text
        data = self.get_job_metadata()
        imgs = self.get_image_urls(page)
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], url in enumerate(imgs, 1):
            yield Message.Url, url + ":orig", text.nameext_from_url(url, data)

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        return {
            "user": self.user,
            "tweet-id": self.tid,
        }

    @staticmethod
    def get_image_urls(page):
        """Extract and return a list of all image-urls"""
        needle = '<img data-aria-label-part src="'
        return list(text.extract_iter(page, needle, '"'))
