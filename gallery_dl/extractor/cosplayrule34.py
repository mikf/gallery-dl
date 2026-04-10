# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://cosplayrule34.com/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?cosplayrule34\.com(?:/[a-z]{2})?"


class Cosplayrule34Extractor(Extractor):
    """Base class for cosplayrule34 extractors"""
    category = "cosplayrule34"
    root = "https://cosplayrule34.com"
    directory_fmt = ("{category}", "{title}")
    filename_fmt = "{id}_{num}.{extension}"
    archive_fmt = "{id}_{num}"
    request_interval = (0.5, 1.5)

    _find_next = text.re(
        r'class="d-none next"[^>]*href="([^"]+)').search
    _find_post_urls = text.re(
        r"""onclick="location\.href='(/post/\d+)'""").findall
    _find_image_urls = text.re(
        r'href="(https://cosplayrule34\.com/images/a/1280/[^"]+)"').findall
    _find_tags = text.re(
        r'href="/(model|cosplay|fandom)/[^"]+">([^<]+)</a>').findall

    def _set_page_url(self, path):
        if self.url.startswith(("http://", "https://")):
            self.page_url = self.url
        else:
            self.page_url = self.root + path


class Cosplayrule34PostExtractor(Cosplayrule34Extractor):
    """Extractor for individual cosplayrule34 posts"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/post/(\d+)(?:/?\?[^#]+)?/?$"
    example = "https://cosplayrule34.com/post/101851"

    def __init__(self, match):
        Cosplayrule34Extractor.__init__(self, match)
        self.post_id = text.parse_int(match[1])
        self._set_page_url("/post/" + match[1])

    def items(self):
        data, urls = self._extract_post(self.page_url)
        data["count"] = len(urls)

        yield Message.Directory, "", data
        for data["num"], url in enumerate(urls, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def _extract_post(self, url):
        page = self.request(url, notfound=self.subcategory).text
        title = text.unescape(text.extr(page, 'const title = "', '";'))
        if not title:
            title = text.unescape(text.extr(page, '<h1 class="h6">', '<'))
        description = text.unescape(text.extr(
            page, '<meta name="description" content="', '"'))
        suffix = " - " + str(self.post_id)
        if description.endswith(suffix):
            description = description[:-len(suffix)]

        tag_region = text.extr(
            page,
            '<div style="padding-top:10px;padding-bottom:10px">',
            '<div class="container mt-4" id="comments"',
        ) or page

        tags = {"model": [], "cosplay": [], "fandom": []}
        for tag_type, tag_name in util.unique(self._find_tags(tag_region)):
            tags[tag_type].append(text.unescape(tag_name))

        data = {
            "id"         : self.post_id,
            "title"      : title,
            "description": description,
            "model"      : tags["model"][0] if tags["model"] else "",
            "models"     : tags["model"],
            "cosplay"    : tags["cosplay"][0] if tags["cosplay"] else "",
            "cosplays"   : tags["cosplay"],
            "fandom"     : tags["fandom"][0] if tags["fandom"] else "",
            "fandoms"    : tags["fandom"],
            "tags"       : tags["model"] + tags["cosplay"] + tags["fandom"],
            "album_id"   : text.extr(page, 'const albumId = "', '"'),
            "owner_id"   : text.extr(page, 'const ownerId = "', '"'),
            "download"   : text.parse_int(
                text.extr(page, "const download = ", ";"), 1),
            "download_id": text.parse_int(
                text.extr(page, "const downloadId = ", ";")),
            "counter"    : text.parse_int(
                text.extr(page, "let counter = ", ";"), 1),
            "count"      : text.parse_int(
                text.extr(page, "const totalPhotos = ", ";")),
        }

        urls = list(util.unique(self._find_image_urls(page)))
        if data["count"] > len(urls):
            urls.extend(self._load_more_photos(data, len(urls)))
            urls = list(util.unique(urls))
            urls = self._recover_sequence(urls, data["count"])
        elif not data["count"]:
            data["count"] = len(urls)

        return data, urls

    def _load_more_photos(self, data, offset):
        url = self.root + "/cms/load-more-photos.php"
        counter = data["counter"]
        photos_per_load = 10
        remaining = data["count"] - offset
        urls = []

        while remaining > 0:
            response = self.request_json(
                url,
                method="POST",
                json={
                    "album_id"   : data["album_id"],
                    "owner_id"   : data["owner_id"],
                    "download"   : data["download"],
                    "download_id": data["download_id"],
                    "offset"     : offset,
                    "limit"      : min(photos_per_load, remaining),
                    "title"      : data["title"],
                    "counter"    : counter,
                },
                fatal=False,
            )

            photos = response.get("photos") or ()
            if not photos:
                break

            for photo in photos:
                urls.extend(self._find_image_urls(photo["html"]))
                counter = photo.get("counter", counter)

            count = len(photos)
            offset += count
            remaining -= count

        return urls

    def _recover_sequence(self, urls, count):
        if count <= len(urls):
            return urls

        prefix = extension = None
        numbers = {}

        for url in urls:
            base, _, filename = url.rpartition("/")
            stem, dot, ext = filename.partition(".")
            num = text.parse_int(stem, -1)
            if not dot or num < 1:
                return urls

            current_prefix = base + "/"
            current_ext = "." + ext

            if prefix is None:
                prefix = current_prefix
                extension = current_ext
            elif prefix != current_prefix or extension != current_ext:
                return urls

            numbers[num] = url

        recovered = [
            numbers.get(num) or f"{prefix}{num}{extension}"
            for num in range(1, count + 1)
        ]
        return recovered


class Cosplayrule34ListingExtractor(Cosplayrule34Extractor):
    """Base class for cosplayrule34 post listings"""

    def items(self):
        data = {"_extractor": Cosplayrule34PostExtractor}
        for post_url in self.posts():
            yield Message.Queue, post_url, data

    def posts(self):
        url = self.page_url

        while True:
            page = self.request(url, notfound=self.subcategory).text

            for post_url in util.unique(self._find_post_urls(page)):
                yield self.root + post_url

            match = self._find_next(page)
            if not match:
                return
            url = self.root + text.unescape(match.group(1))


class Cosplayrule34ModelExtractor(Cosplayrule34ListingExtractor):
    """Extractor for cosplayrule34 model pages"""
    subcategory = "model"
    pattern = BASE_PATTERN + r"(/model/[^/?#]+(?:/?\?[^#]+)?)$"
    example = "https://cosplayrule34.com/model/Lynie-Nicole"

    def __init__(self, match):
        Cosplayrule34ListingExtractor.__init__(self, match)
        self._set_page_url(match[1])


class Cosplayrule34CosplayExtractor(Cosplayrule34ListingExtractor):
    """Extractor for cosplayrule34 cosplay pages"""
    subcategory = "cosplay"
    pattern = BASE_PATTERN + r"(/cosplay/[^/?#]+(?:/?\?[^#]+)?)$"
    example = "https://cosplayrule34.com/cosplay/Makima"

    def __init__(self, match):
        Cosplayrule34ListingExtractor.__init__(self, match)
        self._set_page_url(match[1])


class Cosplayrule34FandomExtractor(Cosplayrule34ListingExtractor):
    """Extractor for cosplayrule34 fandom pages"""
    subcategory = "fandom"
    pattern = BASE_PATTERN + r"(/fandom/[^/?#]+(?:/?\?[^#]+)?)$"
    example = "https://cosplayrule34.com/fandom/Baldurs-Gate"

    def __init__(self, match):
        Cosplayrule34ListingExtractor.__init__(self, match)
        self._set_page_url(match[1])


class Cosplayrule34CategoryExtractor(Cosplayrule34ListingExtractor):
    """Extractor for cosplayrule34 category pages"""
    subcategory = "category"
    pattern = BASE_PATTERN + r"(/category/[^/?#]+(?:/?\?[^#]+)?)$"
    example = "https://cosplayrule34.com/category/cosplay"

    def __init__(self, match):
        Cosplayrule34ListingExtractor.__init__(self, match)
        self._set_page_url(match[1])


class Cosplayrule34SearchExtractor(Cosplayrule34ListingExtractor):
    """Extractor for cosplayrule34 search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"(/search/[^/?#]+(?:/?\?[^#]+)?)$"
    example = "https://cosplayrule34.com/search/Makima"

    def __init__(self, match):
        Cosplayrule34ListingExtractor.__init__(self, match)
        self._set_page_url(match[1])


class Cosplayrule34TopExtractor(Cosplayrule34ListingExtractor):
    """Extractor for cosplayrule34 top pages"""
    subcategory = "top"
    pattern = BASE_PATTERN + r"(/top(?:/?\?[^#]+)?)$"
    example = "https://cosplayrule34.com/top"

    def __init__(self, match):
        Cosplayrule34ListingExtractor.__init__(self, match)
        self._set_page_url(match[1])


class Cosplayrule34PostsExtractor(Cosplayrule34ListingExtractor):
    """Extractor for cosplayrule34 front-page posts"""
    subcategory = "posts"
    pattern = BASE_PATTERN + r"(/?(?:\?[^#]+)?)$"
    example = "https://cosplayrule34.com/"

    def __init__(self, match):
        Cosplayrule34ListingExtractor.__init__(self, match)
        self._set_page_url(match[1] or "/")
