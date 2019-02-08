# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://idol.sankakucomplex.com/"""

from . import sankaku


class IdolcomplexExtractor(sankaku.SankakuExtractor):
    """Base class for idolcomplex extractors"""
    category = "idolcomplex"
    cookiedomain = "idol.sankakucomplex.com"
    subdomain = "idol"


class IdolcomplexTagExtractor(IdolcomplexExtractor,
                              sankaku.SankakuTagExtractor):
    """Extractor for images from idol.sankakucomplex.com by search-tags"""
    pattern = r"(?:https?://)?idol\.sankakucomplex\.com/\?([^#]*)"
    test = (
        ("https://idol.sankakucomplex.com/?tags=lyumos+wreath", {
            "count": ">= 6",
            "pattern": r"https://is\.sankakucomplex\.com/data/[^/]{2}/[^/]{2}"
                       r"/[^/]{32}\.\w+\?e=\d+&m=[^&#]+",
        }),
        ("https://idol.sankakucomplex.com"
         "/?tags=lyumos+wreath&page=3&next=694215"),
    )


class IdolcomplexPoolExtractor(IdolcomplexExtractor,
                               sankaku.SankakuPoolExtractor):
    """Extractor for image-pools from idol.sankakucomplex.com"""
    pattern = r"(?:https?://)?idol\.sankakucomplex\.com/pool/show/(\d+)"
    test = ("https://idol.sankakucomplex.com/pool/show/145", {
        "count": 3,
    })


class IdolcomplexPostExtractor(IdolcomplexExtractor,
                               sankaku.SankakuPostExtractor):
    """Extractor for single images from idol.sankakucomplex.com"""
    pattern = r"(?:https?://)?idol\.sankakucomplex\.com/post/show/(\d+)"
    test = ("https://idol.sankakucomplex.com/post/show/694215", {
        "content": "694ec2491240787d75bf5d0c75d0082b53a85afd",
        "options": (("tags", True),),
        "keyword": {
            "tags_character": "shani_(the_witcher)",
            "tags_copyright": "the_witcher",
            "tags_idol": str,
            "tags_medium": str,
            "tags_general": str,
        },
    })
