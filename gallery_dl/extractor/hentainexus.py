# -*- coding: utf-8 -*-

# Copyright 2019-2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentainexus.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util
import binascii


class HentainexusGalleryExtractor(GalleryExtractor):
    """Extractor for hentainexus galleries"""
    category = "hentainexus"
    root = "https://hentainexus.com"
    pattern = (r"(?i)(?:https?://)?(?:www\.)?hentainexus\.com"
               r"/(?:view|read)/(\d+)")
    example = "https://hentainexus.com/view/12345"

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = "{}/view/{}".format(self.root, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        rmve = text.remove_html
        extr = text.extract_from(page)
        data = {
            "gallery_id": text.parse_int(self.gallery_id),
            "cover"     : extr('"og:image" content="', '"'),
            "title"     : extr('<h1 class="title">', '</h1>'),
        }

        for key in ("Artist", "Book", "Circle", "Event", "Language",
                    "Magazine", "Parody", "Publisher", "Description"):
            value = rmve(extr('viewcolumn">' + key + '</td>', '</td>'))
            value, sep, rest = value.rpartition(" (")
            data[key.lower()] = value if sep else rest

        data["tags"] = tags = []
        for k in text.extract_iter(page, '<a href="/?q=tag:', '"'):
            tags.append(text.unquote(k).strip('"').replace("+", " "))

        if not data["language"]:
            data["language"] = "English"
        data["lang"] = util.language_to_code(data["language"])

        if "doujin" in data["tags"]:
            data["type"] = "Doujinshi"
        elif "illustration" in data["tags"]:
            data["type"] = "Illustration"
        else:
            data["type"] = "Manga"
        data["title_conventional"] = self._join_title(data)
        return data

    def images(self, _):
        url = "{}/read/{}".format(self.root, self.gallery_id)
        page = self.request(url).text
        imgs = util.json_loads(self._decode(text.extr(
            page, 'initReader("', '"')))

        headers = None
        if not self.config("original", True):
            headers = {"Accept": "image/webp,*/*"}
            for img in imgs:
                img["_http_headers"] = headers

        results = []
        for img in imgs:
            try:
                results.append((img["image"], img))
            except KeyError:
                pass
        return results

    @staticmethod
    def _decode(data):
        # https://hentainexus.com/static/js/reader.min.js?r=22
        hostname = "hentainexus.com"
        primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53)
        blob = list(binascii.a2b_base64(data))
        for i in range(0, len(hostname)):
            blob[i] = blob[i] ^ ord(hostname[i])

        key = blob[0:64]

        C = 0
        for k in key:
            C = C ^ k
            for _ in range(8):
                if C & 1:
                    C = C >> 1 ^ 0xc
                else:
                    C = C >> 1
        k = primes[C & 0x7]

        x = 0
        S = list(range(256))
        for i in range(256):
            x = (x + S[i] + key[i % len(key)]) % 256
            S[i], S[x] = S[x], S[i]

        result = ""
        a = c = m = x = 0
        for n in range(64, len(blob)):
            a = (a + k) % 256
            x = (c + S[(x + S[a]) % 256]) % 256
            c = (c + a + S[a]) % 256

            S[a], S[x] = S[x], S[a]
            m = S[(x + S[(a + S[(m + c) % 256]) % 256]) % 256]
            result += chr(blob[n] ^ m)

        return result

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
    """Extractor for hentainexus search results"""
    category = "hentainexus"
    subcategory = "search"
    root = "https://hentainexus.com"
    pattern = (r"(?i)(?:https?://)?(?:www\.)?hentainexus\.com"
               r"(?:/page/\d+)?/?(?:\?(q=[^/?#]+))?$")
    example = "https://hentainexus.com/?q=QUERY"

    def items(self):
        params = text.parse_query(self.groups[0])
        data = {"_extractor": HentainexusGalleryExtractor}
        path = "/"

        while path:
            page = self.request(self.root + path, params=params).text
            extr = text.extract_from(page)

            while True:
                gallery_id = extr('<a href="/view/', '"')
                if not gallery_id:
                    break
                yield Message.Queue, self.root + "/view/" + gallery_id, data

            path = extr('class="pagination-next" href="', '"')
