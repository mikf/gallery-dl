# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://tumblrgallery.xyz/"""

from .common import GalleryExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?tumblrgallery\.xyz"


class TumblrgalleryExtractor(GalleryExtractor):
    """Base class for tumblrgallery extractors"""
    category = "tumblrgallery"
    filename_fmt = "{category}_{gallery_id}_{num:>03}_{id}.{extension}"
    directory_fmt = ("{category}", "{gallery_id} {title}")
    root = "https://tumblrgallery.xyz"


class TumblrgalleryTumblrblogExtractor(TumblrgalleryExtractor):
    """Extractor for Tumblrblog on tumblrgallery.xyz"""
    subcategory = "tumblrblog"
    pattern = BASE_PATTERN + r"(/tumblrblog/gallery/(\d+)\.html)"
    test = ("https://tumblrgallery.xyz/tumblrblog/gallery/103975.html",)

    def __init__(self, match):
        TumblrgalleryExtractor.__init__(self, match)
        self.gallery_id = text.parse_int(match.group(2))

    def metadata(self, page):
        return {
            "title" : text.unescape(text.extract(page, "<h1>", "</h1>"))[0],
            "gallery_id": self.gallery_id,
        }

    def images(self, _):
        page_num = 1
        while True:
            response = self.request(
                "{}/tumblrblog/gallery/{}/{}.html"
                .format(self.root, self.gallery_id, page_num),
                allow_redirects=False
            )
            if response.status_code != 200:
                return

            page = response.text
            page_num += 1

            urls = list(text.extract_iter(
                page,
                '<div class="report xx-co-me"> <a href="',
                '" data-fancybox="gallery"'
            ))

            for image_src in urls:
                yield image_src, {
                    "id": text.extract(image_src, "tumblr_", "_")[0]
                }


class TumblrgalleryPostExtractor(TumblrgalleryExtractor):
    """Extractor for Posts on tumblrgallery.xyz"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"(/post/(\d+)\.html)"
    test = ("https://tumblrgallery.xyz/post/405674.html",)

    def __init__(self, match):
        TumblrgalleryExtractor.__init__(self, match)
        self.gallery_id = text.parse_int(match.group(2))

    def metadata(self, page):
        return {
            "title" : text.remove_html(
                text.unescape(text.extract(page, "<title>", "</title>")[0])
            ).replace("_", "-"),
            "gallery_id": self.gallery_id,
        }

    def images(self, page):
        urls = list(text.extract_iter(
            page,
            '<div class="report xx-co-me"> <a href="',
            '" data-fancybox="gallery"'
        ))

        for image_src in urls:
            yield image_src, {
                "id": text.extract(image_src, "tumblr_", "_")[0] or
                text.nameext_from_url(image_src)["filename"]
            }


class TumblrgallerySearchExtractor(TumblrgalleryExtractor):
    """Extractor for Search result on tumblrgallery.xyz"""
    subcategory = "search"
    filename_fmt = "{category}_{num:>03}_{gallery_id}_{id}_{title}.{extension}"
    directory_fmt = ("{category}", "{search_term}")
    pattern = BASE_PATTERN + r"(/s\.php\?q=([^&#]+))"
    test = ("https://tumblrgallery.xyz/s.php?q=everyday-life",)

    def __init__(self, match):
        TumblrgalleryExtractor.__init__(self, match)
        self.search_term = match.group(2)

    def metadata(self, page):
        return {
            "search_term": self.search_term,
        }

    def images(self, _):
        page_num = 1
        while True:
            response = self.request(
                "{}/s.php?q={}&page={}"
                .format(self.root, self.search_term, page_num),
                allow_redirects=False
            )
            if response.status_code != 200:
                return

            page = response.text
            page_num += 1

            gallery_ids = list(text.extract_iter(
                page,
                '<div class="title"><a href="post/',
                '.html'
            ))

            for gallery_id in gallery_ids:
                post_page = self.request(
                    "{}/post/{}.html"
                    .format(self.root, gallery_id),
                    allow_redirects=False
                ).text
                for image_src in TumblrgalleryPostExtractor.images(
                    self, post_page
                ):
                    image_src[1]["title"] = text.remove_html(
                        text.unescape(
                            text.extract(post_page, "<title>", "</title>")[0]
                        )
                    ).replace("_", "-")
                    image_src[1]["gallery_id"] = gallery_id
                    yield image_src
