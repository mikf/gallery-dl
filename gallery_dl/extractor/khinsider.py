# -*- coding: utf-8 -*-

# Copyright 2016-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://downloads.khinsider.com/"""

from .common import Extractor, Message, AsynchronousMixin
from .. import text, exception


class KhinsiderSoundtrackExtractor(AsynchronousMixin, Extractor):
    """Extractor for soundtracks from khinsider.com"""
    category = "khinsider"
    subcategory = "soundtrack"
    root = "https://downloads.khinsider.com"
    directory_fmt = ("{category}", "{album[name]}")
    archive_fmt = "{filename}.{extension}"
    pattern = (r"(?:https?://)?downloads\.khinsider\.com"
               r"/game-soundtracks/album/([^/?#]+)")
    example = ("https://downloads.khinsider.com"
               "/game-soundtracks/album/TITLE")

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.album = match.group(1)

    def items(self):
        url = self.root + "/game-soundtracks/album/" + self.album
        page = self.request(url, encoding="utf-8").text
        if "Download all songs at once:" not in page:
            raise exception.NotFoundError("soundtrack")

        data = self.metadata(page)
        yield Message.Directory, data
        for track in self.tracks(page):
            track.update(data)
            yield Message.Url, track["url"], track

    def metadata(self, page):
        extr = text.extract_from(page)
        return {"album": {
            "name" : text.unescape(extr("<h2>", "<")),
            "platform": extr("Platforms: <a", "<").rpartition(">")[2],
            "count": text.parse_int(extr("Number of Files: <b>", "<")),
            "size" : text.parse_bytes(extr("Total Filesize: <b>", "<")[:-1]),
            "date" : extr("Date Added: <b>", "<"),
            "type" : text.remove_html(extr("Album type: <b>", "</b>")),
        }}

    def tracks(self, page):
        fmt = self.config("format", ("mp3",))
        if fmt and isinstance(fmt, str):
            if fmt == "all":
                fmt = None
            else:
                fmt = fmt.lower().split(",")

        page = text.extr(page, '<table id="songlist">', '</table>')
        for num, url in enumerate(text.extract_iter(
                page, '<td class="clickable-row"><a href="', '"'), 1):
            url = text.urljoin(self.root, url)
            page = self.request(url, encoding="utf-8").text
            track = first = None

            for url in text.extract_iter(page, '<p><a href="', '"'):
                track = text.nameext_from_url(url, {"num": num, "url": url})
                if first is None:
                    first = track
                if not fmt or track["extension"] in fmt:
                    first = False
                    yield track
            if first:
                yield first
