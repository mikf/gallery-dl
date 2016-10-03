# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://pic-maniac.com/"""

from . import chronos

class PicmaniacImageExtractor(chronos.ChronosImageExtractor):
    """Extractor for single images from pic-maniac.com"""
    category = "picmaniac"
    pattern = [r"(?:https?://)?(?:www\.)?pic-maniac\.com/([a-z0-9]{12})"]
    url_base = "http://pic-maniac.com/"
    test = []
