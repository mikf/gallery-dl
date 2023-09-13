# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://jpg1.su/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?jpe?g\d?\.(?:su|pet|fish(?:ing)?|church)"


class JpgfishExtractor(Extractor):
    """Base class for jpgfish extractors"""
    category = "jpgfish"
    root = "https://jpg1.su"
    directory_fmt = ("{category}", "{user}", "{album}",)
    archive_fmt = "{id}"

    def _pagination(self, url):
        while url:
            page = self.request(url).text

            for item in text.extract_iter(
                    page, '<div class="list-item-image ', 'image-container'):
                yield text.extract(item, '<a href="', '"')[0]

            url = text.extract(
                page, '<a data-pagination="next" href="', '" ><')[0]


class JpgfishImageExtractor(JpgfishExtractor):
    """Extractor for jpgfish Images"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/img/((?:[^/?#]+\.)?(\w+))"
    example = "https://jpg1.su/img/TITLE.ID"

    def __init__(self, match):
        JpgfishExtractor.__init__(self, match)
        self.path, self.image_id = match.groups()

    def items(self):
        url = "{}/img/{}".format(self.root, self.path)
        extr = text.extract_from(self.request(url).text)

        image = {
            "id"   : self.image_id,
            "url"  : extr('<meta property="og:image" content="', '"'),
            "album": text.extract(extr(
                "Added to <a", "/a>"), ">", "<")[0] or "",
            "user" : extr('username: "', '"'),
        }

        text.nameext_from_url(image["url"], image)
        yield Message.Directory, image
        yield Message.Url, image["url"], image


class JpgfishAlbumExtractor(JpgfishExtractor):
    """Extractor for jpgfish Albums"""
    subcategory = "album"
    pattern = BASE_PATTERN + r"/a(?:lbum)?/([^/?#]+)(/sub)?"
    example = "https://jpg1.su/album/TITLE.ID"

    def __init__(self, match):
        JpgfishExtractor.__init__(self, match)
        self.album, self.sub_albums = match.groups()

    def items(self):
        url = "{}/a/{}".format(self.root, self.album)
        data = {"_extractor": JpgfishImageExtractor}

        if self.sub_albums:
            albums = self._pagination(url + "/sub")
        else:
            albums = (url,)

        for album in albums:
            for image in self._pagination(album):
                yield Message.Queue, image, data


class JpgfishUserExtractor(JpgfishExtractor):
    """Extractor for jpgfish Users"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!img|a(?:lbum)?)([^/?#]+)(/albums)?"
    example = "https://jpg1.su/USER"

    def __init__(self, match):
        JpgfishExtractor.__init__(self, match)
        self.user, self.albums = match.groups()

    def items(self):
        url = "{}/{}".format(self.root, self.user)

        if self.albums:
            url += "/albums"
            data = {"_extractor": JpgfishAlbumExtractor}
        else:
            data = {"_extractor": JpgfishImageExtractor}

        for url in self._pagination(url):
            yield Message.Queue, url, data
