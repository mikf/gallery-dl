# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.comedywildlifephoto.com/"""

from .common import GalleryExtractor
from .. import text


class ComedywildlifephotoGalleryExtractor(GalleryExtractor):
    """Extractor for comedywildlifephoto galleries"""
    category = "comedywildlifephoto"
    root = "https://www.comedywildlifephoto.com"
    directory_fmt = ("{category}", "{section}", "{title}")
    filename_fmt = "{num:>03} {filename}.{extension}"
    archive_fmt = "{section}/{title}/{num}"
    pattern = (r"(?:https?://)?(?:www\.)?comedywildlifephoto\.com"
               r"(/gallery/[^/?#]+/[^/?#]+\.php)")
    example = "https://www.comedywildlifephoto.com/gallery/SECTION/TITLE.php"

    def metadata(self, page):
        extr = text.extract_from(page)

        return {
            "section": extr("<h1>", "<").strip(),
            "title"  : extr(">", "<"),
            "description": text.unescape(extr(
                'class="c1 np">', "<div")),
        }

    def images(self, page):
        results = []

        for fig in text.extract_iter(page, "<figure", "</figure>"):
            width, _, height = text.extr(
                fig, 'data-size="', '"').partition("x")
            results.append((
                self.root + text.extr(fig, 'href="', '"'), {
                    "width"  : text.parse_int(width),
                    "height" : text.parse_int(height),
                    "caption": text.unescape(text.extr(
                        fig, "<figcaption>", "<")),
                }
            ))

        return results
