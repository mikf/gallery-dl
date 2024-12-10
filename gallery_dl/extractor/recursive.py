# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Recursive extractor"""

from .common import Extractor, Message
from .. import text
import re


class RecursiveExtractor(Extractor):
    """Extractor that fetches URLs from a remote or local source"""
    category = "recursive"
    pattern = r"r(?:ecursive)?:"
    example = "recursive:https://pastebin.com/raw/FLwrCYsT"

    def items(self):
        url = self.url.partition(":")[2]

        if url.startswith("file://"):
            with open(url[7:]) as fp:
                page = fp.read()
        else:
            page = self.request(text.ensure_http_scheme(url)).text

        for match in re.finditer(r"https?://[^\s\"']+", page):
            yield Message.Queue, match.group(0), {}
