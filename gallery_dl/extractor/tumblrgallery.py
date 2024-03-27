# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://tumblrgallery.xyz/"""

from .common import GalleryExtractor
from .. import text

import os
import sys
import time
import math
import random
import datetime
from pathlib import Path

BASE_PATTERN = r"(?:https?://)?tumblrgallery\.xyz"


# --- 80 cols ---------------------------------------------------------------- #


def sleeping_time() -> bool:
    current_time = datetime.datetime.now().time()
    start_time = datetime.datetime.strptime("23:00", "%H:%M").time()
    end_time = datetime.datetime.strptime("08:00", "%H:%M").time()
    # Check if the current time is between 11:00 PM and 8:00 AM
    is_between = start_time <= current_time or current_time <= end_time
    return is_between


def go_to_bed() -> None:
    if sleeping_time():
        print(
            "Program is going to bed for today."
        )
        while sleeping_time():
            time.sleep(60)
    return


def wait_inbetween_calls() -> None:
    wait_time = max(0, random.gauss(mu = 120, sigma = 30))
    print(
        "Waiting for extra time inbetween retriving tweets."
        + f" ({wait_time:.3f}s)"
    )
    time.sleep(wait_time)
    go_to_bed()
    return


def wait_inbetween_downloads():
    wait_time = max(0, random.gauss(mu = 120, sigma = 30))
    print(
        "Waiting for extra time inbetween downloading media."
        + f" ({wait_time:.3f}s)"
    )
    time.sleep(wait_time)
    go_to_bed()
    return


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
    example = "https://tumblrgallery.xyz/tumblrblog/gallery/12345.html"

    def __init__(self, match):
        TumblrgalleryExtractor.__init__(self, match)
        self.gallery_id = text.parse_int(match.group(2))

    def metadata(self, page):
        return {
            "title" : text.unescape(text.extr(page, "<h1>", "</h1>")),
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
    example = "https://tumblrgallery.xyz/post/12345.html"

    def __init__(self, match):
        TumblrgalleryExtractor.__init__(self, match)
        self.gallery_id = text.parse_int(match.group(2))

    def metadata(self, page):
        return {
            "title" : text.remove_html(
                text.unescape(text.extr(page, "<title>", "</title>"))
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
    example = "https://tumblrgallery.xyz/s.php?q=QUERY"

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
                        text.extr(post_page, "<title>", "</title>")
                    )).replace("_", "-")
                    yield url, data

            next_url = text.extr(
                page, '</span> <a class="btn btn-primary" href="', '"')
            if not next_url or page_url == next_url:
                return
            page_url = next_url
