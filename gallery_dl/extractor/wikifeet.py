# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.wikifeet.com/"""

from .common import GalleryExtractor
from .. import text
import json


class WikifeetGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from wikifeet.com"""
    category = "wikifeet"
    directory_fmt = ("{category}", "{celebrity}")
    filename_fmt = "{category}_{celeb}_{pid}.{extension}"
    archive_fmt = "{type}_{celeb}_{pid}"
    pattern = (r"(?:https?://)(?:(?:www\.)?wikifeetx?|"
               r"men\.wikifeet)\.com/([^/?#]+)")
    test = (
        ("https://www.wikifeet.com/Madison_Beer", {
            "pattern": (r"https://pics\.wikifeet\.com/Madison_Beer"
                        r"-Feet-\d+\.jpg"),
            "count"  : ">= 352",
            "keyword": {
                "celeb"     : "Madison_Beer",
                "celebrity" : "Madison Beer",
                "birthday"  : "dt:1999-03-05 00:00:00",
                "birthplace": "United States",
                "rating"    : float,
                "pid"       : int,
                "width"     : int,
                "height"    : int,
                "shoesize"  : "7.5 US",
                "type"      : "women",
                "tags"      : list,
            },
        }),
        ("https://www.wikifeetx.com/Tifa_Quinn", {
            "pattern": (r"https://pics\.wikifeet\.com/Tifa_Quinn"
                        r"-Feet-\d+\.jpg"),
            "count"  : ">= 9",
            "keyword": {
                "celeb"     : "Tifa_Quinn",
                "celebrity" : "Tifa Quinn",
                "birthday"  : "[NOT SET]",
                "birthplace": "United States",
                "rating"    : float,
                "pid"       : int,
                "width"     : int,
                "height"    : int,
                "shoesize"  : "[NOT SET]",
                "type"      : "women",
                "tags"      : list,
            },
        }),
        ("https://men.wikifeet.com/Chris_Hemsworth", {
            "pattern": (r"https://pics\.wikifeet\.com/Chris_Hemsworth"
                        r"-Feet-\d+\.jpg"),
            "count"  : ">= 860",
            "keyword": {
                "celeb"     : "Chris_Hemsworth",
                "celebrity" : "Chris Hemsworth",
                "birthday"  : "dt:1983-08-11 00:00:00",
                "birthplace": "Australia",
                "rating"    : float,
                "pid"       : int,
                "width"     : int,
                "height"    : int,
                "shoesize"  : "12.5 US",
                "type"      : "men",
                "tags"      : list,
            },
        }),
    )

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
                "tags"  : [tagmap[tag] for tag in data["tags"]],
            })
            for data in json.loads(text.extr(page, "['gdata'] = ", ";"))
        ]
