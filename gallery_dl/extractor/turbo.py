# -*- coding: utf-8 -*-

# Copyright 2024-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://turbo.cr/"""

from .lolisafe import LolisafeAlbumExtractor
from .. import text

BASE_PATTERN = (r"(?:https?://)?(?:"
                r"(?:www\.)?turbo(?:vid)?\.cr|"
                r"saint\d*\.(?:su|pk|cr|to))")


class TurboAlbumExtractor(LolisafeAlbumExtractor):
    """Extractor for turbo.cr albums"""
    category = "turbo"
    root = "https://turbo.cr"
    pattern = BASE_PATTERN + r"/a/([^/?#]+)"
    example = "https://turbo.cr/a/ID"

    def fetch_album(self, album_id):
        url = f"{self.root}/a/{album_id}"
        extr = text.extract_from(self.request(url).text)
        title = extr("<h1 ", "<")
        descr = extr("<p ", "<")
        tbody = extr('id="fileTbody"', '</tbody>')
        headers = {"Referer": url}

        return self._extract_files(tbody, headers), {
            "album_id"     : album_id,
            "album_name"   : text.unescape(title[title.find(">")+1:]),
            "description"  : text.unescape(descr[descr.find(">")+1:]),
            "album_size"   : sum(map(text.parse_int, text.extract_iter(
                tbody, 'data-size="', '"'))),
            "count"        : tbody.count("data-id="),
            "_http_headers": headers,
        }

    def _extract_files(self, body, headers):
        for file in text.extract_iter(body, "<tr", "</tr>"):
            data_id = text.extr(file, 'data-id="', '"')
            url = f"{self.root}/api/sign?v={data_id}"
            data = self.request_json(url, headers=headers)
            name = data.get("original_filename") or data.get("filename")
            yield text.nameext_from_name(name, {
                "id"  : data_id,
                "file": data.get("url"),
                "size": text.parse_int(text.extr(file, 'data-size="', '"')),
                "_http_headers": headers,
            })


class TurboMediaExtractor(TurboAlbumExtractor):
    """Extractor for turbo.cr media links"""
    subcategory = "media"
    directory_fmt = ("{category}",)
    pattern = BASE_PATTERN + r"/(?:embe)?[dv]/([^/?#]+)"
    example = "https://turbo.cr/embed/ID"

    def fetch_album(self, album_id):
        try:
            return (self._extract_file(album_id),), {
                "album_id"   : "",
                "album_name" : "",
                "album_size" : -1,
                "description": "",
                "count"      : 1,
            }
        except Exception as exc:
            self.log.error("%s: %s", exc.__class__.__name__, exc)
            return (), {}

    def _extract_file(self, data_id):
        url = f"{self.root}/d/{data_id}"
        headers = {"Referer": url}
        page = self.request(url).text
        size = text.extr(page, 'id="fileSizeBytes">', '<')
        date = text.extract(page, "<span>", "<", page.find("File ID:"))[0]

        url = f"{self.root}/api/sign?v={data_id}"
        data = self.request_json(url, headers=headers)
        name = data.get("original_filename") or data.get("filename")
        return text.nameext_from_name(name, {
            "id"  : data_id,
            "file": data.get("url"),
            "size": int(text.parse_float(size.replace("&#43;", "+"))),
            "date": self.parse_datetime_iso(date),
            "_http_headers": headers,
        })
