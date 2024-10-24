# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://lensdump.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?lensdump\.com"


class LensdumpBase():
    """Base class for lensdump extractors"""
    category = "lensdump"
    root = "https://lensdump.com"

    def _pagination(self, page, begin, end):
        while True:
            yield from text.extract_iter(page, begin, end)

            next = text.extr(page, ' data-pagination="next"', '>')
            if not next:
                return

            url = text.urljoin(self.root, text.extr(next, 'href="', '"'))
            page = self.request(url).text


class LensdumpAlbumExtractor(LensdumpBase, GalleryExtractor):
    subcategory = "album"
    pattern = BASE_PATTERN + r"/a/(\w+)(?:/?\?([^#]+))?"
    example = "https://lensdump.com/a/ID"

    def __init__(self, match):
        self.gallery_id, query = match.groups()
        if query:
            url = "{}/a/{}/?{}".format(self.root, self.gallery_id, query)
        else:
            url = "{}/a/{}".format(self.root, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        return {
            "gallery_id": self.gallery_id,
            "title": text.unescape(text.extr(
                page, 'property="og:title" content="', '"').strip())
        }

    def images(self, page):
        for image in self._pagination(page, ' class="list-item ', '>'):

            data = util.json_loads(text.unquote(
                text.extr(image, "data-object='", "'") or
                text.extr(image, 'data-object="', '"')))
            image_id = data.get("name")
            image_url = data.get("url")
            image_title = data.get("title")
            if image_title is not None:
                image_title = text.unescape(image_title)

            yield (image_url, {
                "id"       : image_id,
                "url"      : image_url,
                "title"    : image_title,
                "name"     : data.get("filename"),
                "filename" : image_id,
                "extension": data.get("extension"),
                "width"    : text.parse_int(data.get("width")),
                "height"   : text.parse_int(data.get("height")),
            })


class LensdumpAlbumsExtractor(LensdumpBase, Extractor):
    """Extractor for album list from lensdump.com"""
    subcategory = "albums"
    pattern = BASE_PATTERN + r"/(?![ai]/)([^/?#]+)(?:/?\?([^#]+))?"
    example = "https://lensdump.com/USER"

    def items(self):
        user, query = self.groups
        url = "{}/{}/".format(self.root, user)
        if query:
            params = text.parse_query(query)
        else:
            params = {"sort": "date_asc", "page": "1"}
        page = self.request(url, params=params).text

        data = {"_extractor": LensdumpAlbumExtractor}
        for album_path in self._pagination(page, 'data-url-short="', '"'):
            album_url = text.urljoin(self.root, album_path)
            yield Message.Queue, album_url, data


class LensdumpImageExtractor(LensdumpBase, Extractor):
    """Extractor for individual images on lensdump.com"""
    subcategory = "image"
    filename_fmt = "{category}_{id}{title:?_//}.{extension}"
    directory_fmt = ("{category}",)
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?(?:(?:i\d?\.)?lensdump\.com|\w\.l3n\.co)/i/(\w+)"
    example = "https://lensdump.com/i/ID"

    def items(self):
        key = self.groups[0]
        url = "{}/i/{}".format(self.root, key)
        extr = text.extract_from(self.request(url).text)

        data = {
            "id"    : key,
            "title" : text.unescape(extr(
                'property="og:title" content="', '"')),
            "url"   : extr(
                'property="og:image" content="', '"'),
            "width" : text.parse_int(extr(
                'property="image:width" content="', '"')),
            "height": text.parse_int(extr(
                'property="image:height" content="', '"')),
            "date"  : text.parse_datetime(extr(
                '<span title="', '"'), "%Y-%m-%d %H:%M:%S"),
        }

        text.nameext_from_url(data["url"], data)
        yield Message.Directory, data
        yield Message.Url, data["url"], data
