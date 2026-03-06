# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://filester.me/"""

from .common import Extractor, Message
from .. import text
import random

BASE_PATTERN = r"(?:https?://)?(?:www\.)?filester\.me"


class FilesterExtractor(Extractor):
    """Base class for filester extractors"""
    category = "filester"
    archive_fmt = "{id}"
    root = "https://filester.me"

    def _download_url(self, slug):
        url = self.root + "/api/public/download"
        data = self.request_json(url, method="POST", json={"file_slug": slug})
        return (f"https://cache{random.choice((1, 6))}.filester.me"
                f"{data['download_url']}?download=true")


class FilesterFileExtractor(FilesterExtractor):
    subcategory = "file"
    filename_fmt = "{id} {filename}.{extension}"
    pattern = BASE_PATTERN + r"/d/([^/?#]+)"
    example = "https://filester.me/d/ID"

    def items(self):
        file_slug = self.groups[0]

        url = f"{self.root}/d/{file_slug}"
        page = self.request(url).text
        extr = text.extract_from(page)

        name = text.unquote(text.unescape(extr(
            'property="og:title" content="', '"')))
        file = text.nameext_from_name(name, {
            "id"  : file_slug,
            "uuid": extr('>UUID</span', '</span').rpartition(">")[2],
            "mime": extr('>Type</span', '</span').rpartition(">")[2],
            "date": self.parse_datetime_iso(extr(
                '>Uploaded</span', '</span').rpartition(">")[2]),
            "size": extr('>Size</span', '</span').rpartition(">")[2],
            "hash": extr('>SHA-256</span', '</span').rpartition(">")[2],
        })

        yield Message.Directory, "", file
        yield Message.Url, self._download_url(file_slug), file


class FilesterFolderExtractor(FilesterExtractor):
    subcategory = "folder"
    directory_fmt = ("{category}", "{folder_name} ({folder_id})")
    filename_fmt = "{num:>03} {id} {filename}.{extension}"
    pattern = BASE_PATTERN + r"/f/([^/?#]+)"
    example = "https://filester.me/f/ID"

    def items(self):
        folder_slug = self.groups[0]
        num = None

        url = f"{self.root}/f/{folder_slug}"
        params = {"page": 1}
        while True:
            page = self.request(url, params=params).text

            if num is None:
                extr = text.extract_from(page)
                kw = self.kwdict
                kw["folder_id"] = folder_slug
                kw["folder_name"] = text.unescape(extr(
                    'property="og:title" content="', '"'))
                kw["folder_uuid"] = extr('/t/', '"')
                kw["folder_date"] = self.parse_datetime(extr(
                    "<span>Created ", "<"), "%b %d, %Y")
                kw["count"] = num = text.parse_int(extr("<span>", " "))
                kw["folder_size"] = text.parse_bytes(extr("<span>", "B<"))
                del extr
                yield Message.Directory, "", {}

            for html in text.extract_iter(
                    page, 'class="file-item"', "</button>"):
                extr = text.extract_from(html)
                name = text.unescape(extr('data-name="', '"'))
                file = text.nameext_from_name(name, {
                    "size": extr('data-size="', '"'),
                    "date": self.parse_datetime_iso(extr('data-date="', '"')),
                    "id"  : extr("href='/d/", "'"),
                    "uuid": extr('src="/t/', '"'),
                    "num" : num,
                })
                num -= 1
                yield Message.Url, self._download_url(file["id"]), file

            if ">→</a>" not in page:
                break
            params["page"] += 1
