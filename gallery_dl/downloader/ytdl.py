# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for URLs requiring youtube-dl support"""

from .common import DownloaderBase
from youtube_dl import YoutubeDL
import logging
import os


class Downloader(DownloaderBase):
    scheme = "ytdl"

    def __init__(self, extractor, output):
        DownloaderBase.__init__(self, extractor, output)
        self.ytdl = YoutubeDL({
            "logger": logging.getLogger("ytdl"),
        })

    def download(self, url, pathfmt):
        try:
            info_dict = self.ytdl.extract_info(url[5:], download=False)
        except Exception:
            return False

        if "entries" in info_dict:
            return self._download_playlist(pathfmt, info_dict)
        return self._download_video(pathfmt, info_dict)

    def _download_video(self, pathfmt, info_dict):
        pathfmt.set_extension(info_dict["ext"])
        if pathfmt.exists():
            pathfmt.temppath = ""
            return True
        if self.partdir:
            pathfmt.temppath = os.path.join(
                self.partdir, pathfmt.filename)
        self.ytdl.params["outtmpl"] = pathfmt.temppath.replace("%", "%$")

        self.out.start(pathfmt.path)
        try:
            self.ytdl.process_info(info_dict)
        except Exception:
            return False
        return True

    def _download_playlist(self, pathfmt, info_dict):
        pathfmt.set_extension("%(playlist_index)s.%(ext)s")
        self.ytdl.params["outtmpl"] = pathfmt.realpath

        for entry in info_dict["entries"]:
            self.ytdl.process_info(entry)
        return True
