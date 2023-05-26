# -*- coding: utf-8 -*-

"""Extractors for https://lensdump.com/"""

import json

from .common import GalleryExtractor, Extractor, Message
from .. import text


class LensdumpExtractor(GalleryExtractor):
    """Extractor for lensdump.com"""
    category = "lensdump"
    root = "https://lensdump.com"

    def get_meta_prop(self, page, name):
        return text.extr(page, f'property="{name}" content="', '"')

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


class LensdumpAlbumExtractor(LensdumpExtractor):
    subcategory = "album"
    pattern = (r"(?:https?://)?lensdump\.com/"
               r"(?:((?!\w+/albums|a/|i/)\w+)|a/(\w+))")
    test = (
        ("https://lensdump.com/a/1IhJr", {
            "url": "7428cc906e7b291c778d446a11c602b81ba72840",
            "keyword": {
                "extension": "png",
                "name": str,
                "num": int,
                "title": str,
                "url": str,
                "width": int,
            },
        }),
    )

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
            json_data = json.loads(text.unquote(
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


class LensdumpAlbumsExtractor(LensdumpExtractor):
    """Extractor for album list from lensdump.com"""
    pattern = r"(?:https?://)?lensdump\.com/\w+/albums"

    def __init__(self, match):
        Extractor.__init__(self, match)

    def items(self):
        for node in self.nodes():
            album_url = text.urljoin(self.root, text.extr(
                node, 'data-url-short="', '"'))
            yield Message.Queue, album_url, {
                "_extractor": LensdumpAlbumExtractor}


class LensdumpImageExtractor(LensdumpExtractor):
    """Extractor for individual images on lensdump.com"""
    subcategory = "image"
    filename_fmt = "{category}_{id}{title:?_//}.{extension}"
    directory_fmt = ("{category}",)
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?lensdump\.com/i/(\w+)"
    test = (
        ("https://lensdump.com/i/tyoAyM", {
            "url": "ae9933f5f3bd9497bfc34e3e70a0fbef6c562d38",
            "content": "1aa749ed2c0cf679ec8e1df60068edaf3875de46",
            "keyword": {
                "extension": "webp",
                "filename": "tyoAyM",
                "height": "400",
                "id": "tyoAyM",
                "title": "MYOBI clovis bookcaseset",
                "url": "https://i2.lensdump.com/i/tyoAyM.webp",
                "width": "620",
            },
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.key = match.group(1)

    def items(self):
        page = self.request(self.url).text
        image_url = text.extr(page, 'property="og:image" content="', '"')
        data = text.nameext_from_url(image_url)
        data.update({
            'id': self.key,
            'url': image_url,
            'title': self.get_meta_prop(page, "og:title"),
            'height': self.get_meta_prop(page, "image:height"),
            'width': self.get_meta_prop(page, "image:width"),
        })
        yield Message.Directory, data
        yield Message.Url, image_url, data
