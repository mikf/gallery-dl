# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://desktopography.net"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?desktopography\.net"


class DesktopographyExtractor(Extractor):
    """Base class for desktopography extractors"""

    category = "desktopography"

    filename_fmt = "{filename}.{extension}"
    # filename_fmt = "{filename}_{filename}.{extension}"
    archive_fmt = "{filename}"
    root = "https://desktopography.net"
    test = (
        ("https://desktopography.net")
    )

    def __init__(self, match):
        Extractor.__init__(self, match)

    def items(self):
        url = self.root

        page = self.request(url).text
        last_pos = 0

        while True:
            exhibition_year, pos = text.extract(
                page,
                '<a href="https://desktopography.net/exhibition-',
                '/">',
                last_pos,
            )

            exhibition_url = self.root + "/exhibition-" + exhibition_year + "/"

            if exhibition_year is not None:
                data = {}
                # data = {"filename": last_pos, "extension": "jpg"}
                data["_extractor"] = DesktopographyExhibitionExtractor

                last_pos = pos
                # yield Message.Url, final_image_url, data
                yield Message.Queue, exhibition_url, data

            else:
                break


class DesktopographyExhibitionExtractor(DesktopographyExtractor):
    """Extractor for an yearly desktopography exhibition"""
    pattern = BASE_PATTERN + r"/exhibition-(.*)/"
    subcategory = "exhibition"
    test = (
        ("https://desktopography.net/exhibition-2020/")
    )

    def __init__(self, match):
        DesktopographyExtractor.__init__(self, match)
        self.year = match.group(1)

    def items(self):
        url = "{}/exhibition-{}/".format(self.root, self.year)
        base_entry_url = "https://desktopography.net/portfolios/"
        page = self.request(url).text
        last_pos = 0

        while True:
            entry_url, pos = text.extract(
                page,
                '<a class="overlay-background" href="' + base_entry_url,
                '">',
                last_pos,
            )

            if entry_url is not None:
                final_entry_url = base_entry_url + entry_url
                data = {}
                # data = {"filename": last_pos, "extension": "jpg"}
                data["_extractor"] = DesktopographyEntryExtractor
                data["exhibition_year"] = self.year

                last_pos = pos
                # yield Message.Url, final_image_url, data
                yield Message.Queue, final_entry_url, data

            else:
                break


class DesktopographyEntryExtractor(DesktopographyExtractor):
    """Extractor for all resolutions of a desktopography wallpaper"""

    pattern = BASE_PATTERN + r"/portfolios/([\w-]+)"
    subcategory = "entry"
    test = (
        ("https://desktopography.net/portfolios/new-era/")
    )

    def __init__(self, match):
        DesktopographyExtractor.__init__(self, match)
        self.entry = match.group(1)

    def items(self):
        url = "{}/portfolios/{}".format(self.root, self.entry)

        page = self.request(url).text
        last_pos = 0

        entry_data = {}

        yield Message.Version, 1
        yield Message.Directory, entry_data

        while True:
            image_data, pos = text.extract(
                page,
                '<a target="_blank" href="https://desktopography.net',
                '">',
                last_pos,
            )

            if image_data is not None:

                plit_string = '" class="wallpaper-button" download="'
                image_data = image_data.split(plit_string)

                final_image_url = self.root + image_data[0]

                image_data = image_data[1].split('.')

                entry_data["filename"] = image_data[0]
                entry_data["extension"] = image_data[1]

                image_data = image_data[0].split('_')
                entry_data["entry_tile"] = image_data[0]

                last_pos = pos
                yield Message.Url, final_image_url, entry_data

            else:
                break
