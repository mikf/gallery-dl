# -*- coding: utf-8 -*-

# Copyright 2014-2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by downloader modules."""

import os


class BasicDownloader():
    """Base class for downloader modules"""

    max_tries = 5

    def __init__(self):
        self.downloading = False

    def download(self, url, pathfmt):
        """Download the resource at 'url' and write it to a file-like object"""
        try:
            return self.download_impl(url, pathfmt)
        except:
            # remove file if download failed
            try:
                if self.downloading:
                    os.unlink(pathfmt.realpath)
            except (AttributeError, FileNotFoundError):
                pass
            raise

    def download_impl(self, url, file_handle):
        """Actual implementaion of the download process"""
        pass
