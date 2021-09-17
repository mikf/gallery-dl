# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://desktopography.net/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?desktopography\.net"


class DesktopographyExtractor(Extractor):
    """Base class for desktopography extractors"""
    category = "desktopography"
    archive_fmt = "{filename}"
    root = "https://desktopography.net"


class DesktopographySiteExtractor(DesktopographyExtractor):
    """Extractor for all desktopography exhibitions """
    subcategory = "site"
    pattern = BASE_PATTERN + r"/$"
    test = ("https://desktopography.net/",)

    def items(self):
        page = self.request(self.root).text
        data = {"_extractor": DesktopographyExhibitionExtractor}

        for exhibition_year in text.extract_iter(
                page,
                '<a href="https://desktopography.net/exhibition-',
                '/">'):

            url = self.root + "/exhibition-" + exhibition_year + "/"
            yield Message.Queue, url, data


class DesktopographyExhibitionExtractor(DesktopographyExtractor):
    """Extractor for a yearly desktopography exhibition"""
    subcategory = "exhibition"
    pattern = BASE_PATTERN + r"/exhibition-([^/?#]+)/"
    test = ("https://desktopography.net/exhibition-2020/",)

    def __init__(self, match):
        DesktopographyExtractor.__init__(self, match)
        self.year = match.group(1)

    def items(self):
        url = "{}/exhibition-{}/".format(self.root, self.year)
        base_entry_url = "https://desktopography.net/portfolios/"
        page = self.request(url).text

        data = {
            "_extractor": DesktopographyEntryExtractor,
            "year": self.year,
        }

        for entry_url in text.extract_iter(
                page,
                '<a class="overlay-background" href="' + base_entry_url,
                '">'):

            url = base_entry_url + entry_url
            yield Message.Queue, url, data


class DesktopographyEntryExtractor(DesktopographyExtractor):
    """Extractor for all resolutions of a desktopography wallpaper"""
    subcategory = "entry"
    pattern = BASE_PATTERN + r"/portfolios/([\w-]+)"
    test = ("https://desktopography.net/portfolios/new-era/",)

    def __init__(self, match):
        DesktopographyExtractor.__init__(self, match)
        self.entry = match.group(1)

    def items(self):
        url = "{}/portfolios/{}".format(self.root, self.entry)
        page = self.request(url).text

        entry_data = {"entry": self.entry}
        yield Message.Directory, entry_data

        for image_data in text.extract_iter(
                page,
                '<a target="_blank" href="https://desktopography.net',
                '">'):

            path, _, filename = image_data.partition(
                '" class="wallpaper-button" download="')
            text.nameext_from_url(filename, entry_data)
            yield Message.Url, self.root + path, entry_data
