# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nudecollect.com/"""

from .common import GalleryExtractor
from .. import text


class NudecollectExtractor(GalleryExtractor):
    """Base class for Nudecollect extractors"""
    category = "nudecollect"
    directory_fmt = ("{category}", "{title}")
    filename_fmt = "{slug}_{num:>03}.{extension}"
    archive_fmt = "{slug}_{num}"
    root = "https://www.nudecollect.com"

    def request(self, url, **kwargs):
        kwargs["allow_redirects"] = False
        return GalleryExtractor.request(self, url, **kwargs)

    @staticmethod
    def get_title(page):
        return text.unescape(text.extr(page, "<title>", "</title>"))[31:]

    @staticmethod
    def get_image(page):
        return text.extr(page, '<img src="', '"')


class NudecollectImageExtractor(NudecollectExtractor):
    """Extractor for individual images from nudecollect.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:www\.)?nudecollect\.com"
               r"(/content/([^/?#]+)/image-(\d+)-pics-(\d+)"
               r"-mirror-(\d+)\.html)")
    example = ("https://www.nudecollect.com/content/12345_TITLE"
               "/image-1-pics-108-mirror-1.html")

    def __init__(self, match):
        NudecollectExtractor.__init__(self, match)
        _, self.slug, self.num, self.count, self.mirror = match.groups()

    def metadata(self, page):
        return {
            "slug"  : self.slug,
            "title" : self.get_title(page),
            "count" : text.parse_int(self.count),
            "mirror": text.parse_int(self.mirror),
        }

    def images(self, page):
        return ((self.get_image(page), {"num": text.parse_int(self.num)}),)


class NudecollectAlbumExtractor(NudecollectExtractor):
    """Extractor for image albums on nudecollect.com"""
    subcategory = "album"
    pattern = (r"(?:https?://)?(?:www\.)?nudecollect\.com"
               r"/content/([^/?#]+)/(?:index-mirror-(\d+)-(\d+)"
               r"|page-\d+-pics-(\d+)-mirror-(\d+))\.html")
    example = ("https://www.nudecollect.com/content/12345_TITLE"
               "/index-mirror-01-123.html")

    def __init__(self, match):
        self.slug = match.group(1)
        self.mirror = match.group(2) or match.group(5)
        self.count = text.parse_int(match.group(3) or match.group(4))
        url = "{}/content/{}/image-1-pics-{}-mirror-{}.html".format(
            self.root, self.slug, self.count, self.mirror)
        NudecollectExtractor.__init__(self, match, url)

    def metadata(self, page):
        return {
            "slug"  : self.slug,
            "title" : self.get_title(page),
            "mirror": text.parse_int(self.mirror),
        }

    def images(self, page):
        url = self.get_image(page)
        p1, _, p2 = url.partition("/image0")
        ufmt = p1 + "/image{:>05}" + p2[4:]
        return [(ufmt.format(num), None) for num in range(1, self.count + 1)]
