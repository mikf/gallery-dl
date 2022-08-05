# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractor for https://catbox.moe/"""

import unicodedata
import re
from .common import Extractor, Message
from .. import text


def slugify(value):
    """
    Modified from https://github.com/django/django/blob/master/django/utils/text.py
    Convert spaces, repeated dashes abd repeated underscores to single underscore.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Also strip leading and trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    value = unicodedata.normalize('NFKC', value)
    value = re.sub(r'[^\w\s-]', '', value)
    return re.sub(r'[-\s]+', '_', value).strip('-_')


class CatboxCollectionExtractor(Extractor):
    """extractor for Catbox Collections"""
    category = "catbox"
    subcategory = "collection"
    directory_fmt = ("{category}","{title}{id}",)
    pattern = (
        r"(?:https?:\/\/)?(?:www\.)?catbox\.moe\/c\/[\w-]+#?"
    )
    test = (
        ("https://www.catbox.moe/c/cd90s1"),
        ("https://catbox.moe/c/w7tm47#"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.name = match.group(0).split("/")[-1]
        self.name = self.name.replace("#", "")
        self.url = text.ensure_http_scheme(self.url.rstrip("#"))

    def items(self):
        webpage = self.request(self.url).text
        title = re.search(r'<h1>(.*?)<\/h1>', webpage)
        if title is not None:
            title = title.group(1)
            title = slugify(title) + "_"
        else:
            title = ""
        links = re.findall(
            r">https?:\/\/files\.catbox\.moe\/[0-9a-z.]+<", webpage)
        if len(links) != 0:
            yield Message.Directory, {"id": self.name, "title": title}
            links = [l.strip("<>") for l in set(links)]
            for link in links:
                yield Message.Url, link, text.nameext_from_url(link)
