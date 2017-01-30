# -*- coding: utf-8 -*-

# Copyright 2014-2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for text:// urls"""

from .common import BasicDownloader


class Downloader(BasicDownloader):

    def __init__(self, output):
        BasicDownloader.__init__(self)
        self.out = output

    def download_impl(self, url, pathfmt):
        if not pathfmt.has_extension:
            pathfmt.set_extension("txt")
            if pathfmt.exists():
                self.out.skip(pathfmt.path)
                return

        self.out.start(pathfmt.path)
        self.downloading = True
        with pathfmt.open() as file:
            file.write(bytes(url[7:], "utf-8"))
        self.downloading = False
        self.out.success(pathfmt.path, 0)
