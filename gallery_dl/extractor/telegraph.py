# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractor for https://telegra.ph/"""

from .common import GalleryExtractor
from .. import text


class TelegraphGalleryExtractor(GalleryExtractor):
    """Extractor for articles from telegra.ph"""
    category = "telegraph"
    root = "https://telegra.ph"
    directory_fmt = ("{category}", "{slug}")
    filename_fmt = "{num_formatted}_{filename}.{extension}"
    archive_fmt = "{slug}_{num}"
    pattern = r"(?:https?://)(?:www\.)??telegra\.ph(/[^/?#]+)"
    example = "https://telegra.ph/TITLE"

    def metadata(self, page):
        extr = text.extract_from(page)
        data = {
            "title": text.unescape(extr(
                'property="og:title" content="', '"')),
            "description": text.unescape(extr(
                'property="og:description" content="', '"')),
            "date": text.parse_datetime(extr(
                'property="article:published_time" content="', '"'),
                "%Y-%m-%dT%H:%M:%S%z"),
            "author": text.unescape(extr(
                'property="article:author" content="', '"')),
            "post_url": text.unescape(extr(
                'rel="canonical" href="', '"')),
        }
        data["slug"] = data["post_url"][19:]
        return data

    def images(self, page):
        figures = (tuple(text.extract_iter(page, "<figure>", "</figure>")) or
                   tuple(text.extract_iter(page, "<img", ">")))
        num_zeroes = len(str(len(figures)))
        num = 0

        result = []
        for figure in figures:
            url, pos = text.extract(figure, 'src="', '"')
            if url.startswith("/embed/"):
                continue
            elif url[0] == "/":
                url = self.root + url
            caption, pos = text.extract(figure, "<figcaption>", "<", pos)
            num += 1

            result.append((url, {
                "url"          : url,
                "caption"      : text.unescape(caption) if caption else "",
                "num"          : num,
                "num_formatted": str(num).zfill(num_zeroes),
            }))
        return result
