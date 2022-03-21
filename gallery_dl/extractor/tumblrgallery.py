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

    @staticmethod
    def _urls_from_page(page):
        return text.extract_iter(
            page, '<div class="report"> <a class="xx-co-me" href="', '"')

    @staticmethod
    def _data_from_url(url):
        filename = text.nameext_from_url(url)["filename"]
        parts = filename.split("_")
        try:
            return {"id": parts[1] if parts[1] != "inline" else parts[2]}
        except IndexError:
            return {"id": filename}


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
            url = "{}/tumblrblog/gallery/{}/{}.html".format(
                self.root, self.gallery_id, page_num)
            response = self.request(url, allow_redirects=False, fatal=False)

            if response.status_code >= 300:
                return

            for url in self._urls_from_page(response.text):
                yield url, self._data_from_url(url)
            page_num += 1


class TumblrgalleryPostExtractor(TumblrgalleryExtractor):
    """Extractor for Posts on tumblrgallery.xyz"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"(/post/(\d+)\.html)"
    test = ("https://tumblrgallery.xyz/post/405674.html", {
        "pattern": r"https://78\.media\.tumblr\.com/bec67072219c1f3bc04fd9711d"
                   r"ec42ef/tumblr_p51qq1XCHS1txhgk3o1_1280\.jpg",
        "count": 3,
    })

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
        for url in self._urls_from_page(page):
            yield url, self._data_from_url(url)


class TumblrgallerySearchExtractor(TumblrgalleryExtractor):
    """Extractor for Search result on tumblrgallery.xyz"""
    subcategory = "search"
    filename_fmt = "{category}_{num:>03}_{gallery_id}_{id}_{title}.{extension}"
    directory_fmt = ("{category}", "{search_term}")
    pattern = BASE_PATTERN + r"(/s\.php\?q=([^&#]+))"
    test = ("https://tumblrgallery.xyz/s.php?q=everyday-life", {
        "pattern": r"https://\d+\.media\.tumblr\.com/.+",
        "count": "< 1000",
    })

    def __init__(self, match):
        TumblrgalleryExtractor.__init__(self, match)
        self.search_term = match.group(2)

    def metadata(self, page):
        return {
            "search_term": self.search_term,
        }

    def images(self, _):
        page_url = "s.php?q=" + self.search_term
        while True:
            page = self.request(self.root + "/" + page_url).text

            for gallery_id in text.extract_iter(
                    page, '<div class="title"><a href="post/', '.html'):

                url = "{}/post/{}.html".format(self.root, gallery_id)
                post_page = self.request(url).text

                for url in self._urls_from_page(post_page):
                    data = self._data_from_url(url)
                    data["gallery_id"] = gallery_id
                    data["title"] = text.remove_html(text.unescape(
                        text.extract(post_page, "<title>", "</title>")[0]
                    )).replace("_", "-")
                    yield url, data

            next_url = text.extract(
                page, '</span> <a class="btn btn-primary" href="', '"')[0]
            if not next_url or page_url == next_url:
                return
            page_url = next_url
