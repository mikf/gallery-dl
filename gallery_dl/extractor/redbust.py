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


class RedbustGalleryExtractor(GalleryExtractor, RedbustExtractor):
    """Extractor for RedBust galleries"""
    pattern = BASE_PATTERN + r"/([\w-]+)/?$"
    example = "https://redbust.com/TITLE/"

    def __init__(self, match):
        Extractor.__init__(self, match)

    def items(self):
        url = f"{self.root}/{self.groups[0]}/"
        self.page = page = self.request(url).text

        self.gallery_id = gid = text.extr(
            page, "<link rel='shortlink' href='https://redbust.com/?p=", "'")

        if gid:
            self.gallery_url = False
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
                    url = f"{path}.{end.rpartition(".")[2]}"
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


class RedbustExtractor(Extractor):
    """Extractor for Redbust Images"""
    category = "redbust"
    pattern = BASE_PATTERN + r"/([\w-]*)/([\w-]*)/$"
    directory_fmt = ("{category}", "{gallery}")
    filename_fmt = "{filename}.{extension}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.gallery, self.image_id = match.groups()

    def items(self):
        """Return a list of all (image-url, metadata)-tuples"""
        pagetext = self.request(text.ensure_http_scheme(self.url)).text

        # Look for the largest image in srcset first
        srcset = text.extract(pagetext, 'srcset="', '"')[0]
        if srcset:
            # Extract the largest image from srcset (typically last one)
            srcset_urls = srcset.split(', ')
            img_url = srcset_urls[-1].split(' ')[0] if srcset_urls else None
        
        # Fallback to original extraction method
        if not srcset or not img_url:
            divdata = text.extract(pagetext, '<div class="entry-inner ', 'alt="')
            if not divdata or not divdata[0]:
                divdata = text.extract(pagetext, '<div class=\'entry-inner ', 'alt=\'')
            
            img_url = None
            if divdata and divdata[0]:
                img_url_data = text.extract(divdata[0], 'img src=\"', '\"')
                if not img_url_data or not img_url_data[0]:
                    img_url_data = text.extract(divdata[0], 'img src=\'', '\'')
                
                if img_url_data and img_url_data[0]:
                    img_url = img_url_data[0]
        
        if not img_url:
            return

        data = text.nameext_from_url(img_url, {"url": img_url})
        data["filename"] = self.image_id
        data["gallery"] = self.gallery

        yield Message.Directory, data
        yield Message.Url, img_url, data
