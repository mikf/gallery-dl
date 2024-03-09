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

    def nodes(self, page=None):
        if page is None:
            page = self.request(self.url).text

        # go through all pages starting from the oldest
        page_url = text.urljoin(self.root, text.extr(
            text.extr(page, ' id="list-most-oldest-link"', '>'),
            'href="', '"'))
        while page_url is not None:
            if page_url == self.url:
                current_page = page
            else:
                current_page = self.request(page_url).text

            for node in text.extract_iter(
                    current_page, ' class="list-item ', '>'):
                yield node

            # find url of next page
            page_url = text.extr(
                text.extr(current_page, ' data-pagination="next"', '>'),
                'href="', '"')
            if page_url is not None and len(page_url) > 0:
                page_url = text.urljoin(self.root, page_url)
            else:
                page_url = None


class LensdumpAlbumExtractor(LensdumpBase, GalleryExtractor):
    subcategory = "album"
    pattern = BASE_PATTERN + r"/(?:((?!\w+/albums|a/|i/)\w+)|a/(\w+))"
    example = "https://lensdump.com/a/ID"

    def __init__(self, match):
        GalleryExtractor.__init__(self, match, match.string)
        self.gallery_id = match.group(1) or match.group(2)

    def metadata(self, page):
        return {
            "gallery_id": self.gallery_id,
            "title": text.unescape(text.extr(
                page, 'property="og:title" content="', '"').strip())
        }

    def images(self, page):
        for node in self.nodes(page):
            # get urls and filenames of images in current page
            json_data = util.json_loads(text.unquote(
                text.extr(node, "data-object='", "'") or
                text.extr(node, 'data-object="', '"')))
            image_id = json_data.get('name')
            image_url = json_data.get('url')
            image_title = json_data.get('title')
            if image_title is not None:
                image_title = text.unescape(image_title)
            yield (image_url, {
                'id': image_id,
                'url': image_url,
                'title': image_title,
                'name': json_data.get('filename'),
                'filename': image_id,
                'extension': json_data.get('extension'),
                'height': text.parse_int(json_data.get('height')),
                'width': text.parse_int(json_data.get('width')),
            })


class LensdumpAlbumsExtractor(LensdumpBase, Extractor):
    """Extractor for album list from lensdump.com"""
    subcategory = "albums"
    pattern = BASE_PATTERN + r"/\w+/albums"
    example = "https://lensdump.com/USER/albums"

    def items(self):
        for node in self.nodes():
            album_url = text.urljoin(self.root, text.extr(
                node, 'data-url-short="', '"'))
            yield Message.Queue, album_url, {
                "_extractor": LensdumpAlbumExtractor}


class LensdumpImageExtractor(LensdumpBase, Extractor):
    """Extractor for individual images on lensdump.com"""
    subcategory = "image"
    filename_fmt = "{category}_{id}{title:?_//}.{extension}"
    directory_fmt = ("{category}",)
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?(?:(?:i\d?\.)?lensdump\.com|\w\.l3n\.co)/i/(\w+)"
    example = "https://lensdump.com/i/ID"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.key = match.group(1)

    def items(self):
        url = "{}/i/{}".format(self.root, self.key)
        extr = text.extract_from(self.request(url).text)

        data = {
            "id"    : self.key,
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
