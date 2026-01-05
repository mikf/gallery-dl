# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://sexygirlspics.com/"""

import re

from .common import Extractor, GalleryExtractor, Message
from .. import text


BASE_PATTERN = r"(?:https?://)?(?:www\.)?sexygirlspics\.com"


def _normalize_url(url, root):
    url = text.unescape(url).strip()
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/"):
        return root + url
    return url


class SexygirlspicsBaseExtractor(Extractor):
    category = "sexygirlspics"
    root = "https://sexygirlspics.com"


class SexygirlspicsTagExtractor(SexygirlspicsBaseExtractor):
    """Extractor for album URLs from tag/category pages"""
    subcategory = "tag"
    pattern = (BASE_PATTERN +
               r"/(?!pics(?:/|$))(?!page(?:/|$))([a-z0-9-]+)/?$")
    example = "https://sexygirlspics.com/shaved/"

    def items(self):
        tag = self.groups[0]
        url = f"{self.root}/{tag}/"

        data = {"tag": tag}
        yield Message.Directory, "", data

        seen = set()
        page = self.request(url, notfound="tag").text

        for href in text.extract_iter(page, "href='https://sexygirlspics.com/pics/", "'"):
            yield from self._queue_album(
                "https://sexygirlspics.com/pics/" + href, seen, data)
        for href in text.extract_iter(page, 'href="https://sexygirlspics.com/pics/', '"'):
            yield from self._queue_album(
                "https://sexygirlspics.com/pics/" + href, seen, data)

    def _queue_album(self, url, seen, data):
        url = url.partition("#")[0]
        if not url.endswith("/"):
            url += "/"
        if url in seen:
            return
        seen.add(url)
        yield Message.Queue, url, data


class SexygirlspicsAlbumExtractor(SexygirlspicsBaseExtractor, GalleryExtractor):
    """Extractor for individual albums"""
    subcategory = "gallery"
    pattern = BASE_PATTERN + r"/pics/([^/?#]+)/?$"
    example = ("https://sexygirlspics.com/pics/"
               "blonde-teen-ashlee-cox-has-a-threesome-with-a-couple-98021229/")

    filename_fmt = "{gallery_id}_{num:>03}.{extension}"
    directory_fmt = ("{category}", "{gallery_id} {title}")
    archive_fmt = "{gallery_id}_{num}"

    def __init__(self, match):
        slug = match.group(1)
        url = f"{self.root}/pics/{slug}/"
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)
        title = extr("<title>", "</title>").strip()
        if title:
            title = text.unescape(title)

        slug = self.groups[0]
        gallery_id = text.parse_int(slug.rsplit("-", 1)[-1])

        return {
            "gallery_id": gallery_id,
            "slug": slug,
            "title": title or slug,
        }

    def images(self, page):
        urls = []
        seen = set()

        prefix = "https://cdni.sexygirlspics.com/1280/"
        for href in text.extract_iter(page, "href='" + prefix, "'"):
            url = prefix + href
            if url not in seen:
                seen.add(url)
                urls.append((url, None))
        for href in text.extract_iter(page, 'href="' + prefix, '"'):
            url = prefix + href
            if url not in seen:
                seen.add(url)
                urls.append((url, None))

        if urls:
            return urls

        # fallback: extract any image-like URLs from page source
        for begin, end in (
            ("href='", "'"),
            ('href="', '"'),
            ("data-src='", "'"),
            ('data-src="', '"'),
            ("src='", "'"),
            ('src="', '"'),
        ):
            for u in text.extract_iter(page, begin, end):
                u = _normalize_url(u, self.root)
                if u in seen:
                    continue
                if not re.search(r"\.(?:jpe?g|png|gif|webp)(?:$|[?#])", u, re.I):
                    continue
                seen.add(u)
                urls.append((u, None))
        return urls
