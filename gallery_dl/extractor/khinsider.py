# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract soundtracks from https://khinsider.com/"""

from .common import AsynchronousExtractor, Message
from .. import text

class KhinsiderSoundtrackExtractor(AsynchronousExtractor):
    """Extractor for soundtracks from khinsider.com"""
    category = "khinsider"
    subcategory = "soundtrack"
    directory_fmt = ["{category}", "{album}"]
    filename_fmt = "{filename}"
    pattern = [r"(?:https?://)?downloads\.khinsider\.com/game-soundtracks/album/(.+)"]

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.album = match.group(1)

    def items(self):
        url = "http://downloads.khinsider.com/game-soundtracks/album/" + self.album
        page = self.request(url, encoding="utf-8").text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for url, track in self.get_album_tracks(page):
            track.update(data)
            yield Message.Url, url, track

    def get_job_metadata(self, page):
        return text.extract_all(page, (
            ("album", "Album name: <b>", "</b>"),
            ("count", "Number of Files: <b>", "</b>"),
            ("size" , "Total Filesize: <b>", "</b>"),
            ("date" , "Date added: <b>", "</b>"),
            ("type" , "Album type: <b>", "</b>"),
        ), values={"category": self.category})[0]

    def get_album_tracks(self, page):
        pos = page.index("Download all songs at once:")
        num = 0
        for url in text.extract_iter(page, '<tr>\r\n\t\t<td><a href="', '"', pos):
            page = self.request(url, encoding="utf-8").text
            name, pos = text.extract(page, "Song name: <b>", "</b>")
            url , pos = text.extract(page, '<p><a style="color: #21363f;" href="', '"', pos)
            num += 1
            yield url, text.nameext_from_url(name, {"num": num})
