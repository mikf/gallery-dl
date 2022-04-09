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
    test = (
        ("https://telegra.ph/Telegraph-Test-03-28", {
            "pattern": r"https://telegra\.ph/file/[0-9a-f]+\.png",
            "keyword": {
                "author": "mikf",
                "caption": r"re:test|",
                "count": 2,
                "date": "dt:2022-03-28 16:01:36",
                "description": "Just a test",
                "post_url": "https://telegra.ph/Telegraph-Test-03-28",
                "slug": "Telegraph-Test-03-28",
                "title": "Telegra.ph Test",
            },
        }),
        ("https://telegra.ph/森-03-28", {
            "pattern": "https://telegra.ph/file/3ea79d23b0dd0889f215a.jpg",
            "count": 1,
            "keyword": {
                "author": "&",
                "caption": "kokiri",
                "count": 1,
                "date": "dt:2022-03-28 16:31:26",
                "description": "コキリの森",
                "extension": "jpg",
                "filename": "3ea79d23b0dd0889f215a",
                "num": 1,
                "num_formatted": "1",
                "post_url": "https://telegra.ph/森-03-28",
                "slug": "森-03-28",
                "title": '"森"',
                "url": "https://telegra.ph/file/3ea79d23b0dd0889f215a.jpg",
            },
        }),
    )

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
        figures = tuple(text.extract_iter(page, "<figure>", "</figure>"))
        num_zeroes = len(str(len(figures)))
        num = 0

        result = []
        for figure in figures:
            src, pos = text.extract(figure, 'src="', '"')
            if src.startswith("/embed/"):
                continue
            caption, pos = text.extract(figure, "<figcaption>", "<", pos)
            url = self.root + src
            num += 1

            result.append((url, {
                "url"          : url,
                "caption"      : text.unescape(caption),
                "num"          : num,
                "num_formatted": str(num).zfill(num_zeroes),
            }))
        return result
