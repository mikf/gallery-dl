# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for text: URLs"""

from .common import DownloaderBase


class Downloader(DownloaderBase):
    mode = "t"

    def __init__(self, session, output):
        DownloaderBase.__init__(self, session, output)
        self.text = ""

    def connect(self, url, offset):
        self.text = url[offset + 5:]
        return offset, len(url) - 5

    def receive(self, file):
        file.write(self.text)

    def reset(self):
        self.text = ""

    @staticmethod
    def get_extension():
        return "txt"
