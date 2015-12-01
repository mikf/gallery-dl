# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for text urls"""

from .common import BasicDownloader

class Downloader(BasicDownloader):

    def __init__(self, *args):
        BasicDownloader.__init__(self)

    def download_impl(self, url, file):
        file.write(bytes(url[7:], "utf-8"))
        return 0
