# -*- coding: utf-8 -*-

# Copyright 2019-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.wikiart.org/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?wikiart\.org/([a-z]+)"


class WikiartExtractor(Extractor):
    """Base class for wikiart extractors"""
    category = "wikiart"
    filename_fmt = "{id}_{title}.{extension}"
    archive_fmt = "{id}"
    root = "https://www.wikiart.org"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.lang = match.group(1)

    def items(self):
        data = self.metadata()
        yield Message.Version, 1
        yield Message.Directory, data
        for painting in self.paintings():
            url = painting["image"]
            painting.update(data)
            yield Message.Url, url, text.nameext_from_url(url, painting)

    def metadata(self):
        """Return a dict with general metadata"""

    def paintings(self):
        """Return an iterable containing all relevant 'painting' objects"""

    def _pagination(self, url, extra_params=None, key="Paintings", stop=False):
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": url,
        }
        params = {
            "json": "2",
            "layout": "new",
            "page": 1,
            "resultType": "masonry",
        }
        if extra_params:
            params.update(extra_params)

        while True:
            data = self.request(url, headers=headers, params=params).json()
            items = data.get(key)
            if not items:
                return
            yield from items
            if stop:
                return
            params["page"] += 1


class WikiartArtistExtractor(WikiartExtractor):
    """Extractor for an artist's paintings on wikiart.org"""
    subcategory = "artist"
    directory_fmt = ("{category}", "{artist[artistName]}")
    pattern = BASE_PATTERN + r"/(?!\w+-by-)([\w-]+)/?$"
    test = ("https://www.wikiart.org/en/thomas-cole", {
        "url": "5ba2fbe6783fcce34e65014d16e5fbc581490c98",
        "keyword": "eb5b141cf33e6d279afd1518aae24e61cc0adf81",
    })

    def __init__(self, match):
        WikiartExtractor.__init__(self, match)
        self.artist_name = match.group(2)
        self.artist = None

    def metadata(self):
        url = "{}/{}/{}?json=2".format(self.root, self.lang, self.artist_name)
        self.artist = self.request(url).json()
        return {"artist": self.artist}

    def paintings(self):
        url = "{}/{}/{}/mode/all-paintings".format(
            self.root, self.lang, self.artist_name)
        return self._pagination(url)


class WikiartImageExtractor(WikiartArtistExtractor):
    """Extractor for individual paintings on wikiart.org"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/(?!(?:paintings|artists)-by-)([\w-]+)/([\w-]+)"
    test = (
        ("https://www.wikiart.org/en/thomas-cole/the-departure-1838", {
            "url": "4d9fd87680a2620eaeaf1f13e3273475dec93231",
            "keyword": "a1b083d500ce2fd364128e35b026e4ca526000cc",
        }),
        # no year or '-' in slug
        ("https://www.wikiart.org/en/huang-shen/summer", {
            "url": "d7f60118c34067b2b37d9577e412dc1477b94207",
        }),
    )

    def __init__(self, match):
        WikiartArtistExtractor.__init__(self, match)
        self.title = match.group(3)

    def paintings(self):
        title, sep, year = self.title.rpartition("-")
        if not sep or not year.isdecimal():
            title = self.title
        url = "{}/{}/Search/{} {}".format(
            self.root, self.lang,
            self.artist.get("artistName") or self.artist_name, title,
        )
        return self._pagination(url, stop=True)


class WikiartArtworksExtractor(WikiartExtractor):
    """Extractor for artwork collections on wikiart.org"""
    subcategory = "artworks"
    directory_fmt = ("{category}", "Artworks by {group!c}", "{type}")
    pattern = BASE_PATTERN + r"/paintings-by-([\w-]+)/([\w-]+)"
    test = ("https://www.wikiart.org/en/paintings-by-media/grisaille", {
        "url": "36e054fcb3363b7f085c81f4778e6db3994e56a3",
    })

    def __init__(self, match):
        WikiartExtractor.__init__(self, match)
        self.group = match.group(2)
        self.type = match.group(3)

    def metadata(self):
        return {"group": self.group, "type": self.type}

    def paintings(self):
        url = "{}/{}/paintings-by-{}/{}".format(
            self.root, self.lang, self.group, self.type)
        return self._pagination(url)


class WikiartArtistsExtractor(WikiartExtractor):
    """Extractor for artist collections on wikiart.org"""
    subcategory = "artists"
    pattern = (BASE_PATTERN + r"/artists-by-([\w-]+)/([\w-]+)")
    test = ("https://www.wikiart.org/en/artists-by-century/12", {
        "pattern": WikiartArtistExtractor.pattern,
        "count": ">= 8",
    })

    def __init__(self, match):
        WikiartExtractor.__init__(self, match)
        self.group = match.group(2)
        self.type = match.group(3)

    def items(self):
        url = "{}/{}/App/Search/Artists-by-{}".format(
            self.root, self.lang, self.group)
        params = {"json": "3", "searchterm": self.type}

        for artist in self._pagination(url, params, "Artists"):
            artist["_extractor"] = WikiartArtistExtractor
            yield Message.Queue, self.root + artist["artistUrl"], artist
