# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mixdrop.ag/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?m[1i]xdrop\.(?:com|net|top|ag|bz)"


class MixdropFileExtractor(Extractor):
    """Extractor for mixdrop files"""
    category = "mixdrop"
    subcategory = "file"
    root = "https://mixdrop.ag"
    filename_fmt = "{title} ({id}).{extension}"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/[fe]/([^/?#]+)"
    example = "https://mixdrop.ag/f/0123456789abcdef"

    def items(self):
        fid = self.groups[0]
        page = self.request(f"{self.root}/e/{fid}").text
        string, pos = text.extract(page, "}}return p}('", "'")
        items = text.extract(page, ",'", "'.split(", pos)[0].split("|")
        txt = text.re(r"\b\w+\b").sub(lambda m: items[int(m.group(0))], string)

        data = text.nameext_from_name(text.extr(txt, '.vfile="', '"'), {
            "id": fid,
            "title": text.unescape(text.remove_html(text.extr(
                page, '<div class="title">', "</div>"))),
            "poster": text.ensure_http_scheme(text.extr(
                txt, '.poster="', '"')),
        })
        yield Message.Directory, "", data
        yield Message.Url, text.ensure_http_scheme(text.extr(
            txt, '.wurl="', '"')), data
