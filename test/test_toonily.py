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
from gallery_dl.extractor import toonily  # noqa E402
from gallery_dl.extractor.common import Message  # noqa E402


URL = "https://toonily.com/serie/bj-archmage/chapter-1/"
IMAGE_BASE = (
    "https://data.tnlycdn.com/chapters/manga_69a777df554f1/"
    "bdbb2b75b74c3b06fa2f3e15cc8477d9/BJ-Archmage_"
)
HOME_URL = "https://toonily.com/page/2/"
TAG_URL = "https://toonily.com/tag/harem/page/2/"
GENRE_URL = "https://toonily.com/genre/historical/page/2/"


def chapter_html(loading):
    return """\
<div id="btn-lazyload-controller-wrap">
<span>LOAD ALL IMAGES AT ONCE: </span>
<a href="javascript:void(0)" id="btn-lazyload-controller">
<i class="fas fa-toggle-{toggle}"></i></a></div>
<div class="reading-content">
<div class="page-break no-gaps">
<img id="image-0" src="{base}00.jpg" class="wp-manga-chapter-img"
loading="{loading}">
</div>
<div class="page-break no-gaps">
<img id="image-1" src="{base}01.jpg" class="wp-manga-chapter-img"
loading="{loading}">
</div>
</div>
<div class="page-break no-gaps">
<a href="https://discord.gg/B94xGE6" target="_blank" rel="nofollow noopener">
<img id="image-999" src="https://toonily.com/wp-content/assets/999.png"
class="wp-manga-chapter-img" loading="lazy"></a></div>
<div class="entry-header footer"></div>
""".format(
        base=IMAGE_BASE,
        loading=loading,
        toggle="on" if loading == "eager" else "off",
    )


def home_html(entries, next_url=None):
    items = []
    for slug, title in entries:
        items.append("""\
<div class="page-item-detail manga">
<div class="item-thumb c-image-hover">
<a href="https://toonily.com/serie/{slug}/" title="{title}">
<img src="https://static.tnlycdn.com/{slug}.jpg"></a>
</div>
<div class="item-summary">
<h3><a href="https://toonily.com/serie/{slug}/">{title}</a></h3>
<div class="list-chapter">
<a href="https://toonily.com/serie/{slug}/chapter-1/" class="btn-link">
Chapter 1</a>
</div>
</div>
</div>
""".format(slug=slug, title=title))

    if next_url:
        pagination = (
            '<a class="nextpostslink" rel="next" href="{}">»</a>'
        ).format(next_url)
    else:
        pagination = ""

    return "".join(items) + pagination


class TestToonilyChapterExtractor(unittest.TestCase):

    def _images(self, loading):
        extr = toonily.ToonilyChapterExtractor.from_url(URL)
        return [url for url, _ in extr.images(chapter_html(loading))]

    def test_images_lazy(self):
        self.assertEqual(self._images("lazy"), [
            IMAGE_BASE + "00.jpg",
            IMAGE_BASE + "01.jpg",
        ])

    def test_images_load_all(self):
        self.assertEqual(self._images("eager"), [
            IMAGE_BASE + "00.jpg",
            IMAGE_BASE + "01.jpg",
        ])


