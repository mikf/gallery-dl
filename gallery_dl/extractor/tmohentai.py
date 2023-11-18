# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://tmohentai.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r'(?:https?://)?tmohentai\.com'


class TmohentaiExtractor(Extractor):
    category = 'tmohentai'
    root = 'http://tmohentai.com'
    directory_fmt = ('{category}', '{title}')
    filename_fmt = '{filename}.{extension}'
    archive_fmt = '{title}_{filename}'
    pattern = BASE_PATTERN + r'/((contents)|(reader))/(\w+)'
    example = 'https://tmohentai.com/contents/12345a67b89c0'

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.contents = match.group(2)
        self.reader = match.group(3)
        self.id_string = match.group(4)

    def parse_location(self):
        if self.contents:
            url = f'{self.root}/reader/{self.id_string}/paginated'
        else:
            url = self.url
        return url

    def items(self):
        url = self.parse_location()
        page_src = self.request(
            text.ensure_http_scheme(url)).text

        data = self.metadata()
        yield Message.Directory, data

        page_nums = text.extract_iter(page_src, 'option value="', '"')
        pages = [text.extr(page_src, 'data-original="', '"')]
        base_page = pages[0].rpartition('/')[0]
        for num, page in enumerate(page_nums, start=1):
            file = f'{base_page}/{num:>03}.webp'
            img = text.nameext_from_url(file, {
                'num': num,
            })
            yield Message.Url, file, img

    def metadata(self):
        contents = f'{self.root}/contents/{self.id_string}'
        contents_src = self.request(text.ensure_http_scheme(contents)).text

        genders_src = text.extr(contents_src, 'Genders</label>', '</ul>')
        genders_list = text.extract_iter(genders_src, '">', '</a>')

        tags_src = text.extr(contents_src, 'Tags</label>', '</ul>')
        tags_list = text.extract_iter(tags_src, '">', '</a>')

        upload_src = text.extr(contents_src, 'Uploaded By</label>', '/a>')
        data = {
            'title'    : text.extr(contents_src, '<h3>', '</h3>'),
            'id_string': self.id_string,
            'artists'  : text.remove_html(
                text.extr(contents_src, 'tag tag-accepted">', '</a>')),
            'genders'  : list(genders_list),
            'tags'     : list(tags_list),
            'uploader' : text.extr(upload_src, '">', '<'),
            'language' : text.extr(
                contents_src, '<a><span class="flag-icon'
                              ' flag-icon-es"></span>&nbsp;', '</a>'),
        }
        return data
