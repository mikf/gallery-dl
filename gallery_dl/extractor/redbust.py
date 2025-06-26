# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://redbust.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?redbust\.com"


class RedbustExtractor(Extractor):
    """Base class for RedBust extractors"""
    category = "redbust"
    root = "https://redbust.com"
    filename_fmt = "{filename}.{extension}"

    def items(self):
        data = {"_extractor": RedbustGalleryExtractor}
        for url in self.galleries():
            yield Message.Queue, url, data

    def _pagination(self, path, page=None):
        if page is None:
            url = f"{self.root}{path}/"
            base = url + "page/"
            page = self.request(url).text
        else:
            base = f"{self.root}{path}/page/"

        pnum = 1
        while True:
            for post in text.extract_iter(
                    page, '<h2 class="post-title">', "rel="):
                yield text.extr(post, 'href="', '"')

            pnum += 1
            url = f"{base}{pnum}/"
            if url not in page:
                return
            page = self.request(url).text


class RedbustGalleryExtractor(GalleryExtractor, RedbustExtractor):
    """Extractor for RedBust galleries"""
    pattern = BASE_PATTERN + r"/([\w-]+)/?$"
    example = "https://redbust.com/TITLE/"

    def items(self):
        url = f"{self.root}/{self.groups[0]}/"
        self.page = page = self.request(url).text

        self.gallery_id = gid = text.extr(
            page, "<link rel='shortlink' href='https://redbust.com/?p=", "'")

        if gid:
            self.page_url = False
            return GalleryExtractor.items(self)
        else:
            self.subcategory = "category"
            return self._items_category(page)

    def _items_category(self, _):
        page = self.page
        data = {"_extractor": RedbustGalleryExtractor}
        base = f"{self.root}/{self.groups[0]}/page/"
        pnum = 1

        while True:
            for post in text.extract_iter(
                    page, '<h2 class="post-title">', "rel="):
                url = text.extr(post, 'href="', '"')
                yield Message.Queue, url, data

            pnum += 1
            url = f"{base}{pnum}/"
            if url not in page:
                return
            page = self.request(url).text

    def metadata(self, _):
        extr = text.extract_from(self.page)

        return {
            "gallery_id"  : self.gallery_id,
            "gallery_slug": self.groups[0],
            "categories"  : text.split_html(extr(
                '<li class="category">', "</li>"))[::2],
            "title"       : text.unescape(extr('class="post-title">', "<")),
            "date"        : text.parse_datetime(
                extr('class="post-byline">', "<").strip(), "%B %d, %Y"),
            "views"       : text.parse_int(extr("</b>", "v").replace(",", "")),
            "tags"        : text.split_html(extr(
                'class="post-tags">', "</p"))[1:],
        }

    def images(self, _):
        results = []

        for img in text.extract_iter(self.page, "'><img ", ">"):
            if src := text.extr(img, 'src="', '"'):
                path, _, end = src.rpartition("-")
                if "x" in end:
                    url = f"{path}.{end.rpartition('.')[2]}"
                    data = None if src == url else {"_fallback": (src,)}
                else:
                    url = src
                    data = None
                results.append((url, data))

        if not results:
            # fallback for older galleries
            for path in text.extract_iter(
                    self.page, '<img src="/wp-content/uploads/', '"'):
                results.append(
                    (f"{self.root}/wp-content/uploads/{path}", None))

        return results


class RedbustTagExtractor(RedbustExtractor):
    """Extractor for RedBust tag searches"""
    subcategory = "tag"
    pattern = BASE_PATTERN + r"/tag/([\w-]+)"
    example = "https://redbust.com/tag/TAG/"

    def galleries(self):
        return self._pagination("/tag/" + self.groups[0])


class RedbustArchiveExtractor(RedbustExtractor):
    """Extractor for RedBust monthly archive collections"""
    subcategory = "archive"
    pattern = BASE_PATTERN + r"(/\d{4}/\d{2})"
    example = "https://redbust.com/2010/01/"

    def galleries(self):
        return self._pagination(self.groups[0])


class RedbustImageExtractor(RedbustExtractor):
    """Extractor for RedBust images"""
    subcategory = "image"
    directory_fmt = ("{category}", "{title}")
    pattern = BASE_PATTERN + r"/(?!tag/|\d{4}/)([\w-]+)/([\w-]+)/?$"
    example = "https://redbust.com/TITLE/SLUG/"

    def items(self):
        gallery_slug, image_slug = self.groups
        url = f"{self.root}/{gallery_slug}/{image_slug}/"
        page = self.request(url).text

        img_url = None

        # Look for the largest image in srcset first
        if srcset := text.extr(page, 'srcset="', '"'):
            # Extract the largest image from srcset (typically last one)
            urls = srcset.split(", ")
            img_url = urls[-1].partition(" ")[0] if urls else None

        # Fallback to original extraction method
        if not img_url:
            if entry := text.extr(page, "entry-inner ", "alt="):
                img_url = text.extr(entry, "img src=", " ").strip("\"'")

        if not img_url:
            return

        end = img_url.rpartition("-")[2]
        data = text.nameext_from_url(img_url, {
            "title"       : text.unescape(text.extr(
                page, 'title="Return to ', '"')),
            "image_id"    : text.extr(
                page, "rel='shortlink' href='https://redbust.com/?p=", "'"),
            "gallery_slug": gallery_slug,
            "image_slug"  : image_slug,
            "num"         : text.parse_int(end.partition(".")[0]),
            "count"       : 1,
            "url"         : img_url,
        })

        yield Message.Directory, data
        yield Message.Url, img_url, data
