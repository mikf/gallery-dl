# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.wikifeet.com/"""

from .common import GalleryExtractor
from .. import text, util


class WikifeetGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from wikifeet.com"""
    category = "wikifeet"
    directory_fmt = ("{category}", "{celebrity}")
    filename_fmt = "{category}_{celeb}_{pid}.{extension}"
    archive_fmt = "{type}_{celeb}_{pid}"
    pattern = (r"(?:https?://)(?:(?:www\.)?wikifeetx?|"
               r"men\.wikifeet)\.com/([^/?#]+)")
    example = "https://www.wikifeet.com/CELEB"

    def __init__(self, match):
        self.root = text.root_from_url(match.group(0))
        if "wikifeetx.com" in self.root:
            self.category = "wikifeetx"
        self.type = "men" if "://men." in self.root else "women"
        self.celeb = match.group(1)
        GalleryExtractor.__init__(self, match, self.root + "/" + self.celeb)

    def metadata(self, page):
        extr = text.extract_from(page)
        return {
            "celeb"     : self.celeb,
            "type"      : self.type,
            "rating"    : text.parse_float(extr('"ratingValue": "', '"')),
            "celebrity" : text.unescape(extr("times'>", "</h1>")),
            "shoesize"  : text.remove_html(extr("Shoe Size:", "edit")),
            "birthplace": text.remove_html(extr("Birthplace:", "edit")),
            "birthday"  : text.parse_datetime(text.remove_html(
                extr("Birth Date:", "edit")), "%Y-%m-%d"),
        }

    def images(self, page):
        tagmap = {
            "C": "Close-up",
            "T": "Toenails",
            "N": "Nylons",
            "A": "Arches",
            "S": "Soles",
            "B": "Barefoot",
        }
        ufmt = "https://pics.wikifeet.com/" + self.celeb + "-Feet-{}.jpg"
        return [
            (ufmt.format(data["pid"]), {
                "pid"   : data["pid"],
                "width" : data["pw"],
                "height": data["ph"],
                "tags"  : [
                    tagmap[tag]
                    for tag in data["tags"] if tag in tagmap
                ],
            })
            for data in util.json_loads(text.extr(page, "['gdata'] = ", ";"))
        ]
