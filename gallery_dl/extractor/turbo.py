# -*- coding: utf-8 -*-

# Copyright 2024-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors forhttps://turbovid.cr/"""

from gallery_dl.exception import HttpError
from gallery_dl.extractor.message import Message
from .common import Extractor

from .. import text

BASE_PATTERN = r"(?:https?://)?(?:turbo(?:vid)?\.cr)"


class TurboAlbumExtractor(Extractor):
    """Extractor for turbo.cr album files"""
    category = "turbo"
    subcategory = "album"
    directory_fmt = ("{category}",)

    pattern = r"https?://(?:www\.)?turbo(?:vid)?\.cr(/a/([^/?#]+))"
    example = "https://turbo.cr/a/ID"

    def items(self):
        path, album_id = self.groups

        try:
            response = self.request(
                self.url,
            )

            tbody, _ = text.extract(
                response.text,
                '<tbody id="fileTbody"',
                '</tbody>'
            )

            if not tbody:
                raise Exception("Could not extract files from site")

            ids = list(text.extract_iter(tbody, 'data-id="', '"'))

            if not ids:
                raise Exception("Could not extract files from site")

            main, _ = text.extract(
                response.text,
                '<main',
                '</main>'
            )

            h1, _ = text.extract(main, '<h1 class=', '/h1>')
            album_title, _ = text.extract(h1, '>', "<")

            description, _ = text.extract(
                main,
                '<p class="mt-1 text-sm text-white/60">',
                '</p>'
            )

        except Exception as ex:
            self.log.error("%s: %s", ex.__class__.__name__, ex)
            return (), {}

        files = []
        api_url = "https://turbo.cr/api/sign?v={}"

        for v_id in ids:
            # Obtain file metadata
            try:
                response = self.request(
                    f"https://turbo.cr/d/{v_id}"
                )
            except HttpError as ex:
                self.log.error("%s: %s", ex.__class__.__name__, ex)
                return (), {}

            size, _ = text.extract(
                response.text,
                '<span id="fileSizeBytes">',
                '</span>'
            )

            # Fix cientific notation
            size = int(float(size.replace("&#43;", "+")))

            # Obtain signed direct url
            try:
                response = self.request(
                    api_url.format(v_id),
                ).json()
            except HttpError as ex:
                self.log.error("%s: %s", ex.__class__.__name__, ex)
                return (), {}

            video_url = response.get("url")

            filename = response.get("filename").split(".")[0]
            extension = response.get("filename").split(".")[1]

            files.append(
                {
                    "id"       : v_id,
                    "album_id"       : album_id,
                    "url"       : video_url,
                    "filename" : filename,
                    "extension": extension,
                    "size": int(size),
                    "category" : self.category,
                }
            )

        album_data = {
            "album_id": album_id,
            "album_name": album_title,
            "album_size": sum(file["size"] for file in files),
            "description"  : text.unescape(description),
            "count"        : len(files),
            "_http_headers": {"Referer": "https://turbo.cr/" + path}
        }

        yield Message.Directory, "", album_data

        for data in files:
            full_data = album_data.copy()
            full_data.update(data)
            yield Message.Url, data["url"], full_data


class TurboMediaExtractor(Extractor):
    """Extractor for turbo.cr single files"""
    category = "turbo"
    subcategory = "media"
    directory_fmt = ("{category}",)

    pattern = r"https?://(?:www\.)?turbo(?:vid)?\.cr(/(embe)?(v)?d/([^/?#]+))"
    example = "https://turbo.cr/embed/ID"

    def items(self):
        path, _, _, video_id = self.groups
        api_url = "https://turbo.cr/api/sign?v={}".format(video_id)

        # Obtain file metadata
        try:
            response = self.request(
                f"https://turbo.cr/d/{video_id}"
            )
        except HttpError as ex:
            self.log.error("%s: %s", ex.__class__.__name__, ex)
            return (), {}

        size, _ = text.extract(
            response.text,
            '<span id="fileSizeBytes">',
            '</span>'
        )

        # Fix cientific notation
        size = int(float(size.replace("&#43;", "+")))

        try:
            response = self.request(
                api_url,
            ).json()
        except HttpError as ex:
            self.log.error("%s: %s", ex.__class__.__name__, ex)
            return (), {}

        video_url = response.get("url")

        filename = response.get("filename").split(".")[0]
        extension = response.get("filename").split(".")[1]

        if video_url:
            data = {
                "id"       : video_id,
                "url"       : video_url,
                "filename" : filename,
                "extension": extension,
                "size": int(size),
                "category" : self.category,
                "_http_headers": {"Referer": "https://turbo.cr/" + path}
            }

            yield Message.Directory, "", data
            yield Message.Url, video_url, data
