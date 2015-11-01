# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga pages from http://powermanga.org/"""

from .redhawkscans import RedHawkScansExtractor

info = {
    "category": "powermanga",
    "extractor": "PowerMangaExtractor",
    "directory": ["{category}", "{manga}", "c{chapter:>03}{chapter-minor} - {title}"],
    "filename": "{manga}_c{chapter:>03}{chapter-minor}_{page:>03}.{extension}",
    "pattern": [
        r"(?:https?://)?read(?:er)?\.powermanga\.org/read/(.+)(?:/page)?",
    ],
}

class PowerMangaExtractor(RedHawkScansExtractor):

    def __init__(self, match):
        RedHawkScansExtractor.__init__(self, match)
        extra = "er" if "://reader" in match.string else ""
        self.category = info["category"]
        self.url_base = "https://read" + extra + ".powermanga.org/read/"
