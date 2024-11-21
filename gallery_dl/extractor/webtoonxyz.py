# -*- coding: utf-8 -*-

# Copyright 2022 Ion Chary

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.webtoon.xyz/"""

from .. import text, util
from .common import Extractor, GalleryExtractor, Message

BASE_PATTERN = r"(?:https?://)?(?:www\.)?webtoon\.xyz/read/([^/?#]+)"


class WebtoonxyzBase:
    category = "webtoonxyz"
    root = "https://www.webtoon.xyz"

    def setup_agegate_cookies(self):
        self._update_cookies(
            {
                "wpmanga-adault": "1",
            }
        )


class WebtoonxyzChapterExtractor(WebtoonxyzBase, GalleryExtractor):
    """Extractor for a chapter on webtoon.xyz"""

    subcategory = "chapter"
    directory_fmt = ("{category}", "{comic}")
    filename_fmt = "{chapter_no:>02}-{num:>02}.{extension}"
    archive_fmt = "{comic}_{chapter_no:>02}_{num}"
    pattern = BASE_PATTERN + r"/([^/?#]+)/?"
    test = (
        (
            "https://www.webtoon.xyz/read/learning-the-hard-way/chapter-1",
            {
                "url": "55bec5d7c42aba19e3d0d56db25fdf0b0b13be38",
                "content": (
                    "1748c7e82b6db910fa179f6dc7c4281b0f680fa7",
                    "42055e44659f6ffc410b3fb6557346dfbb993df3",
                    "49e1f2def04c6f7a6a3dacf245a1cd9abe77a6a9",
                ),
                "count": 5,
                "keyword": {
                    "comic": "learning-the-hard-way",
                    "description": r"re:^Bullied ruthlessly by girls .+",
                    "chapter_no": "1",
                    "title": "Learning The Hard Way",
                },
            },
        ),
    )

    def __init__(self, match):
        self.comic, self.chapter = match.groups()

        url = "{}/read/{}/{}/".format(self.root, self.comic, self.chapter)
        GalleryExtractor.__init__(self, match, url)
        self.session.headers["Referer"] = self.root + "/"
        self.setup_agegate_cookies()

    def metadata(self, page):
        locale, pos = text.extract(
            page, '<meta property="og:locale" content="', '"'
        )
        title, pos = text.extract(
            page, '<meta property="og:title" content="', '"', pos
        )
        descr, pos = text.extract(
            page, '<meta property="og:description" content="', '"', pos
        )

        return {
            "comic": self.comic,
            "chapter": self.chapter,
            "chapter_no": self.chapter.removeprefix("chapter-"),
            "title": text.unescape(title).removesuffix(
                " Manhwa : Read Manhwa Free at WEBTOON XYZ"
            ),
            "description": text.unescape(descr),
            "lang": locale[0:2],
            "language": util.code_to_language(locale[0:2]),
        }

    @staticmethod
    def images(page):
        images = [
            (url.strip(), None)
            for url in text.extract_iter(
                page,
                'data-src="',
                '" class="wp-manga-chapter-img',
            )
        ]
        return images[:-1]


class WebtoonxyzComicExtractor(WebtoonxyzBase, Extractor):
    """Extractor for an entire comic on webtoon.xyz"""

    subcategory = "comic"
    categorytransfer = True
    pattern = BASE_PATTERN + r"/?$"
    test = (
        (
            "https://www.webtoon.xyz/read/learning-the-hard-way/",
            {
                "url": "55bec5d7c42aba19e3d0d56db25fdf0b0b13be38",
                "content": (
                    "1748c7e82b6db910fa179f6dc7c4281b0f680fa7",
                    "42055e44659f6ffc410b3fb6557346dfbb993df3",
                    "49e1f2def04c6f7a6a3dacf245a1cd9abe77a6a9",
                ),
                "count": 5,
                "keyword": {
                    "comic": "learning-the-hard-way",
                    "description": r"re:^Bullied ruthlessly by girls .+",
                    "title": "Learning The Hard Way",
                },
            },
        ),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.session.headers["Referer"] = self.root + "/"
        self.setup_agegate_cookies()

        (self.comic,) = match.groups()

    def items(self):
        data = {"_extractor": WebtoonxyzChapterExtractor}
        url = "{}/read/{}/".format(self.root, self.comic)

        page = self.request(url).text
        page = text.extr(page, '<ul class="main version-chap', "</ul>")
        chapter_urls = [
            match.group(0)
            for match in WebtoonxyzChapterExtractor.pattern.finditer(page)
        ]

        for chapter_url in chapter_urls:
            yield Message.Queue, chapter_url, data
