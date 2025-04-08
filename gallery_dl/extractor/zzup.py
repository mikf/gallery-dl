# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://zzup.com/"""

from .common import GalleryExtractor
from .. import text


class ZzupGalleryExtractor(GalleryExtractor):
    category = "zzup"
    directory_fmt = ("{category}", "{title}")
    filename_fmt = "{num:>03}.{extension}"
    archive_fmt = "{slug}_{num}"
    root = "https://zzup.com"
    pattern = (r"(?:https?://)?(up\.|w+\.)?zzup\.com(/(?:viewalbum|content)"
               r"/[\w=]+/([^/?#]+)/[\w=]+)/(?:index|page-\d+)\.html")
    example = "https://zzup.com/content/xyz=/12345_TITLE/123=/index.html"

    def __init__(self, match):
        subdomain, path, self.slug = match.groups()
        if subdomain == "up.":
            self.root = "https://up.zzup.com"
            self.images = self.images_v2
        url = "{}{}/index.html".format(self.root, path)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        return {
            "slug" : self.slug,
            "title": text.unescape(text.extr(
                page, "<title>", "</title>"))[:-11],
        }

    def images(self, page):
        path = text.extr(page, 'class="picbox"><a target="_blank" href="', '"')
        count = text.parse_int(text.extr(path, "-pics-", "-mirror"))
        page = self.request(self.root + path).text
        url = self.root + text.extr(page, '\n<a href="', '"')
        p1, _, p2 = url.partition("/image0")
        ufmt = p1 + "/image{:>05}" + p2[4:]
        return [(ufmt.format(num), None) for num in range(1, count + 1)]

    def images_v2(self, page):
        results = []

        while True:
            for path in text.extract_iter(
                    page, ' class="picbox"><a target="_blank" href="', '"'):
                results.append(("{}/showimage/{}/zzup.com.jpg".format(
                    self.root, "/".join(path.split("/")[2:-2])), None))

            pos = page.find("glyphicon-arrow-right")
            if pos < 0:
                break
            path = text.rextract(page, ' href="', '"', pos)[0]
            page = self.request(text.urljoin(self.gallery_url, path)).text

        return results
