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
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import config  # noqa E402
from gallery_dl.extractor import webtoonxyz  # noqa E402
from gallery_dl.extractor.common import Message  # noqa E402


MANGA_URL = (
    "https://www.webtoon.xyz/read/i-became-an-apartment-security-manager/"
)
CHAPTER_URL = MANGA_URL + "chapter-1/"
MINOR_CHAPTER_URL = (
    "https://www.webtoon.xyz/read/the-monster-in-my-room/chapter-42-01/"
)
HOME_URL = "https://www.webtoon.xyz/page/2/"
IMAGE_BASE = (
    "https://cdn8.webtoon.xyz/manga_68989afff3159/"
    "bba27c1e700f002c9476a982e8883101/"
)


def chapter_html():
    return """\
<h1 id="chapter-heading">
I Became an Apartment Security Manager - Chapter 1
</h1>
<div class="reading-content">
<div class="page-break no-gaps">
<img id="image-0" data-src="{base}01.jpg"
src="https://www.webtoon.xyz/wp-content/themes/madara/images/dflazy.jpg">
</div>
<div class="page-break no-gaps">
<img id="image-1" data-src="{base}02.jpg"
src="https://www.webtoon.xyz/wp-content/themes/madara/images/dflazy.jpg">
</div>
<div class="page-break no-gaps">
<img id="image-2" data-src="{base}03.jpg"
src="https://www.webtoon.xyz/wp-content/themes/madara/images/dflazy.jpg">
</div>
<div class="page-break no-gaps">
<img id="image-3" data-src="{base}04.jpg"
src="https://www.webtoon.xyz/wp-content/themes/madara/images/dflazy.jpg">
</div>
<div class="page-break no-gaps">
<img id="image-4" data-src="{base}05.jpg"
src="https://www.webtoon.xyz/wp-content/themes/madara/images/dflazy.jpg">
</div>
<div class="page-break no-gaps">
<img id="image-5" data-src="{base}06.jpg"
src="https://www.webtoon.xyz/wp-content/themes/madara/images/dflazy.jpg">
</div>
<div class="page-break no-gaps">
<img id="image-6" data-src="{base}07.jpg"
src="https://www.webtoon.xyz/wp-content/themes/madara/images/dflazy.jpg">
</div>
<div class="page-break no-gaps">
<img id="image-7" data-src="{base}08.jpg"
src="https://www.webtoon.xyz/wp-content/themes/madara/images/dflazy.jpg">
</div>
<div class="page-break no-gaps">
<img id="image-8" data-src="{base}09.jpg"
src="https://www.webtoon.xyz/wp-content/themes/madara/images/dflazy.jpg">
</div>
<div class="page-break no-gaps">
<img id="image-9" data-src="{base}10.jpg"
src="https://www.webtoon.xyz/wp-content/themes/madara/images/dflazy.jpg">
</div>
<div class="page-break no-gaps">
<img id="image-10" data-src="{base}11.jpg"
src="https://www.webtoon.xyz/wp-content/themes/madara/images/dflazy.jpg">
</div>
<div class="page-break no-gaps">
<img id="image-11" data-src="{base}12.jpg"
src="https://www.webtoon.xyz/wp-content/themes/madara/images/dflazy.jpg">
</div>
<div class="page-break no-gaps">
<img id="image-12" data-src="{base}13.jpg"
src="https://www.webtoon.xyz/wp-content/themes/madara/images/dflazy.jpg">
</div>
<div class="page-break no-gaps">
<img id="image-13" data-src="{base}14.jpg"
src="https://www.webtoon.xyz/wp-content/themes/madara/images/dflazy.jpg">
</div>
<div class="page-break no-gaps">
<img id="image-14" data-src="{base}15.jpg"
src="https://www.webtoon.xyz/wp-content/themes/madara/images/dflazy.jpg">
</div>
</div>
<div class="entry-header footer"></div>
""".format(base=IMAGE_BASE)


