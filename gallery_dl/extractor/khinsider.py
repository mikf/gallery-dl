# -*- coding: utf-8 -*-

# Copyright 2016-2018 Mike Fährmann
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
    archive_fmt = "{album}_{name}.{extension}"
    pattern = [r"(?:https?://)?downloads\.khinsider\.com/"
               r"game-soundtracks/album/([^/?&#]+)"]
    test = [(("https://downloads.khinsider.com/game-soundtracks/"
              "album/horizon-riders-wii"), {
        "pattern": (r"https?://\d+\.\d+\.\d+\.\d+/ost/horizon-riders-wii/[^/]+"
                    r"/Horizon%20Riders%20Wii%20-%20Full%20Soundtrack\.mp3"),
        "count": 1,
        "keyword": "d91cf3edee6713b536eaf3995743f0be7dc72f68",
    })]
    root = "https://downloads.khinsider.com"

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.album = match.group(1)

    def items(self):
        url = (self.root + "/game-soundtracks/album/" + self.album)
        page = self.request(url, encoding="utf-8").text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for url, track in self.get_album_tracks(page):
            track.update(data)
            yield Message.Url, url, track

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        if "Download all songs at once:" not in page:
            raise exception.NotFoundError("soundtrack")
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
        page = text.extract(page, '<table id="songlist">', '</table>')[0]
        for num, url in enumerate(text.extract_iter(
                page, '<td class="clickable-row"><a href="', '"'), 1):
            url = text.urljoin(self.root, url)
            page = self.request(url, encoding="utf-8").text
            url = text.extract(
                page, '<p><a style="color: #21363f;" href="', '"')[0]
            yield url, text.nameext_from_url(url, {"num": num})
