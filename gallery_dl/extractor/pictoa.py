# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://pictoa.com/"""

from .common import Extractor, Message
from .. import text
import re

BASE_PATTERN = r"(?:https?://)?(?:[\w]+\.)?pictoa\.com(?:\.de)?"

class PictoaExtractor(Extractor):
    """Base class for pictoa extractors"""
    category = "pictoa"
    root = "https://pictoa.com"

class PictoaImageExtractor(PictoaExtractor):
    """Extractor for single images from pictoa.com"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/albums/([^/\.?#]+)/([^/\.?#]+).html"
    filename_fmt = "{id}.{extension}"
    directory_fmt = ("{category}", "{album[id]}")
    archive_fmt = "{image_id}"
    example = "https://www.pictoa.com/albums/name-2693203/12345.html"

    def __init__(self, match):
        PictoaExtractor.__init__(self, match)
        self.album_id = match.group(1)
        self.image_id = match.group(2)

    def items(self):
        url = f"{self.root}/albums/{self.album_id}/{self.image_id}.html"
        page = self.request(url).text
        container = text.extract(page, '<div id="player"', "</div>")[0]
        album_title = text.extract(page, '<meta name="keywords" content="', '"')[0]
        image_url = text.extract(container, 'src="', '"')[0]
        data = {
            "album": {
                "id": self.album_id,
                "title": album_title,
            },
            "image_id": self.image_id,
            "id": self.image_id,
            "url": image_url,
        }
        text.nameext_from_url(image_url, data)
        yield Message.Directory, data
        yield Message.Url, image_url, data

class PictoaAlbumExtractor(PictoaExtractor):
    """Extractor for image albums from pictoa.com"""
    subcategory = "album"
    directory_fmt = ("{category}", "{album[id]} {album[title]}")
    archive_fmt = "{album[id]}_{id}"
    pattern = BASE_PATTERN + r"/albums/([^/\.?#]+).html"
    example = "https://www.pictoa.com/albums/name-2693203.html"

    def __init__(self, match):
        PictoaExtractor.__init__(self, match)
        self.album_id = match.group(1)

    def items(self):
        url = f"{self.root}/albums/{self.album_id}.html"
        page = self.request(url).text
        title = text.extract(page, '<h1>', '</h1>')[0]

        # grab the id out of the title (handiest place to get it)
        htmltitle = text.extract(page, '<title>', '</title>')[0]
        album_id = text.extract(htmltitle, '#', ' ')[0]

        # tags
        taghunk = text.extract(page, '<ol class="related-categories bt"', '</ol>')
        tags = re.compile(r"\s<li><a href=\".*\">([\d\w ]+)</a>").findall(taghunk[0])

        album_data = {
            "album": {
                "id": album_id,
                "title": title
            },
            "date": None,
            "title": title,
            "tags": tags,
        }
        yield Message.Directory, album_data

        # paginate through the pages
        pagination = text.extract(page, '<ul class="pagination"', '</ul>')[0]
        findall = re.compile(self.pattern).findall
        pages = findall(pagination)

        # run a quick dedupe
        page_set = {self.album_id: page}
        for i in pages:
            if i not in page_set:
                page_set[i] = self.request(f"{self.root}/albums/{i}.html").text

        for id, page in page_set.items():
            # we'll use the span#flag as the ending token for the
            # galleries portion of the page.
            image_container = text.extract(page, '<main>', '<span id="flag" >')[0]
            for url in text.extract_iter(image_container, '<a rel="nofollow" href="', '"'):
                data = {
                    "url": url,
                    "album_id": album_id,
                    "_extractor": PictoaImageExtractor
                }
                data.update(album_data)
                yield Message.Queue, url, data
