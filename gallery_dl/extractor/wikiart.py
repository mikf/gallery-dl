# -*- coding: utf-8 -*-

# Copyright 2019-2025 Mike Fährmann
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
        self.lang = match[1]

    def items(self):
        data = self.metadata()
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
            data = self.request_json(url, headers=headers, params=params)
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
    example = "https://www.wikiart.org/en/ARTIST"

    def __init__(self, match):
        WikiartExtractor.__init__(self, match)
        self.artist_name = match[2]
        self.artist = None

    def metadata(self):
        url = f"{self.root}/{self.lang}/{self.artist_name}?json=2"
        self.artist = self.request_json(url)
        return {"artist": self.artist}

    def paintings(self):
        url = f"{self.root}/{self.lang}/{self.artist_name}/mode/all-paintings"
        return self._pagination(url)


class WikiartImageExtractor(WikiartArtistExtractor):
    """Extractor for individual paintings on wikiart.org"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/(?!(?:paintings|artists)-by-)([\w-]+)/([\w-]+)"
    example = "https://www.wikiart.org/en/ARTIST/TITLE"

    def __init__(self, match):
        WikiartArtistExtractor.__init__(self, match)
        self.title = match[3]

    def paintings(self):
        title, sep, year = self.title.rpartition("-")
        if not sep or not year.isdecimal():
            title = self.title
        url = (f"{self.root}/{self.lang}/Search/"
               f"{self.artist.get('artistName') or self.artist_name} {title}")
        return self._pagination(url, stop=True)


class WikiartArtworksExtractor(WikiartExtractor):
    """Extractor for artwork collections on wikiart.org"""
    subcategory = "artworks"
    directory_fmt = ("{category}", "Artworks by {group!c}", "{type}")
    pattern = BASE_PATTERN + r"/paintings-by-([\w-]+)/([\w-]+)"
    example = "https://www.wikiart.org/en/paintings-by-GROUP/TYPE"

    def __init__(self, match):
        WikiartExtractor.__init__(self, match)
        self.group = match[2]
        self.type = match[3]

    def metadata(self):
        return {"group": self.group, "type": self.type}

    def paintings(self):
        url = f"{self.root}/{self.lang}/paintings-by-{self.group}/{self.type}"
        return self._pagination(url)


class WikiartArtistsExtractor(WikiartExtractor):
    """Extractor for artist collections on wikiart.org"""
    subcategory = "artists"
    pattern = (BASE_PATTERN + r"/artists-by-([\w-]+)/([\w-]+)")
    example = "https://www.wikiart.org/en/artists-by-GROUP/TYPE"

    def __init__(self, match):
        WikiartExtractor.__init__(self, match)
        self.group = match[2]
        self.type = match[3]

    def items(self):
        url = f"{self.root}/{self.lang}/App/Search/Artists-by-{self.group}"
        params = {"json": "3", "searchterm": self.type}

        for artist in self._pagination(url, params, "Artists"):
            artist["_extractor"] = WikiartArtistExtractor
            yield Message.Queue, self.root + artist["artistUrl"], artist
