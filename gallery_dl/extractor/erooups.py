# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for http://erooups.com/"""

from .common import Extractor, Message
from .. import text


class ErooupsGalleryExtractor(Extractor):
    category = 'erooups'
    directory_fmt = ('{category}', '{title}')
    filename_fmt = '{filename}.{extension}'
    archive_fmt = '{date}_{filename}'
    subcategory = 'gallery'
    pattern = r'(?:http?://)?(?:www\.)?erooups\.com'
    root = 'http://erooups.com'
    example = 'http://erooups.com/2023/10/25/page-title-11-pics.html'

    def items(self):
        page = self.request(
            text.ensure_http_scheme(self.url, scheme="http://")).text

        data = self.metadata(page)
        images = text.extract_iter(page, '</div><img src="', '?')

        yield Message.Directory, data
        for path in images:
            if 'erooups' not in path:
                path = self.root + path
            image = text.nameext_from_url(path, {
                'num': text.parse_int(path.split('_')[-1].split('.')[0]),
                'date': data['date']
            })
            yield Message.Url, path, image

    def metadata(self, page):
        data = {}
        data['pageurl'] = self.url
        data['date'] = '-'.join(self.url.split('/')[3:6])
        data['title'] = text.extr(
            page, '<h1 class="title">', '</h1>')
        data['tag'] = text.extr(
            page, '"><strong>', '</strong></a>')
        data['imagecount'] = text.extr(
            page, '<div class="pics">', '</div>')

        data = {k: text.unescape(data[k]) for k in data if data[k] != ""}

        return data
