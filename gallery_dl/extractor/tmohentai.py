# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://tmohentai.com/"""

from .common import GalleryExtractor, Message
from .. import text

BASE_PATTERN = r'(?:https?://)?tmohentai\.com'


class TmohentaiGalleryExtractor(GalleryExtractor):
    category = 'tmohentai'
    subcategory = 'gallery'
    root = 'http://tmohentai.com'
    directory_fmt = ('{category}', '{title}')
    filename_fmt = '{title}_{filename}.{extension}'
    archive_fmt = '{id_string}_{filename}'
    pattern = BASE_PATTERN + r'/(contents)|(reader)/(\w+)'
    example = 'https://tmohentai.com/contents/12345a67b89c0'

    def __init__(self, match):
        self.id_string = match.group(2)
        url = '{}/contents/{}'.format(self.root, self.id_string)
        GalleryExtractor.__init__(self, match, url)

    def items(self):
        page = self.request(
            text.ensure_http_scheme(self.url)).text
        data = self.metadata(page)

        yield Message.Directory, data
        imgs = self.images(page)

        cdn = 'https://imgrojo.tmohentai.com/contents'
        for num, _ in enumerate(imgs, start=0):
            url = ('{}/{}/{:>03}.webp'.format(cdn, self.id_string, num))
            img = text.nameext_from_url(url, {
                'num'      : num + 1,
                'title'    : data['title'],
                'id_string': self.id_string,
            })
            yield Message.Url, url, img

    def images(self, page):
        pages = text.extract_iter(
            page, 'class="lanzador', '>')
        return pages

    def metadata(self, page):
        extr = text.extract_from(page, page.index('tag tag-accepted">'))

        return {
            'title'    : text.extr(page, '<h3>', '</h3>').strip(),
            'id_string': self.id_string,
            'artists'  : text.remove_html(extr('">', '</a>')),
            'genders'  : text.split_html(extr('Genders</label>', '<div')),
            'tags'     : text.split_html(extr('Tags</label>', '</ul>')),
            'uploader' : text.remove_html(extr('Uploaded By</label>', '</a>')),
            'language' : extr('&nbsp;', '\n</a>'),
        }
