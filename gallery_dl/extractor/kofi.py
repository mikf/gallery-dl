# -*- coding: utf-8 -*-

# Copyright 2022 Benjamin Ryan
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://ko-fi.com/"""

from .common import Extractor, Message
from .. import text

from os.path import basename
import time


class KofiExtractor(Extractor):
    """Extractor for all images from accounts on ko-fi.com"""
    category = "kofi"
    root = "https://ko-fi.com"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{id}.{extension}"
    cookiedomain = ".ko-fi.com"
    pattern = r"(?:https?://)?ko-fi\.com/(\w+)"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)

    def items(self):
        url = "{}/{}/gallery".format(self.root, self.user)
        page = self.request(url).text
        # Author identifier for API requests
        self.pageId = text.extr(page, 'buttonId: \'', '\'')

        yield Message.Directory, {"user": self.user}

        start = 0
        while True:
            posts = self._gallery(start)
            if len(posts) == 0:
                break
            for post in posts:
                if "image" in post and not self._locked(post):
                    yield Message.Url, post["image"], post
            start += 20

    def _gallery(self, start):
        timestamp = int(time.time())
        url = "{}/Buttons/LoadPageGallery?buttonId={}&start={}&_={}"\
            .format(self.root, self.pageId, start, timestamp)
        page = self.request(url).text
        return self.posts(page)

    def posts(self, page):
        """Build a list of all post-objects"""
        needle = '<li '
        posts = page.split(needle)
        if len(posts) > 0 and posts[0] == "":
            posts = posts[1:]
        return [self.parse(post) for post in posts]

    def parse(self, post):
        """Build post-object by extracting data from an HTML post"""
        return self._extract_post(post)

    def _extract_post(self, post):
        data = text.extract_all(post, (
            ("id"  , 'class=\'gi-', ' '),
            ("width"   , 'data-width=\'', 'px'),
            ("image", 'src=\'', '\''),
        ))[0]
        # Use full resolution image
        data["image"] = data["image"].replace('post/', 'display/')
        data["filename"], data["extension"] = basename(data["image"])\
            .split("?")[0].rsplit(".", 1)
        data["width"] = text.parse_int(data["width"])\
            if data["width"] is None else 0
        return data

    def _locked(self, post):
        locked_filenames = ["supporteronly", "supporteronly2"]
        return post["filename"] in locked_filenames