class TestToonilyHomeExtractor(unittest.TestCase):

    def test_mangas(self):
        extr = toonily.ToonilyHomeExtractor.from_url(HOME_URL)
        urls = list(extr.mangas(home_html((
            ("living-in-america-6639a974", "Living in America"),
            ("rooftop-sex-king-e0ec66e5", "Rooftop Sex King"),
        ))))

        self.assertEqual(urls, [
            "https://toonily.com/serie/living-in-america-6639a974/",
            "https://toonily.com/serie/rooftop-sex-king-e0ec66e5/",
        ])

    def test_items_paginate(self):
        pages = {
            "https://toonily.com/page/2/": home_html((
                ("living-in-america-6639a974", "Living in America"),
                ("rooftop-sex-king-e0ec66e5", "Rooftop Sex King"),
            ), next_url="/page/4/"),
            "https://toonily.com/page/4/": home_html((
                ("ground-and-pound-2faa1a4a", "Ground and Pound"),
            )),
        }
        extr = toonily.ToonilyHomeExtractor.from_url(HOME_URL)
        extr.request = lambda url: type("Response", (), {"text": pages[url]})()

        items = list(extr.items())

        self.assertEqual(
            [item[1] for item in items],
            [
                "https://toonily.com/serie/living-in-america-6639a974/",
                "https://toonily.com/serie/rooftop-sex-king-e0ec66e5/",
                "https://toonily.com/serie/ground-and-pound-2faa1a4a/",
            ],
        )
        self.assertTrue(all(item[0] is Message.Queue for item in items))
        self.assertTrue(all(
            item[2]["_extractor"] is toonily.ToonilyMangaExtractor
            for item in items
        ))


class TestToonilyTaxonomyExtractors(unittest.TestCase):

    def test_tag_page_url(self):
        extr = toonily.ToonilyTagExtractor.from_url(TAG_URL)

        self.assertEqual(extr.page_url(1), "https://toonily.com/tag/harem/")
        self.assertEqual(
            extr.page_url(3),
            "https://toonily.com/tag/harem/page/3/",
        )

    def test_genre_page_url(self):
        extr = toonily.ToonilyGenreExtractor.from_url(GENRE_URL)

        self.assertEqual(
            extr.page_url(1),
            "https://toonily.com/genre/historical/",
        )
        self.assertEqual(
            extr.page_url(3),
            "https://toonily.com/genre/historical/page/3/",
        )

    def test_tag_items_paginate(self):
        pages = {
            "https://toonily.com/tag/harem/page/2/": home_html((
                (
                    "regressed-warriors-female-dominance-diary-2b6c9258",
                    "Regressed Warrior's Female Dominance Diary",
                ),
                (
                    "my-lewd-college-friends-d22b396c",
                    "My Lewd College Friends",
                ),
            ), next_url="/tag/harem/page/4/"),
            "https://toonily.com/tag/harem/page/4/": home_html((
                (
                    "turning-my-life-around-with-crypto-a1a1cc09",
                    "Turning My Life Around With Crypto",
                ),
            )),
        }
        extr = toonily.ToonilyTagExtractor.from_url(TAG_URL)
        extr.request = lambda url: type("Response", (), {"text": pages[url]})()

        items = list(extr.items())

        self.assertEqual([item[1] for item in items], [
            "https://toonily.com/serie/"
            "regressed-warriors-female-dominance-diary-2b6c9258/",
            "https://toonily.com/serie/my-lewd-college-friends-d22b396c/",
            "https://toonily.com/serie/"
            "turning-my-life-around-with-crypto-a1a1cc09/",
        ])
        self.assertTrue(all(item[0] is Message.Queue for item in items))
        self.assertTrue(all(
            item[2]["_extractor"] is toonily.ToonilyMangaExtractor
            for item in items
        ))

    def test_genre_items_paginate(self):
        pages = {
            "https://toonily.com/genre/historical/page/2/": home_html((
                ("her-tale-of-shim-chong", "Her Tale of Shim Chong"),
                (
                    "master-villainess-the-invincible",
                    "Master Villainess the Invincible!",
                ),
            ), next_url="/genre/historical/page/4/"),
            "https://toonily.com/genre/historical/page/4/": home_html((
                ("madam-1308167e", "Madam"),
            )),
        }
        extr = toonily.ToonilyGenreExtractor.from_url(GENRE_URL)
        extr.request = lambda url: type("Response", (), {"text": pages[url]})()

        items = list(extr.items())

        self.assertEqual([item[1] for item in items], [
            "https://toonily.com/serie/her-tale-of-shim-chong/",
            "https://toonily.com/serie/master-villainess-the-invincible/",
            "https://toonily.com/serie/madam-1308167e/",
        ])
        self.assertTrue(all(item[0] is Message.Queue for item in items))
        self.assertTrue(all(
            item[2]["_extractor"] is toonily.ToonilyMangaExtractor
            for item in items
        ))


