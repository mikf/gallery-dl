#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl.extractor import wpmadara  # noqa E402
from gallery_dl.extractor.common import Message  # noqa E402


class DummyMangaExtractor():
    pass


class DummyHomeExtractor(wpmadara.WPMadaraHomeExtractor):
    category = "dummy-wpmadara"
    root = "https://example.org"
    mangaextractor = DummyMangaExtractor
    pattern = r"(?:https?://)?example\.org(?:/page/(\d+))?/?$"
    example = "https://example.org/"


class DummyChapterExtractor(wpmadara.WPMadaraChapterExtractor):
    category = "dummy-wpmadara"
    root = "https://example.org"
    pattern = r"(?:https?://)?example\.org(/series/[^/?#]+/[^/?#]+)"
    example = "https://example.org/series/manga/chapter-1/"


def toonily_listing():
    return """\
<div class="page-item-detail manga">
<div class="item-thumb c-image-hover">
<a href="https://toonily.com/serie/living-in-america-6639a974/"
title="Living in America"><img src="cover.jpg"></a>
</div>
<div class="item-summary">
<h3><a href="https://toonily.com/serie/living-in-america-6639a974/">
Living in America</a></h3>
<div class="list-chapter">
<a href="https://toonily.com/serie/living-in-america-6639a974/chapter-20/"
class="btn-link">Chapter 20</a>
</div>
</div>
</div>
<div class="page-item-detail manga">
<div class="item-thumb c-image-hover">
<a href="https://toonily.com/serie/rooftop-sex-king-e0ec66e5/"
title="Rooftop Sex King"><img src="cover.jpg"></a>
</div>
</div>
"""


def webtoonxyz_listing():
    return """\
<div class="page-item-detail manga  ">
<div class="item-thumb c-image-hover">
<a href="https://www.webtoon.xyz/read/jungle-juice/" title="Jungle Juice">
<img src="cover.jpg"></a>
</div>
<div class="item-summary">
<h3><a href="https://www.webtoon.xyz/read/jungle-juice/">Jungle Juice</a></h3>
<div class="list-chapter">
<a href="https://www.webtoon.xyz/read/jungle-juice/chapter-195/"
class="btn-link">Chapter 195</a>
</div>
</div>
</div>
<div class="page-item-detail manga  ">
<div class="item-thumb c-image-hover">
<a href="https://www.webtoon.xyz/read/reality-quest/"
title="Reality Quest"><img src="cover.jpg"></a>
</div>
</div>
"""


class TestWPMadaraHomeExtractor(unittest.TestCase):

    def test_mangas_toonily_listing(self):
        extr = DummyHomeExtractor.from_url("https://example.org/")

        self.assertEqual(extr.basecategory, "wpmadara")

        self.assertEqual(list(extr.mangas(toonily_listing())), [
            "https://toonily.com/serie/living-in-america-6639a974/",
            "https://toonily.com/serie/rooftop-sex-king-e0ec66e5/",
        ])

    def test_mangas_webtoonxyz_listing(self):
        extr = DummyHomeExtractor.from_url("https://example.org/")

        self.assertEqual(list(extr.mangas(webtoonxyz_listing())), [
            "https://www.webtoon.xyz/read/jungle-juice/",
            "https://www.webtoon.xyz/read/reality-quest/",
        ])

    def test_items_paginate(self):
        pages = {
            "https://example.org/page/2/":
                toonily_listing() +
                '<a class="nextpostslink" rel="next" href="/page/4/">'
                '»</a>',
            "https://example.org/page/4/": webtoonxyz_listing(),
        }
        extr = DummyHomeExtractor.from_url("https://example.org/page/2/")
        extr.request = lambda url: type("Response", (), {"text": pages[url]})()

        items = list(extr.items())

        self.assertEqual([item[1] for item in items], [
            "https://toonily.com/serie/living-in-america-6639a974/",
            "https://toonily.com/serie/rooftop-sex-king-e0ec66e5/",
            "https://www.webtoon.xyz/read/jungle-juice/",
            "https://www.webtoon.xyz/read/reality-quest/",
        ])
        self.assertTrue(all(item[0] is Message.Queue for item in items))
        self.assertTrue(all(
            item[2]["_extractor"] is DummyMangaExtractor
            for item in items
        ))


class TestWPMadaraBase(unittest.TestCase):

    def test_manga_data_accepts_alternative_label(self):
        extr = DummyHomeExtractor.from_url("https://example.org/")
        data = extr.manga_data("series/manga", page="""\
<h1>Example Manga</h1>
<div class="post-content_item">
<div class="summary-heading"><h5>Alternative</h5></div>
<div class="summary-content">Alt Title</div>
</div>
<div class="post-content_item">
<div class="summary-heading"><h5>Author(s)</h5></div>
<div class="summary-content"><div class="author-content">
<a rel="tag">Author</a></div></div>
</div>
<div class="post-content_item">
<div class="summary-heading"><h5>Artist(s)</h5></div>
<div class="summary-content"><div class="artist-content">
<a rel="tag">Artist</a></div></div>
</div>
<div class="post-content_item">
<div class="summary-heading"><h5>Genre(s)</h5></div>
<div class="summary-content"><div class="genres-content">
<a rel="tag">Drama</a></div></div>
</div>
<div class="post-content_item">
<div class="summary-heading"><h5>Type</h5></div>
<div class="summary-content">Manhwa</div>
</div>
<div class="post-content_item">
<div class="summary-heading"><h5>Release</h5></div>
<div class="summary-content">2025</div>
</div>
<div class="post-content_item">
<div class="summary-heading"><h5>Status</h5></div>
<div class="summary-content">OnGoing</div>
</div>
<div class="summary__content"><p>Description</p></div>
<span class="score font-meta total_votes">4.3</span>
""")

        self.assertEqual(data["manga_alt"], ["Alt Title"])
        self.assertEqual(data["author"], ["Author"])
        self.assertEqual(data["artist"], ["Artist"])
        self.assertEqual(data["genres"], ["Drama"])
        self.assertEqual(data["type"], "Manhwa")
        self.assertEqual(data["release"], 2025)
        self.assertEqual(data["status"], "OnGoing")
        self.assertEqual(data["rating"], 4.3)


class TestWPMadaraChapterExtractor(unittest.TestCase):

    def test_images_prefer_data_src(self):
        extr = DummyChapterExtractor.from_url(
            "https://example.org/series/manga/chapter-1/",
        )
        images = extr.images("""\
<div class="reading-content">
<div class="page-break no-gaps">
<img data-src="https://example.org/data.jpg"
src="https://example.org/lazy.jpg">
</div>
<div class="page-break no-gaps">
<img src="https://example.org/plain.jpg">
</div>
</div>
<div class="entry-header footer"></div>
""")

        self.assertEqual(images, [
            ("https://example.org/data.jpg", None),
            ("https://example.org/plain.jpg", None),
        ])


if __name__ == "__main__":
    unittest.main()
