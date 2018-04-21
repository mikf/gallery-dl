# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://hitomi.la/"""

from .common import ChapterExtractor
from .. import text, util
import string


class HitomiGalleryExtractor(ChapterExtractor):
    """Extractor for image galleries from hitomi.la"""
    category = "hitomi"
    subcategory = "gallery"
    directory_fmt = ["{category}", "{gallery_id} {title}"]
    filename_fmt = "{category}_{gallery_id}_{page:>03}_{name}.{extension}"
    archive_fmt = "{gallery_id}_{page}"
    pattern = [r"(?:https?://)?hitomi\.la/(?:galleries|reader)/(\d+)"]
    test = [
        ("https://hitomi.la/galleries/867789.html", {
            "url": "cb759868d090fe0e2655c3e29ebf146054322b6d",
            "keyword": "85e453d01ee7f137669e75a764ccdc65ca092ad2",
        }),
        ("https://hitomi.la/reader/867789.html", None),
    ]

    def __init__(self, match):
        self.gid = text.parse_int(match.group(1))
        url = "https://hitomi.la/galleries/{}.html".format(self.gid)
        ChapterExtractor.__init__(self, url)

    def get_metadata(self, page, extr=text.extract):
        pos = page.index('<h1><a href="/reader/')
        title , pos = extr(page, '.html">', '<', pos)
        artist, pos = extr(page, '<h2>', '</h2>', pos)
        group , pos = extr(page, '<td>Group</td><td>', '</td>', pos)
        gtype , pos = extr(page, '<td>Type</td><td>', '</td>', pos)
        lang  , pos = extr(page, '<td>Language</td><td>', '</td>', pos)
        series, pos = extr(page, '<td>Series</td><td>', '</td>', pos)
        chars , pos = extr(page, '<td>Characters</td><td>', '</td>', pos)
        tags  , pos = extr(page, '<td>Tags</td><td>', '</td>', pos)
        date  , pos = extr(page, '<span class="date">', '</span>', pos)
        lang = None if lang == "N/A" else text.remove_html(lang)

        return {
            "gallery_id": self.gid,
            "title": text.unescape(" ".join(title.split())),
            "artist": self._prepare(artist),
            "group": self._prepare(group),
            "type": text.remove_html(gtype).capitalize(),
            "lang": util.language_to_code(lang),
            "language": lang,
            "date": date,
            "series": self._prepare(series),
            "characters": self._prepare(chars),
            "tags": self._prepare(tags),
        }

    def get_images(self, page):
        subdomain = chr(97 + self.gid % 2) + "a"
        base = "https://" + subdomain + ".hitomi.la/galleries/"
        return [
            (base + urlpart, None)
            for urlpart in text.extract_iter(
                page, "'//tn.hitomi.la/smalltn/", ".jpg',"
            )
        ]

    @staticmethod
    def _prepare(value):
        if not value or "<ul " not in value:
            return ""
        value = ", ".join(text.extract_iter(
            value, '.html">', '<'))
        return string.capwords(
            text.unescape(value)
        )
