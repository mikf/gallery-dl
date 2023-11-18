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
    filename_fmt = '{title}_{filename}.{extension}'
    archive_fmt = '{id_string}_{filename}'
    pattern = BASE_PATTERN + r'/((contents)|(reader))/(\w+)'
    example = 'https://tmohentai.com/contents/12345a67b89c0'

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.contents = match.group(2)
        self.reader = match.group(3)
        self.id_string = match.group(4)

    def parse_location(self):
        if self.contents:
            url = '{}/reader/{}/paginated'.format(self.root, self.id_string)
        else:
            url_str = self.url.rpartition('/')
            if url_str[-1].isdigit():
                url = url_str[0]
            else:
                url = self.url
        return url

    @staticmethod
    def get_file_info(page_src):
        file = text.extr(page_src, 'data-original="', '"')
        file_loc, _, file_name = file.rpartition('/')
        start_num, ext = file_name.split('.')
        return file_loc, start_num, ext

    def items(self):
        url = self.parse_location()
        page_src = self.request(
            text.ensure_http_scheme(url)).text

        data = self.metadata()
        yield Message.Directory, data

        file_loc, start_num, ext = self.get_file_info(page_src)
        page_nums = text.extract_iter(
            page_src, 'option value="', '"')

        for num, page in enumerate(page_nums, start=int(start_num)):
            file = '{}/{:>03}.{}'.format(file_loc, num, ext)
            img = text.nameext_from_url(file, {
                'num'      : num,
                'title'    : data['title'],
                'id_string': self.id_string,
            })
            yield Message.Url, file, img

    def metadata(self):
        contents = '{}/contents/{}'.format(self.root, self.id_string)
        contents_src = self.request(text.ensure_http_scheme(contents)).text

        genders_src = text.extr(contents_src, 'Genders</label>', '</ul>')
        genders_list = text.extract_iter(genders_src, '">', '</a>')

        tags_src = text.extr(contents_src, 'Tags</label>', '</ul>')
        tags_list = text.extract_iter(tags_src, '">', '</a>')

        upload_src = text.extr(contents_src, 'Uploaded By</label>', '/a>')
        data = {
            'title'    : text.extr(contents_src, '<h3>', '</h3>').strip(),
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