def manga_html():
    items = []
    for chapter in range(34, 0, -1):
        items.append("""\
<li class="wp-manga-chapter">
<a href="{url}chapter-{chapter}/">Chapter {chapter}</a>
</li>
""".format(url=MANGA_URL, chapter=chapter))

    return """\
<h1>I Became an Apartment Security Manager</h1>
<div class="post-content_item">
<div class="summary-heading"><h5>Alternative</h5></div>
<div class="summary-content">아파트 관리인이 되었다</div>
</div>
<div class="post-content_item">
<div class="summary-heading"><h5>Author(s)</h5></div>
<div class="summary-content"><div class="author-content">
<a href="{url}author/" rel="tag">Bibik</a></div></div>
</div>
<div class="post-content_item">
<div class="summary-heading"><h5>Artist(s)</h5></div>
<div class="summary-content"><div class="artist-content">
<a href="{url}artist/" rel="tag">Beluga</a></div></div>
</div>
<div class="post-content_item">
<div class="summary-heading"><h5>Genre(s)</h5></div>
<div class="summary-content"><div class="genres-content">
<a href="{url}drama/" rel="tag">Drama</a>,
<a href="{url}harem/" rel="tag">Harem</a>,
<a href="{url}mature/" rel="tag">Mature</a>
</div></div>
</div>
<div class="post-content_item">
<div class="summary-heading"><h5>Type</h5></div>
<div class="summary-content">Manhwa</div>
</div>
<div class="post-content_item">
<div class="summary-heading"><h5>Release</h5></div>
<div class="summary-content"><a href="{url}2025/" rel="tag">2025</a></div>
</div>
<div class="post-content_item">
<div class="summary-heading"><h5>Status</h5></div>
<div class="summary-content">OnGoing</div>
</div>
<div class="summary__content">
<p>Lee Han's life was going nowhere until he received an offer too tempting
and dangerous to ignore.</p>
</div>
<span class="score font-meta total_votes">4.3</span>
<ul class="main version-chap no-volumn">
{items}</ul>
""".format(url=MANGA_URL, items="".join(items))


def home_html(entries, next_url=None):
    items = []
    for slug, title in entries:
        items.append("""\
<div class="page-item-detail manga">
<div class="item-thumb c-image-hover">
<a href="https://www.webtoon.xyz/read/{slug}/" title="{title}">
<img src="cover.jpg"></a>
</div>
<div class="item-summary">
<h3><a href="https://www.webtoon.xyz/read/{slug}/">{title}</a></h3>
<div class="list-chapter">
<a href="https://www.webtoon.xyz/read/{slug}/chapter-1/" class="btn-link">
Chapter 1</a>
</div>
</div>
</div>
""".format(slug=slug, title=title))

    if next_url:
        items.append(
            '<a class="nextpostslink" rel="next" href="{}">»</a>'.format(
                next_url,
            ),
        )

    return "".join(items)


class TestWebtoonxyzChapterExtractor(unittest.TestCase):

    def test_images(self):
        extr = webtoonxyz.WebtoonxyzChapterExtractor.from_url(CHAPTER_URL)
        images = [url for url, _ in extr.images(chapter_html())]

        self.assertEqual(images, [
            IMAGE_BASE + "01.jpg",
            IMAGE_BASE + "02.jpg",
            IMAGE_BASE + "03.jpg",
            IMAGE_BASE + "04.jpg",
            IMAGE_BASE + "05.jpg",
            IMAGE_BASE + "06.jpg",
            IMAGE_BASE + "07.jpg",
            IMAGE_BASE + "08.jpg",
            IMAGE_BASE + "09.jpg",
            IMAGE_BASE + "10.jpg",
            IMAGE_BASE + "11.jpg",
            IMAGE_BASE + "12.jpg",
            IMAGE_BASE + "13.jpg",
            IMAGE_BASE + "14.jpg",
            IMAGE_BASE + "15.jpg",
        ])

    def test_minor_chapter_url_matches(self):
        extr = webtoonxyz.WebtoonxyzChapterExtractor.from_url(
            MINOR_CHAPTER_URL,
        )
        self.assertIsInstance(extr, webtoonxyz.WebtoonxyzChapterExtractor)


class TestWebtoonxyzMangaExtractor(unittest.TestCase):

    def test_chapters(self):
        extr = webtoonxyz.WebtoonxyzMangaExtractor.from_url(MANGA_URL)
        chapters = extr.chapters(manga_html())

        self.assertEqual(len(chapters), 34)
        self.assertEqual(chapters[0][0], MANGA_URL + "chapter-34/")
        self.assertEqual(chapters[-1][0], MANGA_URL + "chapter-1/")

        data = chapters[0][1]
        self.assertEqual(
            data["manga"],
            "I Became an Apartment Security Manager",
        )
        self.assertEqual(data["manga_alt"], ["아파트 관리인이 되었다"])
        self.assertEqual(data["author"], ["Bibik"])
        self.assertEqual(data["artist"], ["Beluga"])
        self.assertEqual(data["genres"], ["Drama", "Harem", "Mature"])
        self.assertEqual(data["type"], "Manhwa")
        self.assertEqual(data["release"], 2025)
        self.assertEqual(data["status"], "OnGoing")
        self.assertEqual(data["rating"], 4.3)
        self.assertEqual(data["chapter"], 34)
        self.assertEqual(data["chapter_minor"], "")
        self.assertEqual(data["title"], "")
        self.assertIn("Lee Han's life was going nowhere", data["description"])


