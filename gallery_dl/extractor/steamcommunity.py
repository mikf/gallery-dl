# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://steamcommunity.com"""

from enum import Enum
from .common import Extractor, Message
from .. import text

from urllib.parse import urlparse

import re


class SteamItemType(Enum):
    SCREENSHOT = 1
    ARTWORK = 2


class SteamCommunitySharedfileExtractor(Extractor):
    """Extractor for steamcommunity shared files"""
    category = "SteamCommunity"

    directory_fmt = ("{category}", "{game}")
    filename_fmt = "{filename}.{extension}"
    # archive_fmt = "{board}_{thread}_{tim}"

    pattern = r"(?:https?://)(?:www\.)?steamcommunity\.com/sharedfiles/filedetails/\?id=(\d+)$"
    example = "https://steamcommunity.com/sharedfiles/filedetails/?id=296316110"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.filedetails_id = match.group(1)

    @staticmethod
    def get_content_type(text) -> SteamItemType:
        match = re.search(r'<title>(.+?)<', text)
        if not match:
            raise ValueError("Could not extract item type from text")

        page_title = match.group(1)

        if page_title == 'Steam Community :: Screenshot':
            return SteamItemType.SCREENSHOT
        if page_title == 'Steam Community :: Artwork':
            return SteamItemType.ARTWORK
        else:
            raise NotImplementedError("Could not parse content type from title", page_title)

    def items(self):

        url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={self.filedetails_id}"

        page_text: str = self.request(url).text

        try:
            content_type = self.get_content_type(page_text)
        except ValueError as e:
            raise ValueError("Unknown content type for item", self.filedetails_id) from e

        if content_type == SteamItemType.SCREENSHOT:
            yield from self.screenshot_items(page_text)
        elif content_type == SteamItemType.ARTWORK:
            yield from self.screenshot_items(page_text)
        else:
            raise NotImplementedError(content_type)

    def screenshot_items(self, page_text):

        extr = text.extract_from(page_text)

        app_name = text.extr(text.extr(page_text, '<div class="screenshotAppName">', '</div>'), '>', '<')

        file_size = extr('<div class="detailsStatRight">', '</div>')
        date_posted = extr('<div class="detailsStatRight">', '</div>')
        dimensions = extr('<div class="detailsStatRight">', '</div>')

        meta = {
            "game": app_name,
            "creator": text.extr(page_text, '<div class="friendBlockContent">', '<br>').strip(),
            "filesize": text.parse_bytes(file_size.replace(' ', '')[:-1]),
            "dimensions": dimensions,
            "date": text.parse_datetime(date_posted, "%b %d, %Y @ %I:%M%p")
        }

        yield Message.Directory, meta

        match = re.search(r'<img +id="ActualMedia" +class="(?:.+?)" +src="(.+?)"', page_text)

        img_src = match.group(1)
        url = urlparse(img_src)
        clean_url = url.scheme + '://' + url.netloc + url.path

        meta['filename'] = url.path.replace('/ugc/', '')[:-1]
        meta['extension'] = 'jpg'  # Rely on extension fixing

        yield Message.Url, clean_url, meta
