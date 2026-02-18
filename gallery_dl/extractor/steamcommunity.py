# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://steamcommunity.com"""

import re
from enum import Enum
from urllib.parse import urlparse

from .. import text
from .common import Extractor, Message


class SteamItemType(Enum):
    SCREENSHOT = 'Screenshot'
    ARTWORK = 'Artwork'


class SteamCommunitySharedfileExtractor(Extractor):
    """Extractor for steamcommunity shared files"""
    category = "SteamCommunity"

    directory_fmt = ("{category}", "{game}", "{content_type}")
    filename_fmt = "{filename}.{extension}"
    # archive_fmt = "{board}_{thread}_{tim}"

    pattern = r"(?:https?://)(?:www\.)?steamcommunity\.com/sharedfiles/filedetails/\?id=(\d+)$"
    example = "https://steamcommunity.com/sharedfiles/filedetails/?id=296316110"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.filedetails_id = match.group(1)

    @staticmethod
    def get_content_type(page_text) -> SteamItemType:

        tab = text.extr(
            page_text,
            'class="apphub_sectionTab active "><span>',
            '</span></a>'
        )

        if tab == 'Screenshots':
            return SteamItemType.SCREENSHOT
        if tab == 'Artwork':
            return SteamItemType.ARTWORK
        else:
            raise NotImplementedError("Could not parse content type", tab)

    def items(self):

        url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={self.filedetails_id}"

        page_text: str = self.request(url).text

        try:
            content_type = self.get_content_type(page_text)
        except ValueError as e:
            e2 = ValueError("Unknown content type for item", self.filedetails_id)
            raise e2 from e

        if content_type == SteamItemType.SCREENSHOT:
            yield from self.basic_image_items(page_text, content_type)
        elif content_type == SteamItemType.ARTWORK:
            yield from self.basic_image_items(page_text, content_type)
        else:
            raise NotImplementedError(content_type)

    def basic_image_items(self, page_text, content_type=None):

        app_name = text.extr(
            text.extr(page_text, '<div class="screenshotAppName">', '</div>'),
            '>', '<'
        )

        extr = text.extract_from(page_text)
        file_size = extr('<div class="detailsStatRight">', '</div>')
        date_posted = extr('<div class="detailsStatRight">', '</div>')
        dimensions = extr('<div class="detailsStatRight">', '</div>')
        creator = text.extr(
            page_text,
            '<div class="friendBlockContent">', '<br>'
        )
        title = text.extr(page_text, '<div class="workshopItemTitle">', '<br>')

        meta = {
            "game": app_name,
            "content_type": None,
            "creator": creator.strip(),
            "title": title.strip(),
            "filesize": text.parse_bytes(file_size.replace(' ', '')[:-1]),
            "dimensions": dimensions,
            "date": text.parse_datetime(date_posted, "%b %d, %Y @ %I:%M%p")
        }

        if content_type:
            meta['content_type'] = content_type.value

        yield Message.Directory, meta

        match = re.search(
            r'<img +id="ActualMedia" +class="(?:.+?)" +src="(.+?)"',
            page_text
        )

        img_src = match.group(1)
        url = urlparse(img_src)
        clean_url = url.scheme + '://' + url.netloc + url.path

        meta['filename'] = url.path.replace('/ugc/', '')[:-1]
        meta['extension'] = 'jpg'  # Rely on extension fixing

        yield Message.Url, clean_url, meta
