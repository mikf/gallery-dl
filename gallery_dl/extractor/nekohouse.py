# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nekohouse.su/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?nekohouse\.su"
USER_PATTERN = BASE_PATTERN + r"/([^/?#]+)/user/([^/?#]+)"


class NekohouseExtractor(Extractor):
    """Base class for nekohouse extractors"""
    category = "nekohouse"
    root = "https://nekohouse.su"


class NekohousePostExtractor(NekohouseExtractor):
    subcategory = "post"
    directory_fmt = ("{category}", "{service}", "{username} ({user_id})",
                     "{post_id} {date} {title[b:230]}")
    filename_fmt = "{num:>02} {id|filename}.{extension}"
    archive_fmt = "{service}_{user_id}_{post_id}_{hash}"
    pattern = USER_PATTERN + r"/post/([^/?#]+)"
    example = "https://nekohouse.su/SERVICE/user/12345/post/12345"

    def items(self):
        service, user_id, post_id = self.groups
        url = "{}/{}/user/{}/post/{}".format(
            self.root, service, user_id, post_id)
        html = self.request(url).text

        files = self._extract_files(html)
        post = self._extract_post(html)
        post["service"] = service
        post["user_id"] = user_id
        post["post_id"] = post_id
        post["count"] = len(files)

        yield Message.Directory, post
        for post["num"], file in enumerate(files, 1):
            url = file["url"]
            text.nameext_from_url(url, file)
            file["hash"] = file["filename"]
            file.update(post)
            if "name" in file:
                text.nameext_from_url(file.pop("name"), file)
            yield Message.Url, url, file

    def _extract_post(self, html):
        extr = text.extract_from(html)
        return {
            "username": text.unescape(extr(
                'class="scrape__user-name', '</').rpartition(">")[2].strip()),
            "title"   : text.unescape(extr(
                'class="scrape__title', '</').rpartition(">")[2]),
            "date"   : text.parse_datetime(extr(
                'datetime="', '"')[:19], "%Y-%m-%d %H:%M:%S"),
            "content": text.unescape(extr(
                'class="scrape__content">', "</div>").strip()),
        }

    def _extract_files(self, html):
        files = []

        extr = text.extract_from(text.extr(
            html, 'class="scrape__files"', "<footer"))
        while True:
            file_id = extr('<a href="/post/', '"')
            if not file_id:
                break
            files.append({
                "id"  : file_id,
                "url" : self.root + extr('href="', '"'),
                "type": "file",
            })

        extr = text.extract_from(text.extr(
            html, 'class="scrape__attachments"', "</ul>"))
        while True:
            url = extr('href="', '"')
            if not url:
                break
            files.append({
                "id"  : "",
                "url" : self.root + url,
                "name": text.unescape(extr('download="', '"')),
                "type": "attachment",
            })

        return files


class NekohouseUserExtractor(NekohouseExtractor):
    subcategory = "user"
    pattern = USER_PATTERN + r"/?(?:\?([^#]+))?(?:$|\?|#)"
    example = "https://nekohouse.su/SERVICE/user/12345"

    def items(self):
        service, user_id, _ = self.groups
        creator_url = "{}/{}/user/{}".format(self.root, service, user_id)
        params = {"o": 0}

        data = {"_extractor": NekohousePostExtractor}
        while True:
            html = self.request(creator_url, params=params).text

            cnt = 0
            for post in text.extract_iter(html, "<article", "</article>"):
                cnt += 1
                post_url = self.root + text.extr(post, '<a href="', '"')
                yield Message.Queue, post_url, data

            if cnt < 50:
                return
            params["o"] += 50
