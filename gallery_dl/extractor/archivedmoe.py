# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://archived.moe/"""

from . import chan


class ArchivedmoeThreadExtractor(chan.FoolfuukaThreadExtractor):
    """Extractor for images from threads on archived.moe"""
    category = "archivedmoe"
    root = "https://archived.moe"
    pattern = [r"(?:https?://)?archived\.moe/([^/]+)/thread/(\d+)"]
    test = [
        ("https://archived.moe/gd/thread/309639/", {
            "url": "fdd533840e2d535abd162c02d6dfadbc12e2dcd8",
            "content": "c27e2a7be3bc989b5dd859f7789cc854db3f5573",
        }),
        ("https://archived.moe/a/thread/159767162/", {
            "url": "ffec05a1a1b906b5ca85992513671c9155ee9e87",
        }),
    ]
