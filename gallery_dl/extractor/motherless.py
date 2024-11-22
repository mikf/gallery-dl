# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://motherless.com/"""

from .common import Extractor, Message
from .. import text, util
from ..cache import memcache
from datetime import timedelta

BASE_PATTERN = r"(?:https?://)?motherless\.com"


class MotherlessExtractor(Extractor):
    """Base class for motherless extractors"""
    category = "motherless"
    root = "https://motherless.com"
    filename_fmt = "{id} {title}.{extension}"
    archive_fmt = "{id}"


class MotherlessMediaExtractor(MotherlessExtractor):
    """Extractor for a single image/video from motherless.com"""
    subcategory = "media"
    pattern = (BASE_PATTERN +
               r"/((?:g/[^/?#]+/|G[IV]?[A-Z0-9]+/)?"
               r"(?!G)[A-Z0-9]+)")
    example = "https://motherless.com/ABC123"

    def items(self):
        file = self._extract_media(self.groups[0])
        url = file["url"]
        yield Message.Directory, file
        yield Message.Url, url, text.nameext_from_url(url, file)

    def _extract_media(self, path):
        url = self.root + "/" + path
        page = self.request(url).text
        extr = text.extract_from(page)

        path, _, media_id = path.rpartition("/")
        data = {
            "id"   : media_id,
            "type" : extr("__mediatype = '", "'"),
            "group": extr("__group = '", "'"),
            "url"  : extr("__fileurl = '", "'"),
            "tags" : [
                text.unescape(tag)
                for tag in text.extract_iter(
                    extr('class="media-meta-tags">', "</div>"), ">#", "<")
            ],
            "title": text.unescape(extr("<h1>", "<")),
            "views": text.parse_int(extr(
                'class="count">', " ").replace(",", "")),
            "favorites": text.parse_int(extr(
                'class="count">', " ").replace(",", "")),
            "date" : self._parse_datetime(extr('class="count">', "<")),
            "uploader": text.unescape(extr('class="username">', "<").strip()),
        }

        if path and path[0] == "G":
            data["gallery_id"] = path[1:]
            data["gallery_title"] = self._extract_gallery_title(
                page, data["gallery_id"])

        return data

    def _parse_datetime(self, dt):
        if " ago" not in dt:
            return text.parse_datetime(dt, "%d  %b  %Y")

        value = text.parse_int(dt[:-5])
        delta = timedelta(0, value*3600) if dt[-5] == "h" else timedelta(value)
        return (util.datetime_utcnow() - delta).replace(
            hour=0, minute=0, second=0)

    @memcache(keyarg=2)
    def _extract_gallery_title(self, page, gallery_id):
        title = text.extr(
            text.extr(page, '<h1 class="content-title">', "</h1>"),
            "From the gallery:", "<")
        if title:
            return text.unescape(title.strip())

        pos = page.find(' href="/G' + gallery_id + '"')
        if pos >= 0:
            return text.unescape(text.extract(
                page, ' title="', '"', pos)[0])

        return ""


class MotherlessGalleryExtractor(MotherlessExtractor):
    """Extractor for a motherless.com gallery"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{uploader}",
                     "{gallery_id} {gallery_title}")
    archive_fmt = "{gallery_id}_{id}"
    pattern = BASE_PATTERN + "/G([IVG])?([A-Z0-9]+)/?$"
    example = "https://motherless.com/GABC123"

    def items(self):
        type, gid = self.groups

        if not type:
            data = {"_extractor": MotherlessGalleryExtractor}
            yield Message.Queue, self.root + "/GI" + gid, data
            yield Message.Queue, self.root + "/GV" + gid, data
            return

        url = "{}/G{}{}".format(self.root, type, gid)
        page = self.request(url).text
        data = self._extract_gallery_data(page)

        for num, thumb in enumerate(self._pagination(page), 1):
            file = self._parse_thumb_data(thumb)
            file.update(data)
            file["num"] = num
            url = file["url"]
            yield Message.Directory, file
            yield Message.Url, url, text.nameext_from_url(url, file)

    def _pagination(self, page):
        while True:
            for thumb in text.extract_iter(
                    page, 'class="thumb-container', "</div>"):
                yield thumb

            url = text.extr(page, '<link rel="next" href="', '"')
            if not url:
                return
            page = self.request(text.unescape(url)).text

    def _extract_gallery_data(self, page):
        extr = text.extract_from(page)
        return {
            "gallery_id": self.groups[-1],
            "gallery_title": text.unescape(extr(
                "<title>", "<").rpartition(" | ")[0]),
            "uploader": text.remove_html(extr(
                'class="gallery-member-username">', "</")),
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

        type = data["type"]
        url = data["thumbnail"].replace("thumb", type)
        if type == "video":
            url = "{}/{}.mp4".format(url.rpartition("/")[0], data["id"])
        data["url"] = url

        return data