class TestWebtoonxyzHomeExtractor(unittest.TestCase):

    def test_mangas(self):
        extr = webtoonxyz.WebtoonxyzHomeExtractor.from_url(
            "https://www.webtoon.xyz/",
        )
        urls = list(extr.mangas(home_html((
            ("jungle-juice", "Jungle Juice"),
            (
                "i-became-an-apartment-security-manager",
                "I Became an Apartment Security Manager",
            ),
        ))))

        self.assertEqual(urls, [
            "https://www.webtoon.xyz/read/jungle-juice/",
            "https://www.webtoon.xyz/read/"
            "i-became-an-apartment-security-manager/",
        ])

    def test_items_paginate(self):
        pages = {
            "https://www.webtoon.xyz/page/2/": home_html((
                ("jungle-juice", "Jungle Juice"),
                (
                    "i-became-an-apartment-security-manager",
                    "I Became an Apartment Security Manager",
                ),
            ), next_url="/page/4/"),
            "https://www.webtoon.xyz/page/4/": home_html((
                ("reality-quest", "Reality Quest"),
            )),
        }
        extr = webtoonxyz.WebtoonxyzHomeExtractor.from_url(HOME_URL)
        extr.request = lambda url: type("Response", (), {"text": pages[url]})()

        items = list(extr.items())

        self.assertEqual([item[1] for item in items], [
            "https://www.webtoon.xyz/read/jungle-juice/",
            "https://www.webtoon.xyz/read/"
            "i-became-an-apartment-security-manager/",
            "https://www.webtoon.xyz/read/reality-quest/",
        ])
        self.assertTrue(all(item[0] is Message.Queue for item in items))
        self.assertTrue(all(
            item[2]["_extractor"] is webtoonxyz.WebtoonxyzMangaExtractor
            for item in items
        ))


class TestWebtoonxyzFamilyMode(unittest.TestCase):

    def tearDown(self):
        config.clear()

    def test_chapter_initialize_sets_adult_cookie_by_default(self):
        with patch.object(
            webtoonxyz.WPMadaraChapterExtractor,
            "initialize",
            lambda self: setattr(self, "cookies", {}),
        ):
            extr = webtoonxyz.WebtoonxyzChapterExtractor.from_url(CHAPTER_URL)
            extr.initialize()

        self.assertEqual(extr.cookies.get("wpmanga-adault"), "1")

    def test_chapter_initialize_omits_adult_cookie_in_family_mode(self):
        config.set(("extractor", "webtoonxyz", "chapter"), "family-mode", True)

        with patch.object(
            webtoonxyz.WPMadaraChapterExtractor,
            "initialize",
            lambda self: setattr(self, "cookies", {}),
        ):
            extr = webtoonxyz.WebtoonxyzChapterExtractor.from_url(CHAPTER_URL)
            extr.initialize()

        self.assertNotIn("wpmanga-adault", extr.cookies)

    def test_manga_initialize_sets_adult_cookie_by_default(self):
        with patch.object(
            webtoonxyz.WPMadaraMangaExtractor,
            "initialize",
            lambda self: setattr(self, "cookies", {}),
        ):
            extr = webtoonxyz.WebtoonxyzMangaExtractor.from_url(MANGA_URL)
            extr.initialize()

        self.assertEqual(extr.cookies.get("wpmanga-adault"), "1")

    def test_manga_initialize_omits_adult_cookie_in_family_mode(self):
        config.set(("extractor", "webtoonxyz", "manga"), "family-mode", True)

        with patch.object(
            webtoonxyz.WPMadaraMangaExtractor,
            "initialize",
            lambda self: setattr(self, "cookies", {}),
        ):
            extr = webtoonxyz.WebtoonxyzMangaExtractor.from_url(MANGA_URL)
            extr.initialize()

        self.assertNotIn("wpmanga-adault", extr.cookies)

    def test_home_initialize_sets_adult_cookie_by_default(self):
        with patch.object(
            webtoonxyz.WPMadaraHomeExtractor,
            "initialize",
            lambda self: setattr(self, "cookies", {}),
        ):
            extr = webtoonxyz.WebtoonxyzHomeExtractor.from_url(HOME_URL)
            extr.initialize()

        self.assertEqual(extr.cookies.get("wpmanga-adault"), "1")

    def test_home_initialize_omits_adult_cookie_in_family_mode(self):
        config.set(("extractor", "webtoonxyz", "home"), "family-mode", True)

        with patch.object(
            webtoonxyz.WPMadaraHomeExtractor,
            "initialize",
            lambda self: setattr(self, "cookies", {}),
        ):
            extr = webtoonxyz.WebtoonxyzHomeExtractor.from_url(HOME_URL)
            extr.initialize()

        self.assertNotIn("wpmanga-adault", extr.cookies)


if __name__ == "__main__":
    unittest.main()
