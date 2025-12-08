# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fitnakedgirls.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?fitnakedgirls\.com"


class FitnakedgirlsExtractor(Extractor):
    """Base class for fitnakedgirls extractors"""
    category = "fitnakedgirls"
    root = "https://fitnakedgirls.com"


class FitnakedgirlsGalleryExtractor(GalleryExtractor, FitnakedgirlsExtractor):
    """Extractor for fitnakedgirls galleries"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{title}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{gallery_id}_{filename}"
    pattern = rf"{BASE_PATTERN}/photos/gallery/([\w-]+)/?$"
    example = "https://fitnakedgirls.com/photos/gallery/MODEL-nude/"

    def __init__(self, match):
        self.gallery_slug = match.group(1)
        url = f"{self.root}/photos/gallery/{self.gallery_slug}/"
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)

        title = text.unescape(extr("<title>", "<"))
        if " - " in title:
            title = title.rpartition(" - ")[0]
        title = title.strip()

        # Strip common patterns to get cleaner model name
        model = title
        for pattern in (" Nudes", " Nude", " nudes", " nude"):
            if pattern in model:
                model = model.partition(pattern)[0]
                break

        return {
            "gallery_id": text.parse_int(extr('data-post-id="', '"')),
            "gallery_slug": self.gallery_slug,
            "model": model,
            "title": model,
            "date": self.parse_datetime_iso(
                extr('article:published_time" content="', '"')),
        }

    def images(self, page):
        results = []

        # Extract content from articleBody only (avoid sidebar thumbnails)
        content = text.extr(
            page, 'itemprop="articleBody"', '<!-- .entry-content -->')
        if not content:
            content = page

        # Extract videos from wp-block-video figures
        for figure in text.extract_iter(
                content, '<figure class="wp-block-video">', '</figure>'):
            if src := text.extr(figure, 'src="', '"'):
                if "/wp-content/uploads/" in src:
                    results.append((src, None))

        # Extract images from wp-block-image figures (newer template)
        for figure in text.extract_iter(
                content, '<figure class="wp-block-image', '</figure>'):
            if src := text.extr(figure, 'data-src="', '"'):
                if "/wp-content/uploads/" in src:
                    results.append((src, None))

        # Fallback: Extract images with size-large class (older template)
        if not results:
            for img in text.extract_iter(content, "<img ", ">"):
                if "size-large" in img:
                    if src := text.extr(img, 'data-src="', '"'):
                        if "/wp-content/uploads/" in src:
                            results.append((src, None))

        return results


class FitnakedgirlsCategoryExtractor(FitnakedgirlsExtractor):
    """Extractor for fitnakedgirls category pages"""
    subcategory = "category"
    pattern = rf"{BASE_PATTERN}/photos/gallery/category/([\w-]+)"
    example = "https://fitnakedgirls.com/photos/gallery/category/CATEGORY/"

    def items(self):
        data = {"_extractor": FitnakedgirlsGalleryExtractor}
        base = f"{self.root}/photos/gallery/category/{self.groups[0]}/"
        for url in self._pagination(base):
            yield Message.Queue, url, data

    def _pagination(self, base):
        url = base
        pnum = 1

        while True:
            page = self.request(url).text

            for post in text.extract_iter(
                    page, 'class="entry-title', "</a>"):
                yield text.extr(post, 'href="', '"')

            pnum += 1
            url = f"{base}page/{pnum}/"
            if f'href="{url}"' not in page:
                return


class FitnakedgirlsTagExtractor(FitnakedgirlsExtractor):
    """Extractor for fitnakedgirls tag pages"""
    subcategory = "tag"
    pattern = rf"{BASE_PATTERN}/photos/tag/([\w-]+)"
    example = "https://fitnakedgirls.com/photos/tag/blonde/"

    def items(self):
        data = {"_extractor": FitnakedgirlsGalleryExtractor}
        base = f"{self.root}/photos/tag/{self.groups[0]}/"
        for url in self._pagination(base):
            yield Message.Queue, url, data

    def _pagination(self, base):
        url = base
        pnum = 1

        while True:
            page = self.request(url).text

            for post in text.extract_iter(
                    page, 'class="entry-title', "</a>"):
                yield text.extr(post, 'href="', '"')

            pnum += 1
            url = f"{base}page/{pnum}/"
            if f'href="{url}"' not in page:
                return


class FitnakedgirlsVideoExtractor(FitnakedgirlsExtractor):
    """Extractor for fitnakedgirls video posts"""
    subcategory = "video"
    directory_fmt = ("{category}", "{title}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{video_id}_{filename}"
    pattern = rf"{BASE_PATTERN}/videos/(\d+)/(\d+)/([\w-]+)"
    example = "https://fitnakedgirls.com/videos/2025/08/VIDEO-TITLE/"

    def items(self):
        year, month, slug = self.groups
        url = f"{self.root}/videos/{year}/{month}/{slug}/"
        page = self.request(url).text

        extr = text.extract_from(page)

        title = text.unescape(extr("<title>", "<"))
        if " | " in title:
            title = title.rpartition(" | ")[0]
        title = title.strip()

        data = {
            "video_id": text.parse_int(extr('data-post-id="', '"')),
            "slug": slug,
            "title": title,
            "date": self.parse_datetime_iso(
                extr('article:published_time" content="', '"')),
        }

        # Extract video from articleBody
        content = text.extr(
            page, 'itemprop="articleBody"', '<!-- .entry-content -->')
        if not content:
            content = page

        yield Message.Directory, "", data

        # Extract video URL
        for video in text.extract_iter(content, "<video ", "</video>"):
            if src := text.extr(video, 'src="', '"'):
                if "/wp-content/uploads/" in src:
                    yield Message.Url, src, text.nameext_from_url(src, data)


class FitnakedgirlsBlogExtractor(FitnakedgirlsExtractor):
    """Extractor for fitnakedgirls blog posts"""
    subcategory = "blog"
    directory_fmt = ("{category}", "{title}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{post_id}_{filename}"
    pattern = rf"{BASE_PATTERN}/fitblog/([\w-]+)"
    example = "https://fitnakedgirls.com/fitblog/MODEL-NAME/"

    def items(self):
        slug = self.groups[0]
        url = f"{self.root}/fitblog/{slug}/"
        page = self.request(url).text

        extr = text.extract_from(page)

        title = text.unescape(extr("<title>", "<"))
        if " - " in title:
            title = title.rpartition(" - ")[0]
        title = title.strip()

        data = {
            "post_id": text.parse_int(extr('data-post-id="', '"')),
            "slug": slug,
            "title": title,
            "date": self.parse_datetime_iso(
                extr('article:published_time" content="', '"')),
        }

        # Extract content from articleBody
        content = text.extr(
            page, 'itemprop="articleBody"', '<!-- .entry-content -->')
        if not content:
            content = page

        yield Message.Directory, "", data

        # Extract images from wp-block-image figures
        for figure in text.extract_iter(
                content, '<figure class="wp-block-image', '</figure>'):
            # Try srcset first for highest resolution
            if srcset := text.extr(figure, 'srcset="', '"'):
                # Get the last (largest) image from srcset
                urls = srcset.split(", ")
                if urls:
                    src = urls[-1].partition(" ")[0]
                    if "/wp-content/uploads/" in src:
                        yield Message.Url, src, text.nameext_from_url(
                            src, data)
                        continue
            # Fallback to src
            if src := text.extr(figure, 'src="', '"'):
                if "/wp-content/uploads/" in src:
                    yield Message.Url, src, text.nameext_from_url(src, data)
