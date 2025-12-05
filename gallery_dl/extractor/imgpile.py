# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://imgpile.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?imgpile\.com"


class ImgpileExtractor(Extractor):
    """Base class for imgpile extractors"""
    category = "imgpile"
    root = "https://imgpile.com"
    directory_fmt = ("{category}", "{post[author]}",
                     "{post[title]} ({post[id_slug]})")
    archive_fmt = "{post[id_slug]}_{id}"

    def items(self):
        pass


class ImgpilePostExtractor(ImgpileExtractor):
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/p/(\w+)"
    example = "https://imgpile.com/p/AbCdEfG"

    def items(self):
        post_id = self.groups[0]
        url = f"{self.root}/p/{post_id}"
        page = self.request(url).text
        extr = text.extract_from(page)

        post = {
            "id_slug": post_id,
            "title"  : text.unescape(extr("<title>", " - imgpile<")),
            "id"     : text.parse_int(extr('data-post-id="', '"')),
            "author" : extr('/u/', '"'),
            "score"  : text.parse_int(text.remove_html(extr(
                'class="post-score">', "</"))),
            "views"  : text.parse_int(extr(
                'class="meta-value">', "<").replace(",", "")),
            "tags"   : text.split_html(extr(
                " <!-- Tags -->", '<!-- "')),
        }

        files = self._extract_files(extr)
        data = {"post": post}
        data["count"] = post["count"] = len(files)

        yield Message.Directory, "", data
        for data["num"], file in enumerate(files, 1):
            data.update(file)
            url = file["url"]
            yield Message.Url, url, text.nameext_from_url(url, data)

    def _extract_files(self, extr):
        files = []

        while True:
            media = extr('lass="post-media', '</div>')
            if not media:
                break
            files.append({
                "id_slug": text.extr(media, 'data-id="', '"'),
                "id" : text.parse_int(text.extr(
                    media, 'data-media-id="', '"')),
                "url": f"""http{text.extr(media, '<a href="http', '"')}""",
            })
        return files


class ImgpileUserExtractor(ImgpileExtractor):
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}/u/([^/?#]+)"
    example = "https://imgpile.com/u/USER"

    def items(self):
        url = f"{self.root}/api/v1/posts"
        params = {
            "limit"     : "100",
            "sort"      : "latest",
            "period"    : "all",
            "visibility": "public",
            #  "moderation_status": "approved",
            "username"  : self.groups[0],
        }
        headers = {
            "Accept"        : "application/json",
            #  "Referer"       : "https://imgpile.com/u/USER",
            "Content-Type"  : "application/json",
            #  "X-CSRF-TOKEN": "",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        base = f"{self.root}/p/"
        while True:
            data = self.request_json(url, params=params, headers=headers)

            if params is not None:
                params = None
                self.kwdict["total"] = data["meta"]["total"]

            for item in data["data"]:
                item["_extractor"] = ImgpilePostExtractor
                url = f"{base}{item['slug']}"
                yield Message.Queue, url, item

            url = data["links"].get("next")
            if not url:
                return