class TestToonilyFamilyMode(unittest.TestCase):

    def tearDown(self):
        config.clear()

    def test_chapter_initialize_sets_mature_cookie_by_default(self):
        with patch.object(
            toonily.WPMadaraChapterExtractor,
            "initialize",
            lambda self: setattr(self, "cookies", {}),
        ):
            extr = toonily.ToonilyChapterExtractor.from_url(URL)
            extr.initialize()

        self.assertEqual(extr.cookies.get("toonily-mature"), "1")

    def test_chapter_initialize_omits_mature_cookie_in_family_mode(self):
        config.set(("extractor", "toonily", "chapter"), "family-mode", True)

        with patch.object(
            toonily.WPMadaraChapterExtractor,
            "initialize",
            lambda self: setattr(self, "cookies", {}),
        ):
            extr = toonily.ToonilyChapterExtractor.from_url(URL)
            extr.initialize()

        self.assertNotIn("toonily-mature", extr.cookies)

    def test_manga_initialize_sets_mature_cookie_by_default(self):
        with patch.object(
            toonily.WPMadaraMangaExtractor,
            "initialize",
            lambda self: setattr(self, "cookies", {}),
        ):
            extr = toonily.ToonilyMangaExtractor.from_url(
                "https://toonily.com/serie/bj-archmage/",
            )
            extr.initialize()

        self.assertEqual(extr.cookies.get("toonily-mature"), "1")

    def test_manga_initialize_omits_mature_cookie_in_family_mode(self):
        config.set(("extractor", "toonily", "manga"), "family-mode", True)

        with patch.object(
            toonily.WPMadaraMangaExtractor,
            "initialize",
            lambda self: setattr(self, "cookies", {}),
        ):
            extr = toonily.ToonilyMangaExtractor.from_url(
                "https://toonily.com/serie/bj-archmage/",
            )
            extr.initialize()

        self.assertNotIn("toonily-mature", extr.cookies)

    def test_home_initialize_sets_mature_cookie_by_default(self):
        with patch.object(
            toonily.WPMadaraHomeExtractor,
            "initialize",
            lambda self: setattr(self, "cookies", {}),
        ):
            extr = toonily.ToonilyHomeExtractor.from_url(
                "https://toonily.com/",
            )
            extr.initialize()

        self.assertEqual(extr.cookies.get("toonily-mature"), "1")

    def test_home_initialize_omits_mature_cookie_in_family_mode(self):
        config.set(("extractor", "toonily", "home"), "family-mode", True)

        with patch.object(
            toonily.WPMadaraHomeExtractor,
            "initialize",
            lambda self: setattr(self, "cookies", {}),
        ):
            extr = toonily.ToonilyHomeExtractor.from_url(
                "https://toonily.com/",
            )
            extr.initialize()

        self.assertNotIn("toonily-mature", extr.cookies)

    def test_tag_initialize_omits_mature_cookie_in_family_mode(self):
        config.set(("extractor", "toonily", "tag"), "family-mode", True)

        with patch.object(
            toonily.WPMadaraHomeExtractor,
            "initialize",
            lambda self: setattr(self, "cookies", {}),
        ):
            extr = toonily.ToonilyTagExtractor.from_url(
                "https://toonily.com/tag/harem/",
            )
            extr.initialize()

        self.assertNotIn("toonily-mature", extr.cookies)

    def test_genre_initialize_omits_mature_cookie_in_family_mode(self):
        config.set(("extractor", "toonily", "genre"), "family-mode", True)

        with patch.object(
            toonily.WPMadaraHomeExtractor,
            "initialize",
            lambda self: setattr(self, "cookies", {}),
        ):
            extr = toonily.ToonilyGenreExtractor.from_url(
                "https://toonily.com/genre/historical/",
            )
            extr.initialize()

        self.assertNotIn("toonily-mature", extr.cookies)


if __name__ == "__main__":
    unittest.main()
