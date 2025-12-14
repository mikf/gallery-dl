# -*- coding: utf-8 -*-

# Copyright 2024-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://motherless.com/"""

from .common import Extractor, Message
from .. import text, dt, exception
from ..cache import memcache

BASE_PATTERN = r"(?:https?://)?motherless\.com"


class MotherlessExtractor(Extractor):
    """Base class for motherless extractors"""
    category = "motherless"
    root = "https://motherless.com"
    filename_fmt = "{id} {title}.{extension}"
    archive_fmt = "{id}"

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)

        content = response.content
        if (b'<div class="error-page' in content or
                b">The page you're looking for cannot be found.<" in content):
            raise exception.NotFoundError("page")

        self.request = Extractor.request.__get__(self)
        return response

    def _extract_media(self, path):
        url = f"{self.root}/{path}"
        page = self.request(url).text
        extr = text.extract_from(page)

        path, _, media_id = path.rpartition("/")
        data = {
            "id"   : media_id,
            "title": text.unescape(
                (t := extr("<title>", "<")) and t[:t.rfind(" | ")]),
            "type" : extr("__mediatype = '", "'"),
            "group": extr("__group = '", "'"),
            "url"  : extr("__fileurl = '", "'"),
            "tags" : [
                text.unescape(tag)
                for tag in text.extract_iter(
                    extr('class="media-meta-tags">', "</div>"), ">#", "<")
            ],
            "views": text.parse_int(extr(
                'class="count">', " ").replace(",", "")),
            "favorites": text.parse_int(extr(
                'class="count">', " ").replace(",", "")),
            "date" : self._parse_datetime(extr('class="count">', "<")),
            "uploader": text.unescape(extr('class="username">', "<").strip()),
        }

        if not path:
            pass
        elif path[0] == "G":
            data["gallery_id"] = path[1:]
            data["gallery_title"] = self._extract_gallery_title(
                page, data["gallery_id"])
        elif path[0] == "g":
            data["group_id"] = path[2:]
            data["group_title"] = self._extract_group_title(
                page, data["group_id"])

        return data

    def _pagination(self, page):
        while True:
            for thumb in text.extract_iter(
                    page, 'class="thumb-container', "</div>"):
                yield thumb

            url = text.extr(page, '<link rel="next" href="', '"')
            if not url:
                return
            page = self.request(text.unescape(url)).text

    def _extract_data(self, page, category):
        extr = text.extract_from(page)

        gid = self.groups[-1]
        if category == "gallery":
            title = self._extract_gallery_title(page, gid)
        else:
            title = self._extract_group_title(page, gid)

        return {
            f"{category}_id": gid,
            f"{category}_title": title,
            "uploader": text.remove_html(extr(
                f'class="{category}-member-username">', "</")),
            "count": text.parse_int(
                extr('<span class="active">', ")")
                .rpartition("(")[2].replace(",", "")),
        }

    def _parse_thumb_data(self, thumb):
        extr = text.extract_from(thumb)

        data = {
            "id"       : extr('data-codename="', '"'),
            "type"     : extr('data-mediatype="', '"'),
            "thumbnail": extr('class="static" src="', '"'),
            "title"    : extr(' alt="', '"'),
        }
        data["url"] = data["thumbnail"].replace("thumb", data["type"])

        return data

    def _parse_datetime(self, dt_string):
        if " ago" not in dt_string:
            return dt.parse(dt_string, "%d  %b  %Y")

        value = text.parse_int(dt_string[:-5])
        delta = (dt.timedelta(0, value*3600) if dt_string[-5] == "h" else
                 dt.timedelta(value))
        return (dt.now() - delta).replace(hour=0, minute=0, second=0)

    @memcache(keyarg=2)
    def _extract_gallery_title(self, page, gallery_id):
        title = text.extr(
            text.extr(page, '<h1 class="content-title">', "</h1>"),
            "From the gallery:", "<")
        if title:
            return text.unescape(title.strip())

        if f' href="/G{gallery_id}"' in page:
            return text.unescape(
                (t := text.extr(page, "<title>", "<")) and t[:t.rfind(" | ")])

        return ""

    @memcache(keyarg=2)
    def _extract_group_title(self, page, group_id):
        title = text.extr(
            text.extr(page, '<h1 class="group-bio-name">', "</h1>"),
            ">", "<")
        if title:
            return text.unescape(title.strip())

        return ""


class MotherlessMediaExtractor(MotherlessExtractor):
    """Extractor for a single image/video from motherless.com"""
    subcategory = "media"
    pattern = (rf"{BASE_PATTERN}/("
               rf"(?:g/[^/?#]+/|G[IV]?[A-Z0-9]+/)?"
               rf"(?!G)[A-Z0-9]+)")
    example = "https://motherless.com/ABC123"

    def items(self):
        file = self._extract_media(self.groups[0])
        url = file["url"]
        yield Message.Directory, "", file
        yield Message.Url, url, text.nameext_from_url(url, file)


class MotherlessGalleryExtractor(MotherlessExtractor):
    """Extractor for a motherless.com gallery"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{uploader}",
                     "{gallery_id} {gallery_title}")
    archive_fmt = "{gallery_id}_{id}"
    pattern = rf"{BASE_PATTERN}/G([IVG])?([A-Z0-9]+)/?$"
    example = "https://motherless.com/GABC123"

    def items(self):
        type, gid = self.groups

        if not type:
            data = {"_extractor": MotherlessGalleryExtractor}
            yield Message.Queue, f"{self.root}/GI{gid}", data
            yield Message.Queue, f"{self.root}/GV{gid}", data
            return

        url = f"{self.root}/G{type}{gid}"
        page = self.request(url).text
        data = self._extract_data(page, "gallery")

        for num, thumb in enumerate(self._pagination(page), 1):
            file = self._parse_thumb_data(thumb)
            thumbnail = file["thumbnail"]

            if file["type"] == "video":
                file = self._extract_media(file["id"])

            file.update(data)
            file["num"] = num
            file["thumbnail"] = thumbnail
            url = file["url"]
            yield Message.Directory, "", file
            yield Message.Url, url, text.nameext_from_url(url, file)


class MotherlessGroupExtractor(MotherlessExtractor):
    subcategory = "group"
    directory_fmt = ("{category}", "{uploader}",
                     "{group_id} {group_title}")
    archive_fmt = "{group_id}_{id}"
    pattern = rf"{BASE_PATTERN}/g([iv]?)/?([a-z0-9_]+)/?$"
    example = "https://motherless.com/g/abc123"

    def items(self):
        type, gid = self.groups

        if not type:
            data = {"_extractor": MotherlessGroupExtractor}
            yield Message.Queue, f"{self.root}/gi/{gid}", data
            yield Message.Queue, f"{self.root}/gv/{gid}", data
            return

        url = f"{self.root}/g{type}/{gid}"
        page = self.request(url).text
        data = self._extract_data(page, "group")

        for num, thumb in enumerate(self._pagination(page), 1):
            file = self._parse_thumb_data(thumb)
            thumbnail = file["thumbnail"]

            file = self._extract_media(file["id"])

            uploader = file.get("uploader")
            file.update(data)
            file["num"] = num
            file["thumbnail"] = thumbnail
            file["uploader"] = uploader
            file["group"] = file["group_id"]
            url = file["url"]
            yield Message.Directory, "", file
            yield Message.Url, url, text.nameext_from_url(url, file)
