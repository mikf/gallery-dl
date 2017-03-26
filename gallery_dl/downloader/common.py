# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by downloader modules."""

import os


class BasicDownloader():
    """Base class for downloader modules"""
    def __init__(self):
        self.downloading = False

    def download(self, url, pathfmt):
        """Download the resource at 'url' and write it to a file-like object"""
        try:
            self.download_impl(url, pathfmt)
        finally:
            # remove file from incomplete downloads
            if self.downloading:
                try:
                    os.remove(pathfmt.realpath)
                except (OSError, AttributeError):
                    pass

    def download_impl(self, url, pathfmt):
        """Actual implementaion of the download process"""
