# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://kissjav.com"""

from .common import GalleryExtractor, Extractor, Message
from .. import text

# {} is for category, one of [album, video]
BASE_PATTERN = r"(?:https?://)?kissjav\.com/({})/(\d+)/([a-zA-Z0-9_-]+)(?:/|$)"

class KissjavExtractor(Extractor):
    """Base class for Kissjav Extractor"""
    category = "kissjav"
    root = "https://kissjav.com"
    directory_fmt = ("{category}", "{title}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{id}_{filename}"

    def parse_page(self, url):
        page = self.request(url).text
        extr = text.extract_from(page)

        data = {
            "title": extr('<h1 class="title">', '</h1>'),
            "uploader": extr('<em>', '</em>').replace('\n', '').strip(),
        }

        return page, data


class KissjavAlbumExtractor(GalleryExtractor, KissjavExtractor):
    subcategory = "album"
    pattern = BASE_PATTERN.format("album")
    example = "https://kissjav.com/album/717/no101-3-22/"
    media_url_fmt = "{}/get_image".format(KissjavExtractor.root)

    def __init__(self, match):
        self.gallery_id = match.group(2)
        self.slug = match.group(3)
        self.gallery_url = "{}/album/{}/{}".format(self.root, self.gallery_id,
                                                   self.slug)

        GalleryExtractor.__init__(self, match, self.gallery_url)

    def items(self):
        (page, data) = self.parse_page(self.gallery_url)

        yield Message.Directory, data

        for url in self.images(page):
            data['filename'] = url.split(self.gallery_id + "/")[1].split('.')[0]
            data['extension'] = url.split('.')[-1].replace('/', '')
            url = "{}/{}".format(self.media_url_fmt, url)
            image_url = self.request(url, allow_redirects=False).headers[
                'location']
            yield Message.Url, image_url, data

    def images(self, page):
        return [
            url
            for url in
            text.extract_iter(page, 'href="https://kissjav.com/get_image/', '"')
        ]


class KissjavVideoExtrator(KissjavExtractor):
    subcategory = "video"
    pattern = BASE_PATTERN.format("video")
    example = "https://kissjav.com/video/198454/c1dcf01271f3a7b58559bc3cbf586626/"

    def __init__(self, match):
        KissjavExtractor.__init__(self, match)
        self.videos = self.config("videos", True)

    def items(self):
        if not self.videos:
            return

        (_, data) = self.parse_page(self.url)
        data['extension'] = 'mp4'
        yield Message.Directory, data
        yield Message.Url, "ytdl:" + self.url, data


