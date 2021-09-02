# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://seiso.party/"""

from .common import Extractor, Message
from .. import text
import re


class SeisopartyExtractor(Extractor):
    """Base class for seisoparty extractors"""
    category = "seisoparty"
    root = "https://seiso.party"
    directory_fmt = ("{category}", "{service}", "{username}")
    filename_fmt = "{id}_{title}_{num:>02}_{filename}.{extension}"
    archive_fmt = "{service}_{user}_{id}_{num}"
    cookiedomain = ".seiso.party"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user_name = None
        self._find_files = re.compile(
            r'href="(https://cdn(?:-\d)?\.seiso\.party/files/[^"]+)').findall

    def items(self):
        self._prepare_ddosguard_cookies()

        for post in self.posts():
            files = post.pop("files")
            yield Message.Directory, post
            for post["num"], url in enumerate(files, 1):
                yield Message.Url, url, text.nameext_from_url(url, post)

    def _parse_post(self, page, post_id):
        extr = text.extract_from(page)
        return {
            "service" : self.service,
            "user"    : self.user_id,
            "username": self.user_name,
            "id"      : post_id,
            "date"    : text.parse_datetime(extr(
                '<div class="margin-bottom-15 minor-text">', '<'),
                "%Y-%m-%d %H:%M:%S %Z"),
            "title"   : text.unescape(extr('class="post-title">', '<')),
            "content" : text.unescape(extr("\n<p>\n", "\n</p>\n").strip()),
            "files"   : self._find_files(page),
        }


class SeisopartyUserExtractor(SeisopartyExtractor):
    """Extractor for all posts from a seiso.party user listing"""
    subcategory = "user"
    pattern = r"(?:https?://)?seiso\.party/artists/([^/?#]+)/([^/?#]+)"
    test = (
        ("https://seiso.party/artists/fanbox/21", {
            "pattern": r"https://cdn\.seiso\.party/files/fanbox/\d+/",
            "count": ">=15",
            "keyword": {
                "content": str,
                "date": "type:datetime",
                "id": r"re:\d+",
                "num": int,
                "service": "fanbox",
                "title": str,
                "user": "21",
                "username": "雨",
            },
        }),
    )

    def __init__(self, match):
        SeisopartyExtractor.__init__(self, match)
        self.service, self.user_id = match.groups()

    def posts(self):
        url = "{}/artists/{}/{}".format(self.root, self.service, self.user_id)
        page = self.request(url).text
        self.user_name, pos = text.extract(page, '<span class="title">', '<')

        url = self.root + text.extract(
            page, 'href="', '"', page.index('id="content"', pos))[0]
        response = self.request(url)
        headers = {"Referer": url}

        while True:
            yield self._parse_post(response.text, url.rpartition("/")[2])
            response = self.request(url + "/next", headers=headers)
            if url == response.url:
                return
            url = headers["Referer"] = response.url


class SeisopartyPostExtractor(SeisopartyExtractor):
    """Extractor for a single seiso.party post"""
    subcategory = "post"
    pattern = r"(?:https?://)?seiso\.party/post/([^/?#]+)/([^/?#]+)/([^/?#]+)"
    test = (
        ("https://seiso.party/post/fanbox/21/371", {
            "url": "75f13b92de0ce399b6163c3de18f1f36011c2366",
            "count": 2,
            "keyword": {
                "content": "この前描いためぐるちゃんのPSDファイルです。<br/>"
                           "どうぞよろしくお願いします。",
                "date": "dt:2021-05-06 12:38:31",
                "extension": "re:psd|jpg",
                "filename": "re:backcourt|ffb2ccb7a3586d05f9a4620329dd131e",
                "id": "371",
                "num": int,
                "service": "fanbox",
                "title": "MEGURU.PSD",
                "user": "21",
                "username": "雨",
            },
        }),
        ("https://seiso.party/post/patreon/429/95949", {
            "pattern": r"https://cdn-2\.seiso\.party/files/patreon/95949/",
            "count": 2,
        }),
    )

    def __init__(self, match):
        SeisopartyExtractor.__init__(self, match)
        self.service, self.user_id, self.post_id = match.groups()

    def posts(self):
        url = "{}/artists/{}/{}".format(self.root, self.service, self.user_id)
        page = self.request(url).text
        self.user_name, pos = text.extract(page, '<span class="title">', '<')

        url = "{}/post/{}/{}/{}".format(
            self.root, self.service, self.user_id, self.post_id)
        return (self._parse_post(self.request(url).text, self.post_id),)
