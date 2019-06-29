# -*- coding: utf-8 -*-

# Copyright 2014-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for text: URLs"""

from .common import DownloaderBase


class TextDownloader(DownloaderBase):
    scheme = "text"

    def download(self, url, pathfmt):
        if self.part:
            pathfmt.part_enable(self.partdir)
        self.out.start(pathfmt.path)
        with pathfmt.open("wb") as file:
            file.write(url.encode()[5:])
        return True


__downloader__ = TextDownloader
