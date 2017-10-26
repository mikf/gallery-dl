# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for text: URLs"""

from .common import DownloaderBase


class Downloader(DownloaderBase):
    scheme = "text"

    def __init__(self, session, output):
        DownloaderBase.__init__(self, session, output)
        self.content = b""

    def connect(self, url, offset):
        data = url.encode()
        self.content = data[offset + 5:]
        return offset, len(data) - 5

    def receive(self, file):
        file.write(self.content)

    def reset(self):
        self.content = b""

    @staticmethod
    def get_extension():
        return "txt"
