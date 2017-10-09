# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract soundtracks from https://downloads.khinsider.com/"""

from .common import AsynchronousExtractor, Message
from .. import text, exception


class KhinsiderSoundtrackExtractor(AsynchronousExtractor):
    """Extractor for soundtracks from khinsider.com"""
    category = "khinsider"
    subcategory = "soundtrack"
    directory_fmt = ["{category}", "{album}"]
    pattern = [r"(?:https?://)?downloads\.khinsider\.com/"
               r"game-soundtracks/album/([^/?&#]+)"]
    test = [(("http://downloads.khinsider.com/game-soundtracks/"
              "album/horizon-riders-wii-"), {
        "pattern": ("https?://\d+\.\d+\.\d+\.\d+/ost/horizon-riders-wii-/"
                    "[^/]+/horizon-riders-wii-full-soundtrack\.mp3"),
        "keyword": "d91cf3edee6713b536eaf3995743f0be7dc72f68",
    })]

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.album = match.group(1)

    def items(self):
        url = ("https://downloads.khinsider.com/game-soundtracks/album/" +
               self.album)
        page = self.request(url, encoding="utf-8").text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for url, track in self.get_album_tracks(page):
            track.update(data)
            yield Message.Url, url, track

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = text.extract_all(page, (
            ("album", "Album name: <b>", "</b>"),
            ("count", "Number of Files: <b>", "</b>"),
            ("size" , "Total Filesize: <b>", "</b>"),
            ("date" , "Date added: <b>", "</b>"),
            ("type" , "Album type: <b>", "</b>"),
        ))[0]
        data["album"] = text.unescape(data["album"])
        return data

    def get_album_tracks(self, page):
        """Collect url and metadata for all tracks of a soundtrack"""
        pos = page.find("Download all songs at once:")
        if pos == -1:
            raise exception.NotFoundError("soundtrack")
        num = 0
        for url in text.extract_iter(
                page, '<tr>\r\n\r\n\t \t<td><a href="', '"', pos):
            page = self.request(url, encoding="utf-8").text
            name, pos = text.extract(page, "Song name: <b>", "</b>")
            url , pos = text.extract(
                page, '<p><a style="color: #21363f;" href="', '"', pos
            )
            num += 1
            yield url, text.nameext_from_url(name, {"num": num})
