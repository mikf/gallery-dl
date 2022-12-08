# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractor for https://fandom.com/"""

import re
from .common import GalleryExtractor
from .. import text


class FandomExtractor(GalleryExtractor):
    """Extractor for Fandom/Wikia media"""
    category = "fandom"
    directory_fmt = ("{category}", "{wiki}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{wiki}_{num}"
    pattern = (r"(?:https?://)?([\w-]+)\.(fandom|wikia)?\.com/?")
    test = (
        ("https://projectsekai.fandom.com"),
    )

    def __init__(self, match):
        self.wiki, self.category = match.groups()
        url = 'https://' + self.wiki + '.' + self.category + '.com'
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)
        return {
            "wiki": self.wiki,
            "title": text.unescape(
                extr('title>', '<').rpartition('|')[0].strip()),
        }

    def images(self, _):
        limit = 500
        base_url = self.gallery_url + '/wiki/Special:MIMESearch' + \
            '?limit=%d&mime=image%%2F*' % limit
        url = base_url
        offset = 0
        while True:
            html = self.request(url).text
            matches = re.findall(
                r'<a href="(https:[^"]+)" class="internal" title="([^"]+)"',
                html)
            for match in matches:
                href = text.unescape(match[0])
                name, _, ext = text.unescape(match[1]).rpartition(".")
                yield href, {
                    "filename": name,
                    "extension": ext.lower(),
                }
            if len(matches) < limit:
                return
            offset += limit
            url = base_url + "&offset=" + offset
