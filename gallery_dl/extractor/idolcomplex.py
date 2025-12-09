# -*- coding: utf-8 -*-

# Copyright 2018-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.idolcomplex.com/"""

from . import sankaku

BASE_PATTERN = (r"(?:https?://)?(?:www\.)?"
                r"idol(?:\.sankaku)?complex\.com"
                r"(?:/[a-z]{2}(?:[-_][A-Z]{2})?)?")


class IdolcomplexBase():
    """Base class for idolcomplex extractors"""
    category = "idolcomplex"
    root = "https://www.idolcomplex.com"
    cookies_domain = ".idolcomplex.com"

    def _init(self):
        self.api = sankaku.SankakuAPI(self)
        self.api.ROOT = "https://i.sankakuapi.com"
        self.api.headers["Origin"] = self.root


class IdolcomplexTagExtractor(IdolcomplexBase, sankaku.SankakuTagExtractor):
    """Extractor for idolcomplex tag searches"""
    pattern = rf"{BASE_PATTERN}(?:/posts)?/?\?([^#]*)"
    example = "https://www.idolcomplex.com/en/posts?tags=TAGS"


class IdolcomplexPoolExtractor(IdolcomplexBase, sankaku.SankakuPoolExtractor):
    """Extractor for idolcomplex pools"""
    pattern = rf"{BASE_PATTERN}/pools?/(?:show/)?(\w+)"
    example = "https://www.idolcomplex.com/en/pools/0123456789abcdef"


class IdolcomplexPostExtractor(IdolcomplexBase, sankaku.SankakuPostExtractor):
    """Extractor for individual idolcomplex posts"""
    pattern = rf"{BASE_PATTERN}/posts?(?:/show)?/(\w+)"
    example = "https://www.idolcomplex.com/en/posts/0123456789abcdef"
