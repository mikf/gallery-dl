# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
# Copyright 2022 Merilynn Bandy
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangaplus.shueisha.co.jp"""

from .common import Extractor, Message
from .. import text, util, exception
from ..version import __version__
from uuid import uuid4
from blackboxprotobuf import decode_message
import re
from urllib.parse import urljoin, urlparse
from pathlib import Path

BASE_PATTERN = r"(?:https?://)?mangaplus.shueisha.co.jp"


class MangaPlusExtractor(Extractor):
    """Base class for mangaplus extractors"""
    category = "mangaplus"
    directory_fmt = (
        "{category}",
        "{manga}",
        "{chapter:>03}{title:?: //}")
    filename_fmt = (
        "{manga}_c{chapter:>03}_{page:>03}.{extension}")
    archive_fmt = "{chapter}_{page}"

    api_url = "https://mangaplus.shueisha.co.jp"

    def __init__(self, match):
        Extractor.__init__(self, match)

        self.api = MangaPlusAPI(self)
        self.id = match.group(1)

        # add setting for image_quality


class MangaPlusMangaExtractor(MangaPlusExtractor):
    """Extractor for manga from mangaplus.shueisha.co.jp"""
    subcategory = "manga"
    pattern = BASE_PATTERN + r"/viewer/([0-9]+)"

    def __init__(self, match):
        MangaPlusExtractor.__init__(self, match)

    def items(self):
        pages, chapter_metadata = self.api.manga_viewer(self.id)

        chapter_metadata = {
            "manga": chapter_metadata['title_name'],
            "chapter": int(re.sub(r"\D", "", chapter_metadata['chapter_name'])),
        }

        yield Message.Directory, chapter_metadata

        for i, page in enumerate(pages, start=1):
            url = page['url']
            path_only = urljoin(url, urlparse(url).path)
            extension = Path(path_only).suffix[1:]

            page_metadata = {
                **chapter_metadata,
                "encryption_key": page['encryption_key'],
                "extension": extension,
                "page": i
            }

            yield Message.Url, page['url'], page_metadata


class MangaPlusAPI():
    def __init__(self, extr):
        self.extractor = extr
        self.root = "https://jumpg-webapi.tokyo-cdn.com/api"

        self.headers = {
            "User-Agent": "gallery-dl/" + __version__,
            "Session-Token": uuid4().urn
        }

    def manga_viewer(self, chapter_id, split="yes", img_quality="high"):

        message = self._call(
            f"/manga_viewer?chapter_id={chapter_id}&split={split}&img_quality={img_quality}")

        # A lot of magic numbers coming up below. These are paths in the
        # protobuf message. We're taking a shortcut here since adding protobuf
        # definitions and a compiler is a bit overkill for this lib.
        #
        # Data primarily sourced from:
        # https://github.com/parasquid/manga_plus-api/blob/c7066684f9bb3f354a55cc7094a420134060d897/lib/manga_plus/proto/manga_plus.proto

        root = message['1']['10']

        metadata = {
            "title_id": root['9'],
            "chapter_id": chapter_id,
            "title_name": root['5'].decode('utf-8'),
            "chapter_name": root['6'].decode('utf-8')
        }

        pages = []

        for page in root['1']:
            if '1' in page:
                pages.append({
                    "url": page['1']['1'].decode('utf-8'),
                    "width": page['1']['2'],
                    "height": page['1']['3'],
                    "encryption_key": page['1']['5'].decode('utf-8')
                })

        return pages, metadata

    def _call(self, endpoint, params=None):
        url = self.root + endpoint

        while True:
            response = self.extractor.request(
                url, params=params, headers=self.headers, fatal=None)

            if response.status_code < 400:

                message, typedef = decode_message(response.content)

                return message

            raise exception.StopExtraction(
                f"{response.status_code}: bad response from {url}")
