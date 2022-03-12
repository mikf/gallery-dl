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
import re
from urllib.parse import urljoin, urlparse
from pathlib import Path
from .mangaplus_pb2 import Response

BASE_PATTERN = r"(?:https?://)?mangaplus.shueisha.co.jp"
IMAGE_QUALITIES = ['low', 'medium', 'high', 'super_high']


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

        self.image_quality = self.config("image-quality", "high")

        if self.image_quality not in IMAGE_QUALITIES:
            self.log.warn(
                f"unknown image-quality option '{self.image_quality} "
                f"(should be one of {', '.join(IMAGE_QUALITIES)})")

    def _transform_chapter(self, chapter_id: int, metadata: dict = None):
        message = self.api.manga_viewer(chapter_id, self.image_quality)
        manga_viewer = message.success.mangaViewer

        chapter_metadata = {
            "manga": manga_viewer.titleName,
            "manga_id": manga_viewer.titleId,
            "chapter": int(re.sub(r"\D", "", manga_viewer.chapterName)),
            **(metadata or {}),
        }

        yield Message.Directory, chapter_metadata

        for i, page in enumerate(manga_viewer.pages, start=1):
            image_url = page.mangaPage.imageUrl

            path_only = urljoin(image_url, urlparse(image_url).path)
            extension = Path(path_only).suffix[1:]

            page_metadata = {
                **chapter_metadata,
                "encryption_key": page.mangaPage.encryptionKey,
                "extension": extension,
                "page": i
            }

            self.log.debug(f"page metadata for <{image_url}>:")
            self.log.debug(page_metadata)

            yield Message.Url, image_url, page_metadata

    @staticmethod
    def _transform_title_meta(message):
        title_detail = message.success.titleDetailView

        return {
            "author": title_detail.title.author,
            "manga": title_detail.title.name,
            "manga_id": title_detail.title.titleId,
        }


class MangaPlusChapterExtractor(MangaPlusExtractor):
    """Extractor for chapters from mangaplus.shueisha.co.jp"""

    subcategory = "chapter"
    pattern = BASE_PATTERN + r"/titles/([0-9]+)"

    def __init__(self, match):
        MangaPlusExtractor.__init__(self, match)

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
                **self._transform_title_meta(message),
                "chapter_minor": chapter.subTitle
            }

            yield from self._transform_chapter(chapter.chapterId, metadata)


class MangaPlusMangaExtractor(MangaPlusExtractor):
    """Extractor for manga from mangaplus.shueisha.co.jp"""

    subcategory = "manga"
    pattern = BASE_PATTERN + r"/viewer/([0-9]+)"

    def __init__(self, match):
        MangaPlusExtractor.__init__(self, match)

    def items(self):
        yield from self._transform_chapter(self.id)


class MangaPlusAPI():
    def __init__(self, extr):
        self.extractor = extr
        self.root = "https://jumpg-webapi.tokyo-cdn.com/api"

        self.headers = {
            "User-Agent": "gallery-dl/" + __version__,
            "Session-Token": uuid4().urn
        }

    def manga_viewer(self, chapter_id: int, img_quality: str):
        return self._call(
            f"/manga_viewer?chapter_id={chapter_id}&split=yes&img_quality={img_quality}")

    def title_detail(self, title_id):
        return self._call(f"/title_detail?title_id={title_id}")

    def _call(self, endpoint, params=None):
        url = self.root + endpoint

        while True:
            response = self.extractor.request(
                url, params=params, headers=self.headers, fatal=None)

            if response.status_code < 400:
                msg = Response()
                msg.ParseFromString(response.content)

                self.extractor.log.debug(f"parsed payload from {url}")
                self.extractor.log.debug(msg)

                if not msg.HasField("success"):
                    self.extractor.log.debug(response.content)
                    raise exception.StopExtraction(
                        f"No valid data returned from {url}")

                return msg

            self.extractor.log.debug(response.text)

            raise exception.StopExtraction(
                f"{response.status_code}: bad response from {url}")
