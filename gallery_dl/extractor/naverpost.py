# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://post.naver.com/"""

from .common import Extractor, Message
from .. import text, exception
import json
import re

BASE_PATTERN = r"(?:https?://)?(?:m\.)?post\.naver\.com"


class NaverpostExtractor(Extractor):
    """Base class for naver post extractors"""
    category = "naverpost"
    root = "https://post.naver.com"
    request_interval = (0.5, 1.5)

    def _call(self, url, params=None):
        if params is None:
            params = {}
        while True:
            try:
                return self.request(url, params=params)
            except exception.HttpError as exc:
                if exc.status == 401:
                    raise exception.AuthenticationError()
                if exc.status == 403:
                    raise exception.AuthorizationError()
                if exc.status == 404:
                    raise exception.NotFoundError(self.subcategory)
                self.log.debug(exc)
                return

    def _pagination(self, url, params=None):
        if params is None:
            params = {}
        while True:
            res = self._call(url, params).text
            # the `html` string in the response contains escaped single quotes,
            # which would throw a JSONDecodeError exception
            res = json.loads(res.replace(r"\'", "'"))
            urls = []
            endpoints = text.extract_iter(
                res["html"], '<div class="text_area">\n<a href="', '"')
            for endpoint in endpoints:
                urls.append(self.root + endpoint)
            yield from urls
            if "nextFromNo" not in res:
                return
            params["fromNo"] = res["nextFromNo"]


class NaverpostPostExtractor(NaverpostExtractor):
    """Extractor for posts on post.naver.com"""
    subcategory = "post"
    filename_fmt = "{image[id]}.{extension}"
    directory_fmt = ("{category}", "{author}", "{volume_no}")
    archive_fmt = "{image[id]}"
    pattern = (BASE_PATTERN + r"/viewer/postView\.(naver|nhn)"
               r"\?volumeNo=(\d+)(?:&.+)?")
    example = "https://post.naver.com/viewer/postView.naver?volumeNo=12345"

    def __init__(self, match):
        NaverpostExtractor.__init__(self, match)
        self.url = match.group(0)
        self.page_ext = match.group(1)
        self.volume_no = match.group(2)

    def metadata(self, page):
        data = {
            "title": text.unescape(
                text.extr(page, '"og:title" content="', '"')),
            "description": text.unescape(
                text.extr(page, '"og:description" content="', '"')),
            "author": text.extr(page, '"og:author" content="', '"'),
            "date": text.parse_datetime(
                text.extr(page, '"og:createdate" content="', '"'),
                format="%Y.%m.%d. %H:%M:%S", utcoffset=9),
            "volume_no": self.volume_no,
            "views": text.parse_int(
                (text.extr(page, '<span class="post_view">', ' ') or
                 text.extr(page, '<span class="se_view" style="">', ' ')
                 ).replace(",", "")),
            "url": self.url,
        }
        return data

    def items(self):
        page = self._call(self.url).text
        data = self.metadata(page)

        yield Message.Directory, data

        image_classes = ("img_attachedfile", "se_mediaImage")
        image_query = r"\?type=w\d+$"
        for image in text.extract_iter(page, "<img", ">"):
            img = {
                "id": text.extr(image, ' id="', '"'),
                "title": text.extr(image, ' title="', '"'),
                "attachment-id": text.extr(
                    image, ' data-attachment-id="', '"'),
                "alt": None,
            }
            classes = text.extr(image, ' class="', '"').split()
            if not any(item in classes for item in image_classes):
                continue
            url = text.extr(image, ' data-src="', '"')
            if not re.search(image_query, url):
                continue
            url = re.sub(image_query, "", url)
            img["url"] = url
            alt = text.extr(image, ' alt="', '"')
            if alt and alt.endswith(".jpg"):
                img["alt"] = alt
                data["filename"], _, data["extension"] = alt.rpartition(".")
            else:
                text.nameext_from_url(text.unquote(url), data)
            data["image"] = img
            yield Message.Url, url, data


class NaverpostUserExtractor(NaverpostExtractor):
    """Extractor for all posts from a user on post.naver.com"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/my\.naver\?memberNo=(\d+)"
    example = "https://post.naver.com/my.naver?memberNo=12345"

    def __init__(self, match):
        NaverpostExtractor.__init__(self, match)
        self.member_no = match.group(1)

    def items(self):
        data = {"_extractor": NaverpostPostExtractor}
        endpoint = self.root + "/async/my.naver"
        params = {"memberNo": self.member_no}
        posts = self._pagination(endpoint, params)
        for url in posts:
            yield Message.Queue, url, data
