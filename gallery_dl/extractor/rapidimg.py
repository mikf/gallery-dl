# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://rapidimg.net/"""

from . import imgyt

class RapidimgImageExtractor(imgyt.ImgytImageExtractor):
    """Extractor for single images from rapidimg.net"""
    category = "rapidimg"
    pattern = [r"(?:https?://)?(?:www\.)?rapidimg\.net/img-([a-z0-9]+)\.html"]
    test = []
    url = "http://rapidimg.net"
    https = False
