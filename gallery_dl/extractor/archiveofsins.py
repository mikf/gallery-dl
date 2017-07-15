# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://archiveofsins.com/"""

from . import chan


class ArchiveofsinsThreadExtractor(chan.FoolfuukaThreadExtractor):
    """Extractor for images from threads on archiveofsins.com"""
    category = "archiveofsins"
    root = "https://archiveofsins.com"
    pattern = [r"(?:https?://)?(?:www\.)?archiveofsins\.com"
               r"/([^/]+)/thread/(\d+)"]
    test = [("https://www.archiveofsins.com/h/thread/4668813/", {
        "url": "f612d287087e10a228ef69517cf811539db9a102",
        "content": "0dd92d0d8a7bf6e2f7d1f5ac8954c1bcf18c22a4",
    })]
