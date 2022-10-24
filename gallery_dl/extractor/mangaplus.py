# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
# Copyright 2022 Merilynn Bandy
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangaplus.shueisha.co.jp"""

from .common import Extractor, Message
from .. import exception
from ..version import __version__
from uuid import uuid4
import re
from urllib.parse import urljoin, urlparse
from pathlib import Path

try:
    from ..protobuf.mangaplus_pb2 import Response
except ImportError:
    Response = None

BASE_PATTERN = r"(?:https?://)?mangaplus.shueisha.co.jp"
IMAGE_QUALITIES = ['low', 'medium', 'high', 'super_high']


class MangaplusExtractor(Extractor):
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

        if Response is None:
            self.log.error("'protobuf' module required for {} (install with "
                           "'python -m pip install protobuf')"
                           .format(self.api_url))

        self.api = MangaplusAPI(self)
        self.id = match.group(1)

        self.image_quality = self.config("image-quality", "high")

        if self.image_quality not in IMAGE_QUALITIES:
            self.log.warn(
                "unknown image-quality option '{selected}' "
                "(should be one of {options})"
                .format(selected=self.image_quality,
                        options=', '.join(IMAGE_QUALITIES)))

    def _transform_chapter(self, chapter_id, metadata={}):
        message = self.api.manga_viewer(chapter_id, self.image_quality)
        manga_viewer = message.success.mangaViewer

        chapter_metadata = {
            "manga": manga_viewer.titleName,
            "manga_id": manga_viewer.titleId,
            "chapter": int(re.sub(r"\D", "", manga_viewer.chapterName)),
        }
        chapter_metadata.update(metadata)

        yield Message.Directory, chapter_metadata

        for i, page in enumerate(manga_viewer.pages, start=1):
            image_url = page.mangaPage.imageUrl

            path_only = urljoin(image_url, urlparse(image_url).path)
            extension = Path(path_only).suffix[1:]

            page_metadata = {
                "encryption_key": page.mangaPage.encryptionKey,
                "extension": extension,
                "page": i
            }
            page_metadata.update(chapter_metadata)

            self.log.debug("page metadata for <{}>:".format(image_url))
            self.log.debug(page_metadata)

            yield Message.Url, image_url, page_metadata


class MangaplusChapterExtractor(MangaplusExtractor):
    """Extractor for chapters from mangaplus.shueisha.co.jp"""

    subcategory = "chapter"
    pattern = BASE_PATTERN + r"/titles/([0-9]+)"

    def __init__(self, match):
        MangaplusExtractor.__init__(self, match)

    def items(self):
        message = self.api.title_detail(self.id)
        title_detail = message.success.titleDetailView

        chapters = []

        for chapter in title_detail.firstChapterList:
            chapters.append(chapter)

        for chapter in title_detail.lastChapterList:
            chapters.append(chapter)

        for chapter in chapters:
            metadata = {
                "chapter_minor": chapter.subTitle,
                "author": title_detail.title.author,
                "manga": title_detail.title.name,
                "manga_id": title_detail.title.titleId,
            }

            yield from self._transform_chapter(chapter.chapterId, metadata)


class MangaplusMangaExtractor(MangaplusExtractor):
    """Extractor for manga from mangaplus.shueisha.co.jp"""

    subcategory = "manga"
    pattern = BASE_PATTERN + r"/viewer/([0-9]+)"

    def __init__(self, match):
        MangaplusExtractor.__init__(self, match)

    def items(self):
        yield from self._transform_chapter(self.id)


class MangaplusAPI():
    def __init__(self, extr):
        self.extractor = extr
        self.root = "https://jumpg-webapi.tokyo-cdn.com/api"

        self.headers = {
            "User-Agent": "gallery-dl/" + __version__,
            "Session-Token": uuid4().urn
        }

    def manga_viewer(self, chapter_id, img_quality):
        return self._call(
            "/manga_viewer?chapter_id={}&split=yes&img_quality={}"
            .format(chapter_id, img_quality))

    def title_detail(self, title_id):
        return self._call("/title_detail?title_id={}".format(title_id))

    def _call(self, endpoint, params=None):
        url = self.root + endpoint

        while True:
            response = self.extractor.request(
                url, params=params, headers=self.headers, fatal=None)

            if response.status_code < 400:
                msg = Response()
                msg.ParseFromString(response.content)

                self.extractor.log.debug("parsed payload from {}".format(url))
                self.extractor.log.debug(msg)

                if not msg.HasField("success"):
                    self.extractor.log.debug(response.content)
                    raise exception.StopExtraction(
                        "No valid data returned from {}".format(url))

                return msg

            self.extractor.log.debug(response.text)

            raise exception.StopExtraction(
                "{}: bad response from {}".format(response.status_code, url))
