# -*- coding: utf-8 -*-

# Copyright 2019-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentainexus.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util
import json


class HentainexusGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries on hentainexus.com"""
    category = "hentainexus"
    root = "https://hentainexus.com"
    pattern = (r"(?i)(?:https?://)?(?:www\.)?hentainexus\.com"
               r"/(?:view|read)/(\d+)")
    test = (
        ("https://hentainexus.com/view/5688", {
            "url": "746d0043e20030f1171aae5ea113176607302517",
            "keyword": "5e5bb4b1553b1c6e126b198f9ae017a1a5d0a5ad",
        }),
        ("https://hentainexus.com/read/5688"),
    )

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = "{}/view/{}".format(self.root, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        rmve = text.remove_html
        extr = text.extract_from(page)
        data = {
            "gallery_id": text.parse_int(self.gallery_id),
            "tags"      : extr('"og:description" content="', '"').split(", "),
            "thumbnail" : extr('"og:image" content="', '"'),
            "title"     : extr('<h1 class="title">', '</h1>'),
        }
        for key in ("Artist", "Book", "Circle", "Event", "Language",
                    "Magazine", "Parody", "Publisher", "Description"):
            data[key.lower()] = rmve(extr(
                'viewcolumn">' + key + '</td>', '</td>'))
        data["lang"] = util.language_to_code(data["language"])

        if 'doujin' in data['tags']:
            data['type'] = 'Doujinshi'
        elif 'illustration' in data['tags']:
            data['type'] = 'Illustration'
        else:
            data['type'] = 'Manga'
        data["title_conventional"] = self._join_title(data)
        return data

    def images(self, _):
        url = "{}/read/{}".format(self.root, self.gallery_id)
        page = self.request(url).text
        urls = text.extract(page, "initReader(", "]")[0] + "]"
        return [(url, None) for url in json.loads(urls)]

    @staticmethod
    def _join_title(data):
        event = data['event']
        artist = data['artist']
        circle = data['circle']
        title = data['title']
        parody = data['parody']
        book = data['book']
        magazine = data['magazine']

        # a few galleries have a large number of artists or parodies,
        # which get replaced with "Various" in the title string
        if artist.count(',') >= 3:
            artist = 'Various'
        if parody.count(',') >= 3:
            parody = 'Various'

        jt = ''
        if event:
            jt += '({}) '.format(event)
        if circle:
            jt += '[{} ({})] '.format(circle, artist)
        else:
            jt += '[{}] '.format(artist)
        jt += title
        if parody.lower() != 'original work':
            jt += ' ({})'.format(parody)
        if book:
            jt += ' ({})'.format(book)
        if magazine:
            jt += ' ({})'.format(magazine)
        return jt


class HentainexusSearchExtractor(Extractor):
    """Extractor for search results on hentainexus.com"""
    category = "hentainexus"
    subcategory = "search"
    root = "https://hentainexus.com"
    pattern = (r"(?i)(?:https?://)?(?:www\.)?hentainexus\.com"
               r"(?:/page/\d+)?/?(?:\?(q=[^/?#]+))?$")
    test = (
        ("https://hentainexus.com/?q=tag:%22heart+pupils%22%20tag:group", {
            "pattern": HentainexusGalleryExtractor.pattern,
            "count": ">= 50",
        }),
        ("https://hentainexus.com/page/3?q=tag:%22heart+pupils%22"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.params = text.parse_query(match.group(1))

    def items(self):
        params = self.params
        path = "/"
        data = {"_extractor": HentainexusGalleryExtractor}

        while path:
            page = self.request(self.root + path, params=params).text
            extr = text.extract_from(page)

            while True:
                gallery_id = extr('<a href="/view/', '"')
                if not gallery_id:
                    break
                yield Message.Queue, self.root + "/view/" + gallery_id, data

            path = extr('class="pagination-next" href="', '"')
