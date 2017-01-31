# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract comic issues and entire comics from http://readcomics.tv/"""

from .common import Extractor, Message
from .. import text


class ReadcomicsComicExtractor(Extractor):
    """Extractor for comics from readcomics.tv"""
    category = "readcomics"
    subcategory = "comic"
    pattern = [(r"(?:https?://)?(?:www\.)?(readcomics\.(?:tv|net)/"
                r"comic/[^/]+)/?$")]
    test = [("http://readcomics.tv/comic/hellboy", {
        "url": "f3d53c45a08e068210bc1d5b24810f325d115383",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = "https://" + match.group(1)

    def items(self):
        yield Message.Version, 1
        for issue in self.get_issues():
            yield Message.Queue, issue

    def get_issues(self):
        """Return a list of all comic-issue urls"""
        page = self.request(self.url).text
        return text.extract_iter(page, '<a  class="ch-name" href="', '"')


class ReadcomicsIssueExtractor(Extractor):
    """Extractor for comic-issues from readcomics.tv"""
    category = "readcomics"
    subcategory = "issue"
    directory_fmt = ["{category}", "{comic}", "{issue:>03}"]
    filename_fmt = "{comic}_{issue:>03}_{page:>03}.{extension}"
    pattern = [(r"(?:https?://)?(?:www\.)?readcomics\.(?:tv|net)/"
                r"([^/]+)/chapter-(\d+)")]
    test = [("http://readcomics.tv/hellboy/chapter-1", {
        "url": "22c216fce559cdc9151261d5a76c270a2f7729ca",
        "keyword": "8cc155230e643df67cc863ac5c4742ef4a92e2fd",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = "https://readcomics.tv/{}/chapter-{}/full".format(
            *match.groups()
        )

    def items(self):
        page = self.request(self.url).text
        data = self.get_job_metadata(page)
        imgs = self.get_image_urls(page)
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"], url in enumerate(imgs, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    @staticmethod
    def get_job_metadata(page):
        """Collect metadata for extractor-job"""
        info = text.extract(page, "<title>", " - Read ")[0].rsplit(maxsplit=1)
        return {
            "comic": info[0],
            "issue": info[1][1:],
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def get_image_urls(page):
        """Extract list of all image-urls for a comic-issue"""
        needle = ('class="chapter_img" style="margin-bottom: '
                  '20px; max-width: 100%;" src="')
        return list(text.extract_iter(page, needle, '"'))
